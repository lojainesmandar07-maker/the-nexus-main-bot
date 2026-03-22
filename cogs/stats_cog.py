import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite
import asyncio

from core.bot import StoryBot

DB_PATH = "data/nexus.db"


async def init_stats_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                title TEXT DEFAULT 'الراوي المبتدئ',
                stories_completed INTEGER DEFAULT 0,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await db.commit()


class StatsCog(commands.Cog):
    def __init__(self, bot: StoryBot):
        self.bot = bot
        asyncio.create_task(init_stats_db())

    @app_commands.command(name="إحصائياتي", description="ملخص سريع لإحصائياتك")
    async def my_stats(self, interaction: discord.Interaction):
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                row = await db.execute(
                    "SELECT stories_completed, title FROM players WHERE user_id = ?",
                    (interaction.user.id,),
                )
                player = await row.fetchone()

            stories_completed = player[0] if player else 0
            title = player[1] if player else "الراوي المبتدئ"

            embed = discord.Embed(
                title=f"📊 إحصائيات {interaction.user.display_name}",
                color=discord.Color.dark_teal(),
            )
            embed.add_field(name="🏷️ اللقب", value=title, inline=False)
            embed.add_field(name="📖 القصص المكتملة", value=str(stories_completed), inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            print(f"[StatsCog] my_stats error: {e}")
            await interaction.response.send_message("⚠️ تعذر تحميل الإحصائيات حالياً.", ephemeral=True)


async def setup(bot: StoryBot):
    await bot.add_cog(StatsCog(bot))
