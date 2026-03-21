import discord
from discord import app_commands
from discord.ext import commands
from core.bot import StoryBot
import aiosqlite
import datetime
import uuid

DB_PATH = "data/nexus.db"

async def init_challenge_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS weekly_challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                target_story_id INTEGER,
                target_ending_id TEXT,
                reward_role_id TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS challenge_completions (
                user_id INTEGER,
                challenge_id INTEGER,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, challenge_id),
                FOREIGN KEY (challenge_id) REFERENCES weekly_challenges(id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS shared_endings (
                id TEXT PRIMARY KEY,
                user_id INTEGER,
                story_id INTEGER,
                ending_id TEXT,
                ending_text TEXT,
                shared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS story_plays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                story_id INTEGER,
                ending_id TEXT,
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

class ChallengeCog(commands.Cog):
    def __init__(self, bot: StoryBot):
        self.bot = bot
        self.bot.loop.create_task(init_challenge_db())

    @app_commands.command(name="تحدي_الأسبوع", description="عرض التحدي الأسبوعي النشط")
    async def show_challenge(self, interaction: discord.Interaction):
        async with aiosqlite.connect(DB_PATH) as db:
            row = await db.execute("SELECT id, title, description, reward_role_id, target_story_id FROM weekly_challenges WHERE is_active = 1 ORDER BY created_at DESC LIMIT 1")
            challenge = await row.fetchone()

        if not challenge:
            await interaction.response.send_message("❌ لا يوجد تحدي أسبوعي نشط حالياً. عد لاحقاً!", ephemeral=True)
            return

        c_id, title, desc, role_id, story_id = challenge
        story = self.bot.story_manager.get_story(story_id)
        story_name = story.title if story else "مجهولة"

        embed = discord.Embed(
            title=f"⚔️ {title}",
            description=f"{desc}\n\n**القصة المستهدفة:** {story_name}",
            color=discord.Color.gold()
        )
        if role_id:
            embed.add_field(name="الجائزة", value=f"<@&{role_id}>", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="إنشاء_تحدي", description="إنشاء تحدي أسبوعي جديد (للإدارة فقط)")
    @app_commands.describe(
        title="عنوان التحدي",
        description="وصف التحدي",
        story_id="رقم القصة المستهدفة",
        ending_id="معرف النهاية المستهدفة",
        role_id="معرف الرتبة للجائزة (اختياري)"
    )
    @app_commands.default_permissions(manage_guild=True)
    async def create_challenge(self, interaction: discord.Interaction, title: str, description: str, story_id: int, ending_id: str, role_id: str = None):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ هذا الأمر مخصص للإدارة فقط.", ephemeral=True)
            return

        # Check if story exists
        story = self.bot.story_manager.get_story(story_id)
        if not story:
            await interaction.response.send_message("❌ رقم القصة غير صحيح.", ephemeral=True)
            return

        async with aiosqlite.connect(DB_PATH) as db:
            # Deactivate older challenges
            await db.execute("UPDATE weekly_challenges SET is_active = 0 WHERE is_active = 1")

            # Insert new challenge
            await db.execute("""
                INSERT INTO weekly_challenges (title, description, target_story_id, target_ending_id, reward_role_id)
                VALUES (?, ?, ?, ?, ?)
            """, (title, description, story_id, ending_id, role_id))
            await db.commit()

        embed = discord.Embed(
            title="✅ تم إنشاء التحدي الجديد",
            description=f"**{title}**\nالقصة: {story.title}\nالنهاية: {ending_id}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="إنجازاتي", description="عرض التحديات الأسبوعية التي أنجزتها")
    async def my_achievements(self, interaction: discord.Interaction):
        async with aiosqlite.connect(DB_PATH) as db:
            row = await db.execute("""
                SELECT w.title, c.completed_at
                FROM challenge_completions c
                JOIN weekly_challenges w ON c.challenge_id = w.id
                WHERE c.user_id = ?
                ORDER BY c.completed_at DESC
            """, (interaction.user.id,))
            completions = await row.fetchall()

        if not completions:
            await interaction.response.send_message("لم تنجز أي تحدي أسبوعي بعد. انطلق وشارك في `/تحدي_الأسبوع`!", ephemeral=True)
            return

        embed = discord.Embed(
            title="🏆 إنجازاتي في التحديات",
            color=discord.Color.purple()
        )
        for title, date in completions:
            date_str = date[:10] if date else "غير معروف"
            embed.add_field(name=title, value=f"تاريخ الإنجاز: {date_str}", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: StoryBot):
    await bot.add_cog(ChallengeCog(bot))