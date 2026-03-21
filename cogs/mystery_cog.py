import discord
from discord import app_commands
from discord.ext import commands, tasks
from core.bot import StoryBot
from core.config import get_config
import aiosqlite
import datetime
import json
import os

DB_PATH = "data/nexus.db"

def load_mystery_rooms():
    try:
        with open("data/mystery_rooms.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading mystery_rooms.json: {e}")
        return []

async def init_mystery_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS mystery_rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                riddle TEXT,
                answer TEXT,
                hint TEXT,
                winner_id INTEGER,
                exclusive_story_id INTEGER,
                opens_at TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                message_id INTEGER,
                source_id TEXT UNIQUE
            )
        """)
        try:
            await db.execute("ALTER TABLE mystery_rooms ADD COLUMN source_id TEXT UNIQUE")
            await db.commit()
        except Exception:
            pass # Column already exists

class MysteryRoomModal(discord.ui.Modal, title="إنشاء غرفة الغموض"):
    riddle = discord.ui.TextInput(label="اللغز", style=discord.TextStyle.paragraph, required=True)
    answer = discord.ui.TextInput(label="الجواب", style=discord.TextStyle.short, required=True)
    hint = discord.ui.TextInput(label="تلميح (اختياري)", style=discord.TextStyle.paragraph, required=False)
    story_id = discord.ui.TextInput(label="رقم القصة الحصرية", style=discord.TextStyle.short, required=True)
    days = discord.ui.TextInput(label="أيام قبل الفتح للكل", style=discord.TextStyle.short, default="7", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            s_id = int(self.story_id.value)
            d_val = int(self.days.value)
        except ValueError:
            await interaction.response.send_message("❌ يجب أن يكون رقم القصة وعدد الأيام أرقاماً صحيحة.", ephemeral=True)
            return

        opens_at = datetime.datetime.utcnow() + datetime.timedelta(days=d_val)

        # Post the riddle to the server general channel (e.g. endings_channel or a test channel for now)
        world_channels = get_config("world_channels", {})
        target_channel_id = world_channels.get("general_channel") or world_channels.get("endings_channel") or get_config("test_channel")

        if not target_channel_id:
             await interaction.response.send_message("❌ لم يتم تحديد قناة عامة لنشر اللغز في الإعدادات.", ephemeral=True)
             return

        channel = interaction.client.get_channel(int(target_channel_id))
        if not channel:
             await interaction.response.send_message("❌ القناة المحددة غير موجودة.", ephemeral=True)
             return

        embed = discord.Embed(
            title="🚪 غرفة الغموض الجديدة",
            description=f"**لقد ظهر لغز جديد في النيكسوس!**\n\n{self.riddle.value}\n\n*أول من يقوم بحل اللغز عبر `/حل` سيحصل على وصول حصري لقصة سرية!*",
            color=discord.Color.dark_magenta()
        )
        embed.set_footer(text="استخدم /تلميح إذا احتجت مساعدة لاحقاً")

        msg = await channel.send(embed=embed)

        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                INSERT INTO mystery_rooms (riddle, answer, hint, exclusive_story_id, opens_at, message_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.riddle.value, self.answer.value, self.hint.value, s_id, opens_at, msg.id))
            await db.commit()

        await interaction.response.send_message("✅ تم إنشاء غرفة الغموض ونشر اللغز بنجاح!", ephemeral=True)


class MysteryCog(commands.Cog):
    def __init__(self, bot: StoryBot):
        self.bot = bot
        self.bot.loop.create_task(init_mystery_db())
        self.check_opens_loop.start()
        self.auto_mystery_loop.start()

    def cog_unload(self):
        self.check_opens_loop.cancel()
        self.auto_mystery_loop.cancel()

    @tasks.loop(hours=1.0)
    async def check_opens_loop(self):
        """Background task: check if opens_at passed -> announce story now open for all"""
        now = datetime.datetime.utcnow()
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("SELECT id, exclusive_story_id FROM mystery_rooms WHERE is_active = 1 AND opens_at <= ?", (now,))
            expired_rooms = await cursor.fetchall()

            for r_id, story_id in expired_rooms:
                await db.execute("UPDATE mystery_rooms SET is_active = 0 WHERE id = ?", (r_id,))
                await db.commit()

                # Announce
                world_channels = get_config("world_channels", {})
                ch_id = world_channels.get("general_channel") or world_channels.get("endings_channel") or get_config("test_channel")
                if ch_id:
                    channel = self.bot.get_channel(int(ch_id))
                    if channel:
                        story = self.bot.story_manager.get_story(story_id)
                        s_name = story.title if story else f"قصة #{story_id}"
                        embed = discord.Embed(
                            title="🔓 انفتحت أبواب الغموض",
                            description=f"القصة الحصرية **{s_name}** أصبحت الآن متاحة للجميع للعب!\nاستخدم `/لعب_فردي` لاستكشافها.",
                            color=discord.Color.green()
                        )
                        await channel.send(embed=embed)

    @check_opens_loop.before_loop
    async def before_check_opens(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=24.0)
    async def auto_mystery_loop(self):
        """Check if an active mystery room exists, if not, create one from JSON."""
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("SELECT id FROM mystery_rooms WHERE is_active = 1")
            active = await cursor.fetchone()
            if active:
                return # Already have an active room

            rooms_data = load_mystery_rooms()
            if not rooms_data:
                return

            for room in rooms_data:
                r_id = room.get("id")
                cursor = await db.execute("SELECT id FROM mystery_rooms WHERE source_id = ?", (r_id,))
                if not await cursor.fetchone():
                    # This room hasn't been used yet
                    world_channels = get_config("world_channels", {})
                    target_channel_id = world_channels.get("general_channel") or world_channels.get("endings_channel") or get_config("test_channel")

                    if target_channel_id:
                        channel = self.bot.get_channel(int(target_channel_id))
                        if channel:
                            embed = discord.Embed(
                                title="🚪 غرفة الغموض الجديدة",
                                description=f"**لقد ظهر لغز جديد في النيكسوس!**\n\n{room.get('riddle')}\n\n*أول من يقوم بحل اللغز عبر `/حل` سيحصل على وصول حصري لقصة سرية!*",
                                color=discord.Color.dark_magenta()
                            )
                            embed.set_footer(text="استخدم /تلميح إذا احتجت مساعدة لاحقاً")

                            msg = await channel.send(embed=embed)

                            opens_at = datetime.datetime.utcnow() + datetime.timedelta(days=room.get("unlock_days", 7))

                            await db.execute("""
                                INSERT INTO mystery_rooms (riddle, answer, hint, exclusive_story_id, opens_at, message_id, source_id)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (room.get("riddle"), room.get("answer"), room.get("hint"), room.get("exclusive_story_id"), opens_at, msg.id, r_id))
                            await db.commit()
                    break # Only spawn one at a time

    @auto_mystery_loop.before_loop
    async def before_auto_mystery_loop(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="غرفة_جديدة", description="إنشاء لغز وغرفة غموض جديدة (للإدارة فقط)")
    @app_commands.default_permissions(manage_guild=True)
    async def new_mystery_room(self, interaction: discord.Interaction):
        try:
            if not interaction.user.guild_permissions.manage_guild:
                await interaction.response.send_message("❌ هذا الأمر مخصص للإدارة فقط.", ephemeral=True)
                return
            await interaction.response.send_modal(MysteryRoomModal())
        except Exception as e:
            print(f"Error in new_mystery_room: {e}")
            await interaction.response.send_message("⚠️ حدث خطأ أثناء تنفيذ الأمر.", ephemeral=True)

    @app_commands.command(name="حل", description="حاول حل اللغز النشط في غرفة الغموض")
    @app_commands.describe(answer="جواب اللغز الخاص بك")
    async def solve_mystery(self, interaction: discord.Interaction, answer: str):
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute("SELECT id, answer, winner_id, exclusive_story_id FROM mystery_rooms WHERE is_active = 1 ORDER BY id DESC LIMIT 1")
                room = await cursor.fetchone()

            if not room:
                await interaction.response.send_message("❌ لا توجد غرفة غموض نشطة حالياً.", ephemeral=True)
                return

            r_id, correct_answer, winner_id, story_id = room

            if winner_id:
                await interaction.response.send_message("❌ لقد قام شخص آخر بحل اللغز مسبقاً! انتظر حتى تتاح القصة للجميع.", ephemeral=True)
                return

            user_ans = answer.strip().lower()
            db_ans = correct_answer.strip().lower()

            if user_ans == db_ans:
                # Correct!
                async with aiosqlite.connect(DB_PATH) as db:
                    await db.execute("UPDATE mystery_rooms SET winner_id = ? WHERE id = ?", (interaction.user.id, r_id))
                    await db.commit()

                story = self.bot.story_manager.get_story(story_id)
                s_name = story.title if story else f"القصة #{story_id}"

                # Announce winner
                world_channels = get_config("world_channels", {})
                ch_id = world_channels.get("general_channel") or world_channels.get("endings_channel") or get_config("test_channel")
                if ch_id:
                    channel = self.bot.get_channel(int(ch_id))
                    if channel:
                        embed = discord.Embed(
                            title="🎉 لغز محلول!",
                            description=f"تهانينا لـ <@{interaction.user.id}> لقد حل اللغز الصحيح للغرفة المظلمة!\n\nلقد حصل على وصول حصري مبكر إلى **{s_name}**.",
                            color=discord.Color.gold()
                        )
                        await channel.send(embed=embed)

                await interaction.response.send_message(f"✅ جواب صحيح! لقد فككت الشفرة وربحت وصولاً حصرياً إلى **{s_name}**.", ephemeral=True)
            else:
                await interaction.response.send_message("❌ جواب خاطئ. حاول مرة أخرى!", ephemeral=True)
        except Exception as e:
            print(f"Error in solve_mystery: {e}")
            await interaction.response.send_message("⚠️ حدث خطأ أثناء تنفيذ الأمر.", ephemeral=True)

    @app_commands.command(name="تلميح", description="الحصول على تلميح للغز الحالي (متاح بعد 48 ساعة من النشر)")
    async def mystery_hint(self, interaction: discord.Interaction):
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute("SELECT hint, message_id FROM mystery_rooms WHERE is_active = 1 ORDER BY id DESC LIMIT 1")
                room = await cursor.fetchone()

            if not room:
                await interaction.response.send_message("❌ لا توجد غرفة غموض نشطة حالياً.", ephemeral=True)
                return

            hint, msg_id = room
            if not hint:
                await interaction.response.send_message("❌ لا يوجد تلميح لهذا اللغز.", ephemeral=True)
                return

            # Check if 48 hrs passed
            try:
                 creation_time = discord.utils.snowflake_time(msg_id)
                 now = discord.utils.utcnow()
                 if (now - creation_time).total_seconds() < 48 * 3600:
                     time_left = 48 - ((now - creation_time).total_seconds() / 3600)
                     await interaction.response.send_message(f"❌ التلميح لن يكون متاحاً إلا بعد {time_left:.1f} ساعة.", ephemeral=True)
                     return
            except Exception:
                 pass

            embed = discord.Embed(
                title="💡 تلميح اللغز",
                description=hint,
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            print(f"Error in mystery_hint: {e}")
            await interaction.response.send_message("⚠️ حدث خطأ أثناء تنفيذ الأمر.", ephemeral=True)

async def setup(bot: StoryBot):
    await bot.add_cog(MysteryCog(bot))
