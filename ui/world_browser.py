import discord
from discord.ui import View, Select, Button
from ui.embeds import EmbedBuilder

WORLD_CONFIG = {
    "solo": {
        "name": "القصص الفردية",
        "desc": "مجموعة من القصص المنوعة للعب الفردي.",
        "emoji": "👤",
        "color": discord.Color.blue()
    },
    "fantasy": {
        "name": "عالم الفانتازيا",
        "desc": "عالم السحر والمخلوقات الأسطورية.",
        "emoji": "🐉",
        "color": discord.Color.purple()
    },
    "past": {
        "name": "عالم الماضي",
        "desc": "رحلة عبر الزمن إلى العصور القديمة.",
        "emoji": "⏳",
        "color": discord.Color.gold()
    },
    "future": {
        "name": "عالم المستقبل",
        "desc": "تكنولوجيا متقدمة وخيال علمي.",
        "emoji": "🚀",
        "color": discord.Color.teal()
    },
    "alternate": {
        "name": "العالم البديل",
        "desc": "حقائق بديلة وأبعاد موازية.",
        "emoji": "🌀",
        "color": discord.Color.dark_magenta()
    }
}

class WorldSelectView(View):
    def __init__(self):
        super().__init__(timeout=None)

        options = []
        for w_type, w_info in WORLD_CONFIG.items():
            options.append(discord.SelectOption(
                label=w_info["name"],
                description=w_info["desc"],
                emoji=w_info["emoji"],
                value=w_type
            ))

        select = Select(
            custom_id="world_select_dropdown",
            placeholder="اختر العالم الذي تريد استكشافه...",
            options=options,
            min_values=1,
            max_values=1
        )
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        select = self.children[0]
        world_type = select.values[0]

        bot = interaction.client
        categories = bot.story_manager.get_world_categories(world_type)

        if not categories:
            await interaction.response.send_message("❌ لا توجد قصص متاحة في هذا العالم حالياً.", ephemeral=True)
            return

        view = CategoryBrowserView(world_type, categories)
        embed = EmbedBuilder.category_browser_embed(world_type, WORLD_CONFIG[world_type]["name"], WORLD_CONFIG[world_type]["desc"])

        await interaction.response.edit_message(embed=embed, view=view)


class CategoryBrowserView(View):
    def __init__(self, world_type: str, categories: dict):
        super().__init__(timeout=None)
        self.world_type = world_type
        self.categories = categories

        # Add category select
        options = []
        for i, category in enumerate(categories.keys()):
            # Limit options to max 25 (discord limit)
            if i >= 25:
                break
            options.append(discord.SelectOption(
                label=category,
                value=category
            ))

        if options:
            cat_select = CategorySelect(self.world_type, options)
            self.add_item(cat_select)

        # Add back button
        self.add_item(BackToWorldsButton())


class CategorySelect(Select):
    def __init__(self, world_type: str, options: list):
        super().__init__(
            custom_id=f"cat_select_{world_type}",
            placeholder="اختر التصنيف...",
            options=options,
            min_values=1,
            max_values=1
        )
        self.world_type = world_type

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        bot = interaction.client

        stories = bot.story_manager.get_stories_by_world_and_category(self.world_type, category)

        if not stories:
            await interaction.response.send_message("❌ لا توجد قصص في هذا التصنيف.", ephemeral=True)
            return

        # Update view to show stories in this category
        view = View(timeout=None)

        options = []
        for i, story in enumerate(stories):
            if i >= 25:
                break
            options.append(discord.SelectOption(
                label=story.title,
                description=story.description[:50] + "..." if story.description and len(story.description) > 50 else (story.description or "بدون وصف"),
                value=str(story.id)
            ))

        if options:
            story_select = StorySelect(self.world_type, category, options)
            view.add_item(story_select)

        view.add_item(BackToWorldsButton())

        # We edit the message to keep the same UI flow
        await interaction.response.edit_message(view=view)


class StorySelect(Select):
    def __init__(self, world_type: str, category: str, options: list):
        super().__init__(
            custom_id=f"story_select_{world_type}_{category}",
            placeholder="اختر القصة...",
            options=options,
            min_values=1,
            max_values=1
        )
        self.world_type = world_type
        self.category = category

    async def callback(self, interaction: discord.Interaction):
        story_id = int(self.values[0])
        bot = interaction.client

        story = bot.story_manager.get_story(story_id)
        if not story:
            await interaction.response.send_message("❌ لم يتم العثور على القصة.", ephemeral=True)
            return

        embed = EmbedBuilder.story_preview_embed(story)

        view = View(timeout=None)
        view.add_item(StartStoryButton(story.id))
        view.add_item(BackToWorldsButton())

        await interaction.response.edit_message(embed=embed, view=view)


class StartStoryButton(Button):
    def __init__(self, story_id: int):
        super().__init__(
            style=discord.ButtonStyle.success,
            label="ابدأ القصة",
            custom_id=f"start_story_btn_{story_id}"
        )
        self.story_id = story_id

    async def callback(self, interaction: discord.Interaction):
        # Check exclusive story locks
        try:
            import aiosqlite
            DB_PATH = "data/nexus.db"
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute("SELECT winner_id FROM mystery_rooms WHERE is_active = 1 AND exclusive_story_id = ?", (self.story_id,))
                lock = await cursor.fetchone()
                if lock:
                    winner_id = lock[0]
                    if winner_id != interaction.user.id:
                        await interaction.response.send_message("❌ هذه القصة مقفلة حالياً خلف لغز غرفة الغموض! كن أول من يحل اللغز أو انتظر حتى تتاح للجميع.", ephemeral=True)
                        return
        except Exception as e:
            print(f"Error checking story locks: {e}")

        cog = interaction.client.get_cog("SoloCog")
        if not cog:
            await interaction.response.send_message("❌ لم يتم تحميل أوامر اللعب الفردي.", ephemeral=True)
            return

        session, error = cog.solo_manager.start_solo_game(interaction.user.id, self.story_id)
        if error:
            await interaction.response.send_message(embed=EmbedBuilder.error_embed(error), ephemeral=True)
            return

        story = session["story"]
        scene = session["scene"]
        points = session["points"]
        round_number = session["round"]

        from ui.solo_view import SoloView
        embed = EmbedBuilder.solo_scene_embed(scene, round_number, story.title, points)

        view = None
        if not scene.is_ending and scene.choices:
            view = SoloView(cog.solo_manager, interaction.user.id, scene.choices)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class BackToWorldsButton(Button):
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            label="العودة للعوالم",
            custom_id="back_to_worlds_btn"
        )

    async def callback(self, interaction: discord.Interaction):
        view = WorldSelectView()
        embed = EmbedBuilder.world_select_embed()
        await interaction.response.edit_message(embed=embed, view=view)
