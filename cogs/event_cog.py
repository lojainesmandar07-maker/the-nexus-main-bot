import discord
from discord import app_commands
from discord.ext import commands
from core.bot import StoryBot
from core.category_catalog import EVENT_CATEGORIES

class EventCog(commands.Cog):
    def __init__(self, bot: StoryBot):
        self.bot = bot

    async def multi_story_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        stories = self.bot.story_manager.get_stories_by_mode("multi").values()
        needle = (current or "").strip().casefold()
        out: list[app_commands.Choice[str]] = []
        for story in stories:
            sid = str(story.id)
            label = f"{story.title} ({sid})"
            if needle and needle not in label.casefold():
                continue
            out.append(app_commands.Choice(name=label[:100], value=sid))
            if len(out) >= 25:
                break
        return out

    @app_commands.command(name="حدث", description="بدء حدث قصة تفاعلي جديد")
    @app_commands.describe(story_ref="اسم القصة الجماعية أو معرّفها")
    @app_commands.describe(round_seconds="مدة التصويت لكل جولة بالثواني (افتراضي: 30)")
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.autocomplete(story_ref=multi_story_autocomplete)
    async def start_event(self, interaction: discord.Interaction, story_ref: str, round_seconds: app_commands.Range[int, 15, 120] = 30):

        # Defer the response so we can send initial messages correctly
        await interaction.response.defer()

        if self.bot.event_manager.active_event:
            await interaction.followup.send("❌ حدث تفاعلي جارٍ بالفعل. يرجى إيقافه أولاً.", ephemeral=True)
            return

        story = self.bot.story_manager.resolve_story(story_ref, game_mode="multi")
        if not story:
            multi_stories = self.bot.story_manager.get_stories_by_mode("multi")
            available_stories = ", ".join([str(sid) for sid in multi_stories.keys()])
            await interaction.followup.send(f"❌ لم يتم العثور على قصة مطابقة لـ `{story_ref}`.\nالقصص الجماعية المتاحة: {available_stories}", ephemeral=True)
            return

        if story.game_mode != "multi":
            await interaction.followup.send(f"❌ القصة المختارة ليست مخصصة للعب الجماعي. استخدم أمر `/لعب_فردي`.", ephemeral=True)
            return

        await interaction.followup.send(
            f"✅ جاري تحضير الحدث: {story.title}...\n"
            f"⏱️ زمن التصويت لكل جولة: {round_seconds} ثانية."
        )

        # Start the event in the channel where the command was used
        self.bot.loop.create_task(
            self.bot.event_manager.start_event(interaction.channel, story.id, voting_timeout=float(round_seconds))
        )

    @app_commands.command(name="إيقاف", description="إيقاف الحدث التفاعلي الحالي")
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.checks.has_permissions(manage_guild=True)
    async def stop_event(self, interaction: discord.Interaction):
        await interaction.response.defer()

        if not self.bot.event_manager.active_event:
            await interaction.followup.send("❌ لا يوجد حدث تفاعلي جارٍ حالياً.", ephemeral=True)
            return

        await self.bot.event_manager.stop_event(interaction.channel)
        await interaction.followup.send("✅ تم إصدار أمر إيقاف الحدث.", ephemeral=True)

    @app_commands.command(name="قصص_جماعية", description="عرض القصص المخصصة للفعاليات الجماعية")
    async def list_multi_stories(self, interaction: discord.Interaction):
        stories = self.bot.story_manager.get_stories_by_mode("multi")
        if not stories:
            await interaction.response.send_message("❌ لا توجد قصص جماعية متاحة حالياً.", ephemeral=True)
            return

        from collections import defaultdict
        categories = defaultdict(list)
        for s in stories.values():
            categories[s.theme].append(s)

        from ui.listing_view import MultiLibraryView
        view = MultiLibraryView(categories)
        embed = view.render_embed()

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="تصنيفات_جماعية", description="عرض قائمة التصنيفات المقترحة للفعاليات الجماعية")
    async def list_multi_categories(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🗂️ تصنيفات الفعاليات الجماعية",
            description="هذه التصنيفات تساعدكم على تنظيم قصص الأحداث وصناعة تصويتات أكثر تنوعاً.",
            color=discord.Color.dark_blue(),
        )

        for index, category in enumerate(EVENT_CATEGORIES, start=1):
            embed.add_field(
                name=f"{index}. {category.name}",
                value=category.description,
                inline=False,
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: StoryBot):
    await bot.add_cog(EventCog(bot))
