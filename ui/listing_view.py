import discord
from typing import Dict, List, Optional

from engine.models import Story


def _sorted_categories(categories: Dict[str, List[Story]]) -> Dict[str, List[Story]]:
    sorted_items = sorted(categories.items(), key=lambda item: item[0])
    return {
        category: sorted(stories, key=lambda story: (story.series, story.id, story.title))
        for category, stories in sorted_items
    }


def _story_select_options(stories: List[Story], start_index: int, page_size: int) -> List[discord.SelectOption]:
    options: List[discord.SelectOption] = []
    for story in stories[start_index:start_index + page_size]:
        description = f"ID: {story.id} | سلسلة: {story.series}"
        options.append(
            discord.SelectOption(
                label=story.title[:100],
                value=str(story.id),
                description=description[:100],
                emoji="📖",
            )
        )
    return options


class CategorySelect(discord.ui.Select):
    def __init__(self, parent_view: "BaseLibraryView"):
        self.parent_view = parent_view
        options = [
            discord.SelectOption(label=category[:100], value=category, emoji="🗂️")
            for category in parent_view.category_names
        ]
        super().__init__(placeholder="اختر تصنيفاً", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        self.parent_view.current_category = self.values[0]
        self.parent_view.story_page = 0
        self.parent_view.selected_story_id = None
        await self.parent_view.refresh_message(interaction)


class StorySelect(discord.ui.Select):
    def __init__(self, parent_view: "BaseLibraryView"):
        self.parent_view = parent_view
        stories = parent_view.current_stories
        start_index = parent_view.story_page * parent_view.page_size
        options = _story_select_options(stories, start_index, parent_view.page_size)

        super().__init__(
            placeholder="اختر قصة",
            options=options,
            min_values=1,
            max_values=1,
            disabled=not options,
        )

    async def callback(self, interaction: discord.Interaction):
        self.parent_view.selected_story_id = int(self.values[0])
        await self.parent_view.refresh_message(interaction)


class BaseLibraryView(discord.ui.View):
    def __init__(self, categories: Dict[str, List[Story]], timeout: float = 180):
        super().__init__(timeout=timeout)
        self.categories = _sorted_categories(categories)
        self.category_names = list(self.categories.keys())
        self.current_category = self.category_names[0] if self.category_names else None
        self.selected_story_id: Optional[int] = None
        self.page_size = 20
        self.story_page = 0
        self._rebuild_components()

    @property
    def current_stories(self) -> List[Story]:
        if not self.current_category:
            return []
        return self.categories.get(self.current_category, [])

    @property
    def max_page(self) -> int:
        stories = self.current_stories
        if not stories:
            return 0
        return (len(stories) - 1) // self.page_size

    def _rebuild_components(self):
        self.clear_items()
        if self.category_names:
            self.add_item(CategorySelect(self))
            self.add_item(StorySelect(self))
        self.add_item(PrevStoriesButton(self))
        self.add_item(NextStoriesButton(self))
        self.add_action_components()

    def add_action_components(self):
        return

    def build_embed(self, title: str, description: str, color: discord.Color) -> discord.Embed:
        embed = discord.Embed(title=title, description=description, color=color)

        if not self.current_category:
            embed.add_field(name="لا توجد بيانات", value="لم يتم العثور على تصنيفات حالياً.", inline=False)
            return embed

        stories = self.current_stories
        start_index = self.story_page * self.page_size
        end_index = min(start_index + self.page_size, len(stories))
        page_stories = stories[start_index:end_index]

        embed.add_field(name="التصنيف المختار", value=self.current_category, inline=False)
        embed.add_field(
            name="الصفحة",
            value=f"{self.story_page + 1}/{self.max_page + 1} (إجمالي القصص في التصنيف: {len(stories)})",
            inline=False,
        )

        if page_stories:
            preview = "\n".join(
                f"• #{story.id} | سلسلة {story.series} — {story.title}" for story in page_stories[:8]
            )
            embed.add_field(name="معاينة القصص", value=preview[:1024], inline=False)

        if self.selected_story_id is not None:
            selected_story = next((story for story in stories if story.id == self.selected_story_id), None)
            if selected_story:
                embed.add_field(
                    name="القصة المختارة",
                    value=(
                        f"**{selected_story.title}**\n"
                        f"ID: `{selected_story.id}` | سلسلة: `{selected_story.series}`\n"
                        f"{selected_story.description[:240]}"
                    ),
                    inline=False,
                )

        return embed

    async def refresh_message(self, interaction: discord.Interaction):
        self.story_page = max(0, min(self.story_page, self.max_page))
        self._rebuild_components()
        embed = self.render_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    def render_embed(self) -> discord.Embed:
        raise NotImplementedError


class PrevStoriesButton(discord.ui.Button):
    def __init__(self, parent_view: BaseLibraryView):
        self.parent_view = parent_view
        super().__init__(label="⬅️ السابق", style=discord.ButtonStyle.secondary, row=2)

    async def callback(self, interaction: discord.Interaction):
        if self.parent_view.story_page > 0:
            self.parent_view.story_page -= 1
            self.parent_view.selected_story_id = None
        await self.parent_view.refresh_message(interaction)


class NextStoriesButton(discord.ui.Button):
    def __init__(self, parent_view: BaseLibraryView):
        self.parent_view = parent_view
        super().__init__(label="التالي ➡️", style=discord.ButtonStyle.secondary, row=2)

    async def callback(self, interaction: discord.Interaction):
        if self.parent_view.story_page < self.parent_view.max_page:
            self.parent_view.story_page += 1
            self.parent_view.selected_story_id = None
        await self.parent_view.refresh_message(interaction)


class StartSoloButton(discord.ui.Button):
    def __init__(self, parent_view: "SoloLibraryView"):
        self.parent_view = parent_view
        super().__init__(label="▶️ ابدأ اللعب الفردي", style=discord.ButtonStyle.success, row=3)

    async def callback(self, interaction: discord.Interaction):
        if self.parent_view.selected_story_id is None:
            await interaction.response.send_message("اختر قصة أولاً من القائمة.", ephemeral=True)
            return

        from cogs.solo_cog import start_solo_interaction

        await start_solo_interaction(interaction, self.parent_view.selected_story_id)


class StartEventButton(discord.ui.Button):
    def __init__(self, parent_view: "MultiLibraryView"):
        self.parent_view = parent_view
        super().__init__(label="🚀 بدء الحدث الآن", style=discord.ButtonStyle.primary, row=3)

    async def callback(self, interaction: discord.Interaction):
        if self.parent_view.selected_story_id is None:
            await interaction.response.send_message("اختر قصة جماعية أولاً.", ephemeral=True)
            return

        guild_permissions = getattr(interaction.user, "guild_permissions", None)
        if not guild_permissions or not guild_permissions.manage_guild:
            await interaction.response.send_message("❌ هذا الزر للمشرفين فقط.", ephemeral=True)
            return

        bot = interaction.client
        if bot.event_manager.active_event:
            await interaction.response.send_message("❌ يوجد حدث نشط حالياً. أوقفه ثم أعد المحاولة.", ephemeral=True)
            return

        story = bot.story_manager.get_story(self.parent_view.selected_story_id)
        if not story or story.game_mode != "multi":
            await interaction.response.send_message("❌ القصة المختارة غير متاحة كحدث جماعي.", ephemeral=True)
            return

        if interaction.channel is None:
            await interaction.response.send_message("❌ لا يمكن تشغيل الحدث هنا.", ephemeral=True)
            return

        await interaction.response.send_message(
            f"✅ سيتم بدء الحدث الآن: **{story.title}**\n⏱️ زمن التصويت: 30 ثانية.",
            ephemeral=True,
        )
        bot.loop.create_task(bot.event_manager.start_event(interaction.channel, story.id, voting_timeout=30.0))


class SoloLibraryView(BaseLibraryView):
    def __init__(self, categories: Dict[str, List[Story]], timeout: float = 180):
        super().__init__(categories, timeout=timeout)

    def add_action_components(self):
        self.add_item(StartSoloButton(self))

    def render_embed(self) -> discord.Embed:
        return self.build_embed(
            title="👤 مكتبة القصص الفردية",
            description="اختَر التصنيف ثم القصة من القوائم، وبعدها اضغط زر البدء.",
            color=discord.Color.purple(),
        )


class MultiLibraryView(BaseLibraryView):
    def __init__(self, categories: Dict[str, List[Story]], timeout: float = 180):
        super().__init__(categories, timeout=timeout)

    def add_action_components(self):
        self.add_item(StartEventButton(self))

    def render_embed(self) -> discord.Embed:
        return self.build_embed(
            title="👥 مكتبة الفعاليات الجماعية",
            description="اختَر التصنيف ثم القصة الجماعية، ويمكن للمشرف بدء الحدث مباشرة من الزر.",
            color=discord.Color.blue(),
        )

# --- Dynamic Button Subclasses for Persistence --- #

class StartSoloStoryButton(discord.ui.Button):
    def __init__(self, story_id: int, perspective: str = None):
        super().__init__(
            label=f"ابدأ القصة كـ {perspective}" if perspective else "ابدأ القصة",
            style=discord.ButtonStyle.success,
            custom_id=f"rpg_start_solo_{story_id}_{perspective}" if perspective else f"rpg_start_solo_{story_id}"
        )
        self.story_id = story_id
        self.perspective = perspective

    async def callback(self, interaction: discord.Interaction):
        from cogs.solo_cog import start_solo_interaction
        await start_solo_interaction(interaction, self.story_id, self.perspective)


class SoloPerspectiveSelect(discord.ui.Select):
    def __init__(self, story_id: int):
        self.story_id = story_id
        perspectives = ["القاتل", "المحقق", "الضحية"]
        options = [
            discord.SelectOption(label=p, value=p, emoji="🎭") for p in perspectives
        ]
        super().__init__(
            placeholder="اختر منظورك في هذه القصة...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=f"rpg_solo_persp_{self.story_id}"
        )

    async def callback(self, interaction: discord.Interaction):
        persp = self.values[0]
        start_button = StartSoloStoryButton(self.story_id, persp)
        view = discord.ui.View(timeout=None)
        view.add_item(start_button)
        await interaction.response.edit_message(content=f"أنت الآن مستعد للعب بدور **{persp}**.", view=view, embed=None)


class SoloStorySelect(discord.ui.Select):
    def __init__(self, category: str, stories: List[Story]):
        self.category_name = category
        options = []
        for s in stories:
            options.append(
                discord.SelectOption(
                    label=s.title,
                    description=s.description[:50] + "...",
                    value=str(s.id),
                    emoji="📖"
                )
            )
        super().__init__(
            placeholder="اختر قصة لتبدأها...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=f"rpg_solo_story_{category}"
        )

    async def callback(self, interaction: discord.Interaction):
        story_id = int(self.values[0])
        persp_select = SoloPerspectiveSelect(story_id)
        view = discord.ui.View(timeout=None)
        view.add_item(persp_select)
        await interaction.response.edit_message(content="الخطوة الأخيرة: اختر المنظور الذي تود أن تعيش القصة من خلاله.", view=view, embed=None)


class SoloCategorySelect(discord.ui.Select):
    def __init__(self, categories: dict):
        self.categories = categories
        options = []
        for cat_name, stories in self.categories.items():
            options.append(
                discord.SelectOption(
                    label=cat_name,
                    description=f"{len(stories)} قصة متاحة",
                    value=cat_name,
                    emoji="🕵️"
                )
            )
        super().__init__(
            placeholder="اختر تصنيف القصص الفردية...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="rpg_solo_category"
        )

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        # In a real persistence scenario we fetch the stories from DB/Manager here.
        # But for now, we pass them if they are stored or re-fetch them.
        stories = self.categories.get(category, [])
        if not stories:
            # Fallback to fetching from bot if persistence re-instantiated this empty
            bot = interaction.client
            all_stories = [s for s in bot.story_manager.get_all_stories().values() if s.game_mode == "single"]
            stories = [s for s in all_stories if s.theme == category]

        story_select = SoloStorySelect(category, stories)
        view = discord.ui.View(timeout=None)
        view.add_item(story_select)
        await interaction.response.edit_message(content=f"اختر قصة من تصنيف **{category}**:", view=view, embed=None)


class SoloCategorySelectView(discord.ui.View):
    def __init__(self, categories: dict):
        super().__init__(timeout=None)
        self.add_item(SoloCategorySelect(categories))


# --- World UI Logic --- #

class StartWorldStoryButton(discord.ui.Button):
    def __init__(self, story_id: int):
        super().__init__(
            label="ابدأ القصة",
            style=discord.ButtonStyle.success,
            custom_id=f"rpg_start_world_{story_id}"
        )
        self.story_id = story_id

    async def callback(self, interaction: discord.Interaction):
        from cogs.solo_cog import start_solo_interaction
        await start_solo_interaction(interaction, self.story_id)


class WorldStorySelect(discord.ui.Select):
    def __init__(self, world: str, category: str, stories: List[Story]):
        self.world = world
        self.category_name = category
        options = []
        for s in stories:
            options.append(
                discord.SelectOption(
                    label=s.title,
                    description=s.description[:50] + "...",
                    value=str(s.id),
                    emoji="📖"
                )
            )
        super().__init__(
            placeholder="اختر قصة لتبدأها...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=f"rpg_world_story_{world}_{category}"
        )

    async def callback(self, interaction: discord.Interaction):
        story_id = int(self.values[0])
        start_button = StartWorldStoryButton(story_id)
        view = discord.ui.View(timeout=None)
        view.add_item(start_button)
        await interaction.response.edit_message(content="القصة جاهزة. هل أنت مستعد؟", view=view, embed=None)


class WorldCategorySelect(discord.ui.Select):
    def __init__(self, categories: dict, world: str):
        self.categories = categories
        self.world = world
        options = []
        for cat_name, stories in self.categories.items():
            options.append(
                discord.SelectOption(
                    label=cat_name,
                    description=f"{len(stories)} قصة متاحة",
                    value=cat_name,
                    emoji="📁"
                )
            )
        super().__init__(
            placeholder="اختر تصنيف القصة...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=f"rpg_world_category_{world}"
        )

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        stories = self.categories.get(category, [])
        if not stories:
             # Fallback fetch
             bot = interaction.client
             all_stories = [s for s in bot.story_manager.get_all_stories().values() if getattr(s, 'world_type', self.world) == self.world]
             stories = [s for s in all_stories if s.theme == category]

        story_select = WorldStorySelect(self.world, category, stories)
        view = discord.ui.View(timeout=None)
        view.add_item(story_select)
        await interaction.response.edit_message(content=f"اختر قصة من تصنيف **{category}**:", view=view, embed=None)


class WorldCategorySelectView(discord.ui.View):
    def __init__(self, categories: dict, world: str):
        super().__init__(timeout=None)
        self.add_item(WorldCategorySelect(categories, world))
