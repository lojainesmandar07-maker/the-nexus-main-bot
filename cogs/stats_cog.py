import discord
from discord import app_commands
from discord.ext import commands
from core.bot import StoryBot
import aiosqlite

DB_PATH = "data/nexus.db"

class StatsCog(commands.Cog):
    def __init__(self, bot: StoryBot):
        self.bot = bot

    @app_commands.command(name="إحصائيات", description="عرض إحصائيات النيكسوس العالمية")
    async def global_stats(self, interaction: discord.Interaction):
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                # Total players
                row = await db.execute("SELECT COUNT(*) FROM players")
                total_players = (await row.fetchone())[0]

                # Total stories played
                row = await db.execute("SELECT SUM(stories_completed) FROM players")
                total_completed = (await row.fetchone())[0] or 0

                # Most popular story
                row = await db.execute("SELECT story_id, COUNT(*) as count FROM story_plays GROUP BY story_id ORDER BY count DESC LIMIT 1")
                popular_story_data = await row.fetchone()

            popular_story_title = "مجهولة"
            if popular_story_data:
                s_id, count = popular_story_data
                story = self.bot.story_manager.get_story(s_id)
                if story:
                    popular_story_title = f"{story.title} ({count} مرة)"

            embed = discord.Embed(
                title="📊 إحصائيات عالم النيكسوس",
                color=discord.Color.blue()
            )
            embed.add_field(name="إجمالي المغامرين", value=str(total_players), inline=True)
            embed.add_field(name="القصص المنجزة", value=str(total_completed), inline=True)
            embed.add_field(name="القصة الأكثر شعبية", value=popular_story_title, inline=False)

            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            print(f"Error in global_stats: {e}")
            await interaction.response.send_message("⚠️ حدث خطأ أثناء تنفيذ الأمر.", ephemeral=True)

    @app_commands.command(name="لوحة_الشرف", description="عرض أفضل الرواة والمغامرين في النيكسوس")
    async def leaderboard(self, interaction: discord.Interaction):
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute("""
                    SELECT user_id, title, stories_completed
                    FROM players
                    ORDER BY stories_completed DESC
                    LIMIT 10
                """)
                top_players = await cursor.fetchall()

            if not top_players:
                await interaction.response.send_message("❌ لوحة الشرف فارغة حالياً.", ephemeral=True)
                return

            embed = discord.Embed(
                title="🏆 لوحة الشرف الأسطورية",
                description="أعظم رواة ومغامري النيكسوس:",
                color=discord.Color.gold()
            )

            for idx, (user_id, title, count) in enumerate(top_players, start=1):
                emoji = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else "🏅"
                embed.add_field(
                    name=f"{emoji} المركز {idx}",
                    value=f"<@{user_id}>\n**اللقب:** {title}\n**القصص المنجزة:** {count}",
                    inline=False
                )

            await interaction.response.send_message(embed=embed, ephemeral=False)
        except Exception as e:
            print(f"Error in leaderboard: {e}")
            await interaction.response.send_message("⚠️ حدث خطأ أثناء تنفيذ الأمر.", ephemeral=True)

async def setup(bot: StoryBot):
    await bot.add_cog(StatsCog(bot))
