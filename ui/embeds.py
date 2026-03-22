import discord
from engine.models import Story, Scene

class EmbedBuilder:
    WORLD_STYLES = {
        "fantasy": {"emoji": "👑", "color": 0xD4AF37, "label": "عالم الفانتازيا"},
        "past": {"emoji": "📜", "color": 0xA67C52, "label": "عالم الماضي"},
        "future": {"emoji": "🛸", "color": 0x00B7FF, "label": "عالم المستقبل"},
        "alternate": {"emoji": "🕳️", "color": 0x5C2D91, "label": "العالم البديل"},
        "solo": {"emoji": "🌓", "color": 0x2B2D42, "label": "القصص الفردية"},
    }

    @staticmethod
    def world_color(world_type: str | None, fallback: discord.Color | None = None) -> discord.Color:
        if world_type and world_type in EmbedBuilder.WORLD_STYLES:
            return discord.Color(EmbedBuilder.WORLD_STYLES[world_type]["color"])
        return fallback or discord.Color.blurple()

    @staticmethod
    def world_select_embed() -> discord.Embed:
        embed = discord.Embed(
            title="🌍 مستكشف العوالم",
            description=(
                "مرحباً بك في **The Nexus**.\n"
                "اختر العالم الذي ترغب بالدخول إليه، ثم حدّد التصنيف فالقصة لبدء التجربة."
            ),
            color=discord.Color.blurple(),
        )
        embed.add_field(
            name="🧭 خطوات سريعة",
            value="1) اختر العالم  •  2) اختر التصنيف  •  3) اختر القصة  •  4) ابدأ اللعب",
            inline=False,
        )
        embed.set_footer(text="استخدم القائمة المنسدلة أدناه، ويمكنك الرجوع خطوة للخلف في أي وقت.")
        return embed

    @staticmethod
    def story_preview_embed(story: Story) -> discord.Embed:
        world_type = getattr(story, "world_type", None)
        world_style = EmbedBuilder.WORLD_STYLES.get(world_type, {})
        embed = discord.Embed(
            title=f"📖 {story.title}",
            description=(story.description or "لا يوجد وصف لهذه القصة."),
            color=EmbedBuilder.world_color(world_type, discord.Color.green()),
        )
        embed.add_field(name="🏷️ التصنيف", value=story.theme, inline=True)
        if world_type:
            embed.add_field(
                name="🌐 العالم",
                value=f"{world_style.get('emoji', '🌍')} {world_style.get('label', world_type)}",
                inline=True,
            )
        embed.add_field(name="🎮 النمط", value="لعب فردي" if story.game_mode == "single" else "حدث جماعي", inline=True)
        if story.image_url:
            embed.set_thumbnail(url=story.image_url)
        embed.set_footer(text="إذا بدت القصة مناسبة لك، اضغط «ابدأ القصة الآن».")
        return embed

    @staticmethod
    def category_browser_embed(world_type: str, world_name: str, desc: str) -> discord.Embed:
        embed = discord.Embed(
            title=f"📁 تصنيفات: {world_name}",
            description=f"{desc}\n\nاختر التصنيف المناسب لتظهر لك القصص المتاحة مباشرة.",
            color=EmbedBuilder.world_color(world_type, discord.Color.gold()),
        )
        embed.set_footer(text="بعد اختيار التصنيف ستنتقل لمرحلة اختيار القصة.")
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

        embed.set_author(name=f"{story_title} • اللعب الفردي")
        embed.add_field(name="⭐ النقاط الحالية", value=f"{points}", inline=True)
        embed.add_field(name="🧭 الحالة", value="نهاية القصة" if scene.is_ending else "داخل القصة", inline=True)

        if not scene.is_ending:
            embed.set_footer(text="اختر خياراً واحداً للمتابعة. قراراتك تؤثر مباشرة على النهاية.")
        else:
            embed.set_footer(text="أتممت هذه الرحلة بنجاح. يمكنك الآن مشاركة النهاية أو بدء قصة جديدة.")

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
            description=f"**الخيار الفائز:** {winning_choice_text}",
            color=discord.Color.green(),
        )
        embed.add_field(name="🗳️ إجمالي الأصوات", value=str(total_votes), inline=True)
        embed.set_footer(text="جارٍ الانتقال إلى المشهد التالي...")
        return embed

    @staticmethod
    def tie_break_embed(winning_choice_text: str, total_votes: int) -> discord.Embed:
        embed = discord.Embed(
            title="⚖️ تعادل في الأصوات!",
            description=f"حدث تعادل، فاختار النظام عشوائياً:\n**الخيار الفائز:** {winning_choice_text}",
            color=discord.Color.orange(),
        )
        embed.add_field(name="🗳️ إجمالي الأصوات", value=str(total_votes), inline=True)
        embed.set_footer(text="يمكنكم تغيير النتيجة في الجولة القادمة عبر التصويت الجماعي.")
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
