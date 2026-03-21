import discord
from discord import app_commands
from discord.ext import commands
from core.bot import StoryBot
from core.category_catalog import SOLO_CATEGORIES
from ui.embeds import EmbedBuilder
from ui.solo_view import SoloView

class SoloCog(commands.Cog):
    def __init__(self, bot: StoryBot):
        self.bot = bot
        from engine.solo_manager import SoloGameManager
        self.solo_manager = SoloGameManager(bot, bot.story_manager)

    @app_commands.command(name="ابدأ", description="افتح مستكشف العوالم وابدأ رحلتك في القصص التفاعلية")
    async def start_browser(self, interaction: discord.Interaction):
        from ui.world_browser import WorldSelectView
        from ui.embeds import EmbedBuilder
        view = WorldSelectView()
        embed = EmbedBuilder.world_select_embed()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="مساعدة", description="عرض تعليمات ومعلومات حول كيفية استخدام بوت القصص التفاعلية")
    async def help_command(self, interaction: discord.Interaction):
        from ui.embeds import EmbedBuilder
        embed = EmbedBuilder.help_embed()
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="لعب_فردي", description="ابدأ قصة تفاعلية بمفردك")
    @app_commands.describe(story_id="رقم القصة التي تود لعبها")
    async def play_solo(self, interaction: discord.Interaction, story_id: int):
        await interaction.response.defer(ephemeral=True)

        session, error = self.solo_manager.start_solo_game(interaction.user.id, story_id)
        if error:
            await interaction.followup.send(embed=EmbedBuilder.error_embed(error), ephemeral=True)
            return

        story = session["story"]
        scene = session["scene"]
        points = session["points"]
        round_number = session["round"]

        embed = EmbedBuilder.solo_scene_embed(scene, round_number, story.title, points)

        view = None
        if not scene.is_ending and scene.choices:
            view = SoloView(self.solo_manager, interaction.user.id, scene.choices)

        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="قصص_فردية", description="عرض جميع القصص المتاحة للعب الفردي مصنفة في قوائم")
    async def list_solo_stories(self, interaction: discord.Interaction):
        stories = self.bot.story_manager.get_stories_by_mode("single")
        if not stories:
            await interaction.response.send_message("❌ لا توجد قصص فردية متاحة حالياً.", ephemeral=True)
            return

        # Group by category
        from collections import defaultdict
        categories = defaultdict(list)
        for s in stories.values():
            categories[s.theme].append(s)

        from ui.listing_view import SoloLibraryView
        view = SoloLibraryView(categories)
        embed = view.render_embed()

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="تصنيفات_فردية", description="عرض قائمة التصنيفات المقترحة للقصص الفردية")
    async def list_solo_categories(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🗂️ تصنيفات القصص الفردية",
            description="استخدم هذه التصنيفات عند توليد قصص جديدة لضمان تنظيم المكتبة وتوحيد الثيمات.",
            color=discord.Color.dark_purple(),
        )

        for index, category in enumerate(SOLO_CATEGORIES, start=1):
            embed.add_field(
                name=f"{index}. {category.name}",
                value=category.description,
                inline=False,
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def start_solo_interaction(interaction: discord.Interaction, story_id: int):
    # This function is used by the StoryButton in listing_view.py to bypass the command
    bot = interaction.client
    cog = bot.get_cog("SoloCog")

    if not cog:
        await interaction.response.send_message("❌ لم يتم تحميل أوامر اللعب الفردي.", ephemeral=True)
        return

    session, error = cog.solo_manager.start_solo_game(interaction.user.id, story_id)
    if error:
        from ui.embeds import EmbedBuilder
        await interaction.response.send_message(embed=EmbedBuilder.error_embed(error), ephemeral=True)
        return

    story = session["story"]
    scene = session["scene"]
    points = session["points"]
    round_number = session["round"]

    from ui.embeds import EmbedBuilder
    from ui.solo_view import SoloView
    embed = EmbedBuilder.solo_scene_embed(scene, round_number, story.title, points)

    view = None
    if not scene.is_ending and scene.choices:
        view = SoloView(cog.solo_manager, interaction.user.id, scene.choices)

    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot: StoryBot):
    await bot.add_cog(SoloCog(bot))
