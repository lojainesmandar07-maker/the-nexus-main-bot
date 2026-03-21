import discord
from discord import app_commands
from discord.ext import commands, tasks
from core.bot import StoryBot
import aiosqlite
import datetime
import json
import os
from ui.embeds import EmbedBuilder

DB_PATH = "data/nexus.db"

def load_decisions():
    try:
        with open("data/decisions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading decisions.json: {e}")
        return []

async def init_social_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS friend_challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenger_id INTEGER,
                target_user_id INTEGER,
                story_id INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS collective_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                options_json TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP,
                source_id TEXT UNIQUE
            )
        """)
        # Just in case the table already exists from previous runs, we can try to add the column
        try:
            await db.execute("ALTER TABLE collective_decisions ADD COLUMN source_id TEXT UNIQUE")
            await db.commit()
        except Exception:
            pass # Column already exists
        await db.execute("""
            CREATE TABLE IF NOT EXISTS decision_votes (
                decision_id INTEGER,
                user_id INTEGER,
                option_index INTEGER,
                PRIMARY KEY (decision_id, user_id),
                FOREIGN KEY (decision_id) REFERENCES collective_decisions(id)
            )
        """)
        await db.commit()

class SocialCog(commands.Cog):
    def __init__(self, bot: StoryBot):
        self.bot = bot
        self.bot.loop.create_task(init_social_db())
        self.check_decisions_loop.start()
        self.auto_decision_loop.start()

    def cog_unload(self):
        self.check_decisions_loop.cancel()
        self.auto_decision_loop.cancel()

    @tasks.loop(hours=24.0)
    async def check_decisions_loop(self):
        """Auto announce decision results if they should be closed (e.g. after a week)."""
        # For simplicity, if we wanted auto-close we could do it here.
        # The prompt says 'Auto result announce' so we could assume
        # active decisions automatically close after 7 days.
        now = datetime.datetime.utcnow()
        week_ago = now - datetime.timedelta(days=7)

        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("""
                SELECT id, title, options_json
                FROM collective_decisions
                WHERE is_active = 1 AND created_at <= ?
            """, (week_ago,))
            expired_decisions = await cursor.fetchall()

            for d_id, title, options_json in expired_decisions:
                # Close it
                await db.execute("UPDATE collective_decisions SET is_active = 0, closed_at = ? WHERE id = ?", (now, d_id))
                await db.commit()

                # Fetch results to announce
                options = json.loads(options_json)
                v_cursor = await db.execute("SELECT option_index, COUNT(*) FROM decision_votes WHERE decision_id = ? GROUP BY option_index", (d_id,))
                votes_data = await v_cursor.fetchall()

                # Announce to a specific channel (or global notification if possible).
                # To keep it simple, we could post to 'endings_channel' or similar config.
                from core.config import get_config
                world_channels = get_config("world_channels", {})
                ch_id = world_channels.get("endings_channel") or get_config("test_channel")

                if ch_id:
                    channel = self.bot.get_channel(int(ch_id))
                    if channel:
                        total_votes = sum(count for _, count in votes_data)
                        vote_counts = {i: 0 for i in range(len(options))}
                        for opt_idx, count in votes_data:
                            vote_counts[opt_idx] = count

                        results_text = f"**إجمالي الأصوات:** {total_votes}\n\n"
                        sorted_opts = sorted(vote_counts.items(), key=lambda x: x[1], reverse=True)
                        for idx, count in sorted_opts:
                            percent = int((count / total_votes) * 100) if total_votes > 0 else 0
                            bar = "█" * (percent // 10) + "░" * (10 - (percent // 10))
                            results_text += f"**{options[idx]}**\n{bar} {percent}% ({count} أصوات)\n\n"

                        embed = discord.Embed(
                            title=f"⚖️ نتيجة قرار الأسبوع: {title}",
                            description=f"لقد قرر النيكسوس وتحدث المجتمع!\n\n{results_text}",
                            color=discord.Color.gold()
                        )
                        await channel.send(embed=embed)

    @check_decisions_loop.before_loop
    async def before_check_decisions(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=24.0)
    async def auto_decision_loop(self):
        """Check if an active decision exists, if not, create one from JSON."""
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("SELECT id FROM collective_decisions WHERE is_active = 1")
            active = await cursor.fetchone()
            if active:
                return # Already have an active decision

            # No active decision, try to find an unused one from JSON
            decisions_data = load_decisions()
            if not decisions_data:
                return

            for dec in decisions_data:
                d_id = dec.get("id")
                cursor = await db.execute("SELECT id FROM collective_decisions WHERE source_id = ?", (d_id,))
                if not await cursor.fetchone():
                    # This decision hasn't been used yet
                    options_json = json.dumps(dec.get("options", []), ensure_ascii=False)
                    await db.execute("""
                        INSERT INTO collective_decisions (title, description, options_json, source_id)
                        VALUES (?, ?, ?, ?)
                    """, (dec.get("title"), dec.get("description"), options_json, d_id))
                    await db.commit()

                    # Announce it
                    from core.config import get_config
                    world_channels = get_config("world_channels", {})
                    target_channel_id = world_channels.get("general_channel") or world_channels.get("test_channel")
                    if target_channel_id:
                        channel = self.bot.get_channel(int(target_channel_id))
                        if channel:
                            embed = discord.Embed(
                                title=f"⚖️ قرار جماعي جديد: {dec.get('title')}",
                                description=f"{dec.get('description')}\n\nحدد مصير النيكسوس من خلال التصويت!",
                                color=discord.Color.purple()
                            )
                            embed.set_footer(text="استخدم /قرار_الأسبوع للتفاصيل والمشاركة")
                            await channel.send(embed=embed)
                    break # Only spawn one at a time

    @auto_decision_loop.before_loop
    async def before_auto_decision_loop(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="تحدي_صديق", description="تحدى صديقاً للعب قصة معينة ومقارنة النهايات!")
    @app_commands.describe(friend="الصديق الذي تود تحديه", story_id="رقم القصة")
    async def challenge_friend(self, interaction: discord.Interaction, friend: discord.Member, story_id: int):
        try:
            if friend.bot:
                await interaction.response.send_message("❌ لا يمكنك تحدي البوتات!", ephemeral=True)
                return

            if friend.id == interaction.user.id:
                await interaction.response.send_message("❌ لا يمكنك تحدي نفسك!", ephemeral=True)
                return

            story = self.bot.story_manager.get_story(story_id)
            if not story:
                await interaction.response.send_message("❌ رقم القصة غير صحيح.", ephemeral=True)
                return

            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute("""
                    INSERT INTO friend_challenges (challenger_id, target_user_id, story_id)
                    VALUES (?, ?, ?)
                """, (interaction.user.id, friend.id, story_id))
                await db.commit()

            embed = discord.Embed(
                title="⚔️ تحدي جديد!",
                description=f"لقد تحداك <@{interaction.user.id}> لتلعب القصة **{story.title}**!\n\nهل ستتمكن من اكتشاف نهايات أفضل؟ استخدم `/لعب_فردي story_id:{story_id}` للبدء!",
                color=discord.Color.brand_red()
            )
            embed.set_thumbnail(url=interaction.user.display_avatar.url)

            try:
                await friend.send(embed=embed)
                await interaction.response.send_message(f"✅ تم إرسال التحدي إلى {friend.display_name} بنجاح!", ephemeral=True)
            except discord.Forbidden:
                # Fallback to posting in the channel if DMs are closed
                await interaction.response.send_message(f"<@{friend.id}>", embed=embed)
        except Exception as e:
            print(f"Error in challenge_friend: {e}")
            await interaction.response.send_message("⚠️ حدث خطأ أثناء تنفيذ الأمر.", ephemeral=True)

    @app_commands.command(name="إنشاء_قرار", description="إنشاء قرار أسبوعي جماعي (للإدارة فقط)")
    @app_commands.describe(
        title="عنوان القرار",
        description="وصف وموقف القرار",
        options_comma_separated="الخيارات المتاحة مفصولة بفاصلة (,)"
    )
    @app_commands.default_permissions(manage_guild=True)
    async def create_decision(self, interaction: discord.Interaction, title: str, description: str, options_comma_separated: str):
        try:
            if not interaction.user.guild_permissions.manage_guild:
                await interaction.response.send_message("❌ هذا الأمر مخصص للإدارة فقط.", ephemeral=True)
                return

            options = [opt.strip() for opt in options_comma_separated.split(",") if opt.strip()]
            if len(options) < 2:
                await interaction.response.send_message("❌ يجب تقديم خيارين على الأقل.", ephemeral=True)
                return

            options_json = json.dumps(options, ensure_ascii=False)

            async with aiosqlite.connect(DB_PATH) as db:
                # Only 1 active decision at a time usually
                await db.execute("UPDATE collective_decisions SET is_active = 0 WHERE is_active = 1")

                await db.execute("""
                    INSERT INTO collective_decisions (title, description, options_json)
                    VALUES (?, ?, ?)
                """, (title, description, options_json))
                await db.commit()

            await interaction.response.send_message(f"✅ تم إنشاء القرار الجماعي الأسبوعي: **{title}**", ephemeral=True)
        except Exception as e:
            print(f"Error in create_decision: {e}")
            await interaction.response.send_message("⚠️ حدث خطأ أثناء تنفيذ الأمر.", ephemeral=True)

    @app_commands.command(name="قرار_الأسبوع", description="شارك بصوتك في القرار الجماعي الأسبوعي للنيكسوس")
    async def weekly_decision(self, interaction: discord.Interaction):
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                row = await db.execute("SELECT id, title, description, options_json FROM collective_decisions WHERE is_active = 1 ORDER BY created_at DESC LIMIT 1")
                decision = await row.fetchone()

            if not decision:
                await interaction.response.send_message("❌ لا يوجد قرار جماعي نشط حالياً.", ephemeral=True)
                return

            d_id, title, desc, options_json = decision
            options = json.loads(options_json)

            embed = discord.Embed(
                title=f"⚖️ قرار الأسبوع: {title}",
                description=f"{desc}\n\nحدد مصير النيكسوس من خلال التصويت أدناه!",
                color=discord.Color.purple()
            )
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1234567890/1234567890/scales.png") # Placeholder
            embed.set_footer(text="سيتم إعلان النتيجة نهاية الأسبوع.")

            view = DecisionVoteView(d_id, options)
            await interaction.response.send_message(embed=embed, view=view)
        except Exception as e:
            print(f"Error in weekly_decision: {e}")
            await interaction.response.send_message("⚠️ حدث خطأ أثناء تنفيذ الأمر.", ephemeral=True)

    @app_commands.command(name="ذاكرة_النيكسوس", description="استعرض القرارات الجماعية السابقة ونتائجها")
    async def nexus_memory(self, interaction: discord.Interaction):
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute("SELECT id, title, options_json FROM collective_decisions WHERE is_active = 0 ORDER BY closed_at DESC LIMIT 5")
                past_decisions = await cursor.fetchall()

            if not past_decisions:
                await interaction.response.send_message("❌ لم يتم اتخاذ أي قرارات جماعية سابقة حتى الآن.", ephemeral=True)
                return

            embed = discord.Embed(
                title="📜 ذاكرة النيكسوس",
                description="القرارات الجماعية التي شكلت مصير عالمنا:",
                color=discord.Color.dark_theme()
            )

            for d_id, title, options_json in past_decisions:
                options = json.loads(options_json)
                # Find winning option
                async with aiosqlite.connect(DB_PATH) as db:
                    v_cursor = await db.execute("SELECT option_index, COUNT(*) as c FROM decision_votes WHERE decision_id = ? GROUP BY option_index ORDER BY c DESC LIMIT 1", (d_id,))
                    winner_data = await v_cursor.fetchone()

                if winner_data:
                    win_idx, win_count = winner_data
                    winner_text = options[win_idx]
                    embed.add_field(name=f"⚖️ {title}", value=f"**القرار الفائز:** {winner_text} ({win_count} أصوات)", inline=False)
                else:
                    embed.add_field(name=f"⚖️ {title}", value="*لم يشارك أحد في التصويت*", inline=False)

            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            print(f"Error in nexus_memory: {e}")
            await interaction.response.send_message("⚠️ حدث خطأ أثناء تنفيذ الأمر.", ephemeral=True)


class DecisionVoteView(discord.ui.View):
    def __init__(self, decision_id: int, options: list):
        super().__init__(timeout=None)
        self.decision_id = decision_id

        for i, opt in enumerate(options):
            label = opt if len(opt) <= 80 else opt[:77] + "..."
            btn = discord.ui.Button(
                style=discord.ButtonStyle.primary,
                label=label,
                custom_id=f"decision_vote_{decision_id}_{i}"
            )
            btn.callback = self.make_callback(i)
            self.add_item(btn)

    def make_callback(self, option_index: int):
        async def callback(interaction: discord.Interaction):
            try:
                async with aiosqlite.connect(DB_PATH) as db:
                    # Check if still active
                    row = await db.execute("SELECT is_active FROM collective_decisions WHERE id = ?", (self.decision_id,))
                    dec = await row.fetchone()
                    if not dec or dec[0] == 0:
                        await interaction.response.send_message("❌ انتهى التصويت على هذا القرار.", ephemeral=True)
                        return

                    # Insert or update vote
                    await db.execute("""
                        INSERT INTO decision_votes (decision_id, user_id, option_index)
                        VALUES (?, ?, ?)
                        ON CONFLICT(decision_id, user_id) DO UPDATE SET option_index = ?
                    """, (self.decision_id, interaction.user.id, option_index, option_index))
                    await db.commit()

                await interaction.response.send_message("✅ تم تسجيل صوتك بنجاح. لقد ساهمت في تشكيل مصير النيكسوس!", ephemeral=True)
            except Exception as e:
                print(f"Error voting on decision: {e}")
                await interaction.response.send_message("⚠️ عذراً، حدث خطأ أثناء التصويت.", ephemeral=True)
        return callback

async def setup(bot: StoryBot):
    await bot.add_cog(SocialCog(bot))
