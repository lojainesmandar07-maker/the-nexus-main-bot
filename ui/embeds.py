import discord
from engine.models import Story, Scene

class EmbedBuilder:
    @staticmethod
    def world_select_embed() -> discord.Embed:
        embed = discord.Embed(
            title="🌍 مستكشف العوالم",
            description="اختر العالم الذي تود استكشاف قصصه من القائمة أدناه. كل عالم يحتوي على تصنيفات وقصص فريدة لتستمتع بها.",
            color=discord.Color.blurple()
        )
        embed.set_footer(text="استخدم القائمة المنسدلة لاختيار العالم")
        return embed

    @staticmethod
    def story_preview_embed(story: Story) -> discord.Embed:
        embed = discord.Embed(
            title=f"📖 {story.title}",
            description=story.description or "لا يوجد وصف لهذه القصة.",
            color=discord.Color.green()
        )
        embed.add_field(name="التصنيف", value=story.theme, inline=True)
        if hasattr(story, 'world_type') and story.world_type:
            embed.add_field(name="العالم", value=story.world_type, inline=True)
        if story.image_url:
            embed.set_thumbnail(url=story.image_url)
        return embed

    @staticmethod
    def category_browser_embed(world_type: str, world_name: str, desc: str) -> discord.Embed:
        embed = discord.Embed(
            title=f"📁 تصنيفات: {world_name}",
            description=f"{desc}\n\nالرجاء اختيار تصنيف من القائمة أدناه لعرض القصص المتاحة فيه.",
            color=discord.Color.gold()
        )
        embed.set_footer(text="استخدم القائمة المنسدلة لاختيار التصنيف")
        return embed

    @staticmethod
    def help_embed() -> discord.Embed:
        embed = discord.Embed(
            title="❓ مساعدة - نظام القصص التفاعلية",
            description="مرحباً بك في بوت القصص التفاعلية! إليك كيف يمكنك البدء:",
            color=discord.Color.blue()
        )
        embed.add_field(name="`/ابدأ`", value="لفتح مستكشف العوالم واختيار قصة لتلعبها.", inline=False)
        embed.add_field(name="`/قصص_فردية`", value="لعرض قائمة بكل القصص الفردية.", inline=False)
        embed.add_field(name="كيف ألعب؟", value="اختر قصة، ثم اتبع الأحداث واضغط على الأزرار لاختيار قراراتك. ستحدد قراراتك مسار القصة ونهايتها!", inline=False)
        return embed

    @staticmethod
    def event_start_embed(story: Story) -> discord.Embed:
        embed = discord.Embed(
            title=f"📖 حدث قصة تفاعلي جديد: {story.title}",
            description=story.description,
            color=discord.Color.gold()
        )
        embed.add_field(name="التصنيف", value=story.theme, inline=True)
        if story.image_url:
            embed.set_thumbnail(url=story.image_url)
        embed.set_footer(text="سيتم عرض القصة والخيارات قريباً. استعدوا للتصويت!")
        return embed

    @staticmethod
    def solo_scene_embed(scene: Scene, round_number: int, story_title: str, points: int) -> discord.Embed:
        color = discord.Color.dark_theme() if scene.is_ending else discord.Color.purple()

        embed = discord.Embed(
            title=f"الجولة {round_number}: {scene.title}",
            description=scene.text,
            color=color
        )

        if scene.image_url:
            embed.set_image(url=scene.image_url)

        embed.set_author(name=f"{story_title} (لعب فردي)")
        embed.add_field(name="النقاط ⭐️", value=f"{points}", inline=False)

        if not scene.is_ending:
            embed.set_footer(text="اختر بحكمة، مصيرك يعتمد على قرارك...")
        else:
            embed.set_footer(text="نهاية القصة. شكراً للعبك!")

        return embed

    @staticmethod
    def scene_embed(scene: Scene, round_number: int, story_title: str, voting_seconds: int = 30) -> discord.Embed:
        color = discord.Color.dark_theme() if scene.is_ending else discord.Color.blue()

        embed = discord.Embed(
            title=f"الجولة {round_number}: {scene.title}",
            description=scene.text,
            color=color
        )

        if scene.image_url:
            embed.set_image(url=scene.image_url)

        embed.set_author(name=story_title)

        if not scene.is_ending:
            embed.set_footer(text=f"أمامكم {voting_seconds} ثانية للتصويت على الخيار القادم!")
        else:
            embed.set_footer(text="وصلنا إلى نهاية القصة. شكراً لمشاركتكم!")

        return embed

    @staticmethod
    def voting_result_embed(winning_choice_text: str, total_votes: int) -> discord.Embed:
        embed = discord.Embed(
            title="✅ انتهى التصويت!",
            description=f"**الخيار الفائز هو:** {winning_choice_text}\n(بإجمالي {total_votes} أصوات)",
            color=discord.Color.green()
        )
        return embed

    @staticmethod
    def tie_break_embed(winning_choice_text: str, total_votes: int) -> discord.Embed:
        embed = discord.Embed(
            title="⚖️ تعادل في الأصوات!",
            description=f"حدث تعادل. اختار النظام عشوائياً:\n**الخيار الفائز هو:** {winning_choice_text}\n(بإجمالي {total_votes} أصوات)",
            color=discord.Color.orange()
        )
        return embed

    @staticmethod
    def error_embed(message: str) -> discord.Embed:
        return discord.Embed(
            title="❌ خطأ",
            description=message,
            color=discord.Color.red()
        )

    @staticmethod
    def event_stopped_embed() -> discord.Embed:
        return discord.Embed(
            title="🛑 إيقاف الحدث",
            description="تم إيقاف الحدث التفاعلي من قبل الإدارة.",
            color=discord.Color.red()
        )
