import discord
from discord import app_commands
from discord.ext import commands

from core.bot import StoryBot
from ui.embeds import EmbedBuilder


class HelpTopicButton(discord.ui.Button):
    def __init__(self, topic_key: str, label: str, emoji: str):
        super().__init__(
            label=label,
            emoji=emoji,
            style=discord.ButtonStyle.secondary,
            custom_id=f"help_topic_{topic_key}",
        )
        self.topic_key = topic_key

    async def callback(self, interaction: discord.Interaction):
        view: HelpCenterView = self.view
        embed = EmbedBuilder.help_topic_embed(self.topic_key)
        await interaction.response.edit_message(embed=embed, view=view.details_view())


class HelpBackButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="رجوع للقائمة الرئيسية",
            emoji="↩️",
            style=discord.ButtonStyle.primary,
            custom_id="help_back_main",
        )

    async def callback(self, interaction: discord.Interaction):
        view: HelpCenterView = self.view
        await interaction.response.edit_message(embed=EmbedBuilder.help_embed(), view=view.main_view())


class HelpCenterView(discord.ui.View):
    TOPICS = [
        ("getting_started", "كيف أبدأ؟", "🚀"),
        ("world_stories", "القصص العالمية", "🌍"),
        ("solo_stories", "القصص الفردية", "🌓"),
        ("personality_test", "اختبار الشخصية", "🧠"),
        ("npcs", "الشخصيات NPCs", "🧩"),
        ("profile_titles", "البروفايل والألقاب", "🏅"),
        ("community_loop", "التحديات والنبض والقرارات", "📆"),
        ("admin_tools", "أدوات الإدارة", "🛡️"),
    ]

    def __init__(self, timeout: float = 240):
        super().__init__(timeout=timeout)
        self.message: discord.Message | None = None
        self._show_main_buttons()

    def _show_main_buttons(self):
        self.clear_items()
        for topic_key, label, emoji in self.TOPICS:
            self.add_item(HelpTopicButton(topic_key=topic_key, label=label, emoji=emoji))

    def main_view(self) -> "HelpCenterView":
        self._show_main_buttons()
        return self

    def details_view(self) -> "HelpCenterView":
        self.clear_items()
        self.add_item(HelpBackButton())
        return self

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except Exception:
                pass


class HelpCog(commands.Cog):
    def __init__(self, bot: StoryBot):
        self.bot = bot

    @app_commands.command(name="مساعدة", description="مركز المساعدة التفاعلي في The Nexus")
    async def help_center(self, interaction: discord.Interaction):
        view = HelpCenterView()
        await interaction.response.send_message(embed=EmbedBuilder.help_embed(), view=view, ephemeral=True)
        try:
            view.message = await interaction.original_response()
        except Exception:
            pass


async def setup(bot: StoryBot):
    await bot.add_cog(HelpCog(bot))
