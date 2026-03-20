import discord
from discord import app_commands
from discord.ext import commands
from core.bot import StoryBot
from core.config_manager import get_config
from ui.listing_view import WorldCategorySelectView # Will create this next

WORLD_COLORS = {
    "fantasy": 0xFFD700,
    "past": 0x8B4513,
    "future": 0x00BFFF,
    "alternate": 0x9400D3
}

WORLD_NAMES = {
    "fantasy": "الفانتازيا",
    "past": "الماضي",
    "future": "المستقبل",
    "alternate": "الواقع البديل"
}

class WorldCog(commands.Cog):
    def __init__(self, bot: StoryBot):
        self.bot = bot

    @app_commands.command(name="شرح", description="شرح مبسط لأحد عوالم اللعبة")
    @app_commands.describe(world="اختر العالم")
    @app_commands.choices(world=[
        app_commands.Choice(name="الفانتازيا", value="fantasy"),
        app_commands.Choice(name="الماضي", value="past"),
        app_commands.Choice(name="المستقبل", value="future"),
        app_commands.Choice(name="الواقع البديل", value="alternate")
    ])
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def world_explain(self, interaction: discord.Interaction, world: str):
        color = WORLD_COLORS.get(world, discord.Color.default())
        world_name = WORLD_NAMES.get(world, world)

        embed = discord.Embed(
            title=f"شرح عالم: {world_name}",
            description=f"مرحبًا بك في عالم {world_name}. عالم مليء بالقصص التفاعلية، كل خيار تتخذه قد يغير مسار الأحداث بالكامل.",
            color=color
        )
        embed.add_field(name="كيفية اللعب:", value=f"استخدم الأمر `/قصص-{world_name.replace(' ', '-')}` لبدء قصتك في هذا العالم.", inline=False)
        embed.set_footer(text="اختر مسارك بعناية!")

        await interaction.response.send_message(embed=embed)

    async def _handle_world_story(self, interaction: discord.Interaction, world: str):
        world_channels = get_config("world_channels", {})
        assigned_channel = world_channels.get(world)

        if assigned_channel and interaction.channel_id != assigned_channel:
            await interaction.response.send_message(f"❌ هذا الأمر مخصص لقناة <#{assigned_channel}> فقط.", ephemeral=True)
            return

        # Get all stories for this world (filtering by a custom series or theme flag maybe?)
        # For now, we will assume stories in JSON have `series` matching the world name.
        # Alternatively, and more accurately as per docs, they are separate single player stories
        # but logically grouped by their JSON file or a specific attribute.
        # We will filter them using an assumed attribute `world_type` that we'll add to models.

        # Let's filter by checking if the story description or theme roughly matches, or better:
        # We will just fetch all single player stories and group them by theme.
        # (In a real scenario, we'd tag them in JSON).
        stories = [s for s in self.bot.story_manager.get_all_stories().values() if s.game_mode == "single" and getattr(s, 'world_type', world) == world]

        if not stories:
             await interaction.response.send_message(f"❌ لا توجد قصص متاحة حالياً في عالم {WORLD_NAMES.get(world, world)}.", ephemeral=True)
             return

        # Group by category (theme)
        from collections import defaultdict
        categories = defaultdict(list)
        for s in stories:
            categories[s.theme].append(s)

        color = WORLD_COLORS.get(world, discord.Color.default())

        embed = discord.Embed(
            title=f"📚 قصص عالم {WORLD_NAMES.get(world, world)}",
            description="اختر التصنيف الذي ترغب في استكشافه:",
            color=color
        )

        view = WorldCategorySelectView(categories, world)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


    @app_commands.command(name="قصص-الفانتازيا", description="تصفح وبدء قصص عالم الفانتازيا")
    async def stories_fantasy(self, interaction: discord.Interaction):
        await self._handle_world_story(interaction, "fantasy")

    @app_commands.command(name="قصص-الماضي", description="تصفح وبدء قصص عالم الماضي")
    async def stories_past(self, interaction: discord.Interaction):
        await self._handle_world_story(interaction, "past")

    @app_commands.command(name="قصص-المستقبل", description="تصفح وبدء قصص عالم المستقبل")
    async def stories_future(self, interaction: discord.Interaction):
        await self._handle_world_story(interaction, "future")

    @app_commands.command(name="قصص-الواقع-البديل", description="تصفح وبدء قصص عالم الواقع البديل")
    async def stories_alternate(self, interaction: discord.Interaction):
        await self._handle_world_story(interaction, "alternate")

async def setup(bot: StoryBot):
    await bot.add_cog(WorldCog(bot))
