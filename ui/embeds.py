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
    WORLD_EXPLANATIONS = {
        "fantasy": {
            "title": "👑 عالم الفانتازيا — ممالك السحر والعهود",
            "identity": (
                "هنا تُحكم الممالك بالسيوف القديمة والمواثيق المنسية، وتتحرّك "
                "قوى السحر بين البلاط والخرائب. هذا العالم يوازن بين المجد والنبوءة."
            ),
            "expect": (
                "• قصص ملوك وفرسان وسحرة.\n"
                "• صراعات ولاء وخيانة ومصير.\n"
                "• رحلات أسطورية، آثار نادرة، واختبارات شجاعة."
            ),
            "begin": (
                "1) استخدم `/ابدأ` ثم اختر **عالم الفانتازيا**.\n"
                "2) حدّد التصنيف الذي يلائم ذوقك.\n"
                "3) اختر القصة وابدأ اتخاذ قراراتك."
            ),
            "footer": "بوابتك الأولى: اختر قصة فانتازية واسمح لقرار واحد أن يغيّر المملكة.",
        },
        "past": {
            "title": "📜 عالم الماضي — زمن الأصالة والأثر",
            "identity": (
                "في هذا العالم تنبض الحكاية بروح التاريخ: أسواق عتيقة، مدن قديمة، "
                "وشخصيات تصنع أمجادها بذكاء وحكمة وصبر."
            ),
            "expect": (
                "• قصص اجتماعية وتاريخية بنَفَس عربي أصيل.\n"
                "• تفاصيل حياة يومية ممزوجة بالتحدّي والكرامة.\n"
                "• اختيارات أخلاقية تُشكّل السمعة والإرث."
            ),
            "begin": (
                "1) نفّذ `/ابدأ` واختر **عالم الماضي**.\n"
                "2) تصفّح التصنيفات حسب المزاج والحدث.\n"
                "3) ابدأ القصة وتابع أثر اختياراتك حتى النهاية."
            ),
            "footer": "كل قرار هنا يترك أثراً... فاختر ما يليق باسمك في دفاتر الزمن.",
        },
        "future": {
            "title": "🛸 عالم المستقبل — مدن الضوء والقرارات الحاسمة",
            "identity": (
                "عالم متسارع تُدار فيه الحياة بالخوارزميات والتحالفات التقنية. "
                "الابتكار قوة، لكن الثمن غالباً أكبر مما يبدو."
            ),
            "expect": (
                "• قصص خيال علمي، مدن ذكية، ومهام عالية المخاطر.\n"
                "• منافسة بين العقل البشري والأنظمة الذكية.\n"
                "• نهايات تتبدّل بدقة بناءً على قراراتك."
            ),
            "begin": (
                "1) اكتب `/ابدأ` واختر **عالم المستقبل**.\n"
                "2) اختر تصنيفاً (تشويق/استكشاف/صراع).\n"
                "3) ابدأ اللعب ووازن بين السرعة والدقة."
            ),
            "footer": "في المستقبل لا يفوز الأقوى فقط... بل من يقرأ العواقب قبل الجميع.",
        },
        "alternate": {
            "title": "🕳️ العالم البديل — واقع يتشقق بين الاحتمالات",
            "identity": (
                "هنا تتقاطع الأزمنة والنسخ المتعددة للحقيقة. ما تعرفه عن الواقع "
                "ليس ثابتاً، وكل باب قد يقودك إلى نسخة مختلفة من المصير."
            ),
            "expect": (
                "• قصص غموض نفسي ومفاجآت غير متوقعة.\n"
                "• مفارقات زمنية وقرارات بوجوه متعدّدة.\n"
                "• تجارب سردية عميقة لعشّاق التعقيد."
            ),
            "begin": (
                "1) افتح `/ابدأ` وحدد **العالم البديل**.\n"
                "2) اختر التصنيف الأقرب لأسلوبك.\n"
                "3) خض القصة بتركيز؛ التفاصيل الصغيرة تصنع الفرق."
            ),
            "footer": "إن شعرت أن الواقع تغيّر فجأة... فأنت على المسار الصحيح.",
        },
    }
    HELP_TOPICS = {
        "getting_started": {
            "title": "🚀 كيف تبدأ بسرعة؟",
            "description": "إذا كنت جديداً، هذا المسار المختصر يوصلك لأول تجربة ممتعة خلال دقيقة.",
            "do": (
                "1) ابدأ بـ `/اختبار_الشخصية` لفهم أسلوبك.\n"
                "2) انتقل إلى `/ابدأ` واختر العالم الذي يناسب مزاجك.\n"
                "3) جرّب قصة قصيرة أولاً ثم وسّع مغامرتك."
            ),
            "commands": "`/اختبار_الشخصية` • `/ابدأ` • `/قصص_فردية`",
            "footer": "نصيحة: لا تفكّر كثيراً في البداية — ابدأ واترك القصة تقودك.",
            "color": 0x5865F2,
        },
        "world_stories": {
            "title": "🌍 القصص العالمية",
            "description": "هذه تجربة الاستكشاف الأساسية: تختار عالماً ثم تصنيفاً ثم قصة.",
            "do": (
                "• استخدم `/ابدأ` لفتح مستكشف العوالم.\n"
                "• اختر: الفانتازيا / الماضي / المستقبل / العالم البديل.\n"
                "• داخل كل عالم ستجد قصصاً بنكهة مختلفة."
            ),
            "commands": "`/ابدأ`",
            "footer": "جرّب أكثر من عالم لتكتشف أي أسلوب يناسب قراراتك.",
            "color": 0x00B7FF,
        },
        "solo_stories": {
            "title": "🌓 القصص الفردية",
            "description": "رحلة شخصية كاملة: كل اختيار منك يغيّر المسار والنهاية.",
            "do": (
                "• افتح مكتبة القصص عبر `/قصص_فردية`.\n"
                "• أو ابدأ مباشرة برقم قصة عبر `/لعب_فردي`.\n"
                "• تابع الأزرار داخل المشهد واختر قرارك في كل جولة."
            ),
            "commands": "`/قصص_فردية` • `/لعب_فردي`",
            "footer": "السر في القصص الفردية: جرّب مسارات مختلفة ولا تكتفِ بنهاية واحدة.",
            "color": 0x2B2D42,
        },
        "personality_test": {
            "title": "🧠 اختبار الشخصية",
            "description": "اختبار سريع يحدد نمطك داخل عالم The Nexus ويمنحك هوية أوضح.",
            "do": (
                "• ابدأ الاختبار عبر `/اختبار_الشخصية`.\n"
                "• أجب بصدق لتحصل على نتيجة أدق.\n"
                "• استخدم النتيجة كدليل عند اختيار القصص والتحديات."
            ),
            "commands": "`/اختبار_الشخصية`",
            "footer": "ابدأ منه إذا كنت محتاراً: سيختصر عليك اختيار الاتجاه المناسب.",
            "color": 0x9B59B6,
        },
        "npcs": {
            "title": "🧩 الشخصيات NPCs",
            "description": "تفاعل مع شخصيات العوالم للحصول على لحظات حوارية ومفاجآت ممتعة.",
            "do": (
                "• استخدم `/شخصيات` ثم اختر العالم.\n"
                "• تابع الرسائل التفاعلية لتستكشف ردود كل شخصية.\n"
                "• جرّب أكثر من شخصية لتحصل على تجارب مختلفة."
            ),
            "commands": "`/شخصيات`",
            "footer": "كل عالم لديه شخصيات بطابع مختلف — اختر بحسب مزاجك.",
            "color": 0xF39C12,
        },
        "profile_titles": {
            "title": "🏅 البروفايل والألقاب",
            "description": "صفحتك الشخصية تعرض تقدّمك وهويتك داخل المجتمع.",
            "do": (
                "• اعرض ملفك عبر `/بروفايل`.\n"
                "• أكمل قصصاً وتحديات لرفع حضورك داخل السيرفر.\n"
                "• تابع لقبك وتقدمك بشكل دوري."
            ),
            "commands": "`/بروفايل` • `/لوحة_الشرف`",
            "footer": "تقدّمك يتراكم بمرور الوقت — العودة اليومية تصنع فرقاً واضحاً.",
            "color": 0xF1C40F,
        },
        "community_loop": {
            "title": "📆 التحديات والنبضة والقرارات",
            "description": "هذا القسم يصنع النشاط الجماعي اليومي والأسبوعي داخل السيرفر.",
            "do": (
                "• تابع تحدي الأسبوع عبر `/تحدي_الأسبوع` وإنجازك عبر `/إنجازاتي`.\n"
                "• شارك في نبضة اليوم داخل قناة النبض.\n"
                "• صوّت في القرار الجماعي عبر `/قرار_اجتماعي`."
            ),
            "commands": "`/تحدي_الأسبوع` • `/إنجازاتي` • `/قرار_اجتماعي`",
            "footer": "لأفضل تجربة: افتح هذا القسم يومياً لدقيقة واحدة على الأقل.",
            "color": 0x1ABC9C,
        },
        "admin_tools": {
            "title": "🛡️ أدوات الإدارة (للمشرفين)",
            "description": "هذه الأوامر مخصصة لإدارة السيرفر وتشغيل الأنظمة العامة.",
            "do": (
                "• إعداد القنوات والأنظمة عبر `/إعداد_النيكسوس`.\n"
                "• تشغيل أحداث جماعية ونشر محتوى رسمي عند الحاجة.\n"
                "• إدارة القرارات والنبض والتحديات بصلاحيات الإدارة."
            ),
            "commands": "`/إعداد_النيكسوس` • `/حدث` • `/نبضة_اليوم` • `/إنشاء_تحدي`",
            "footer": "إذا لم تكن مشرفاً، يمكنك تجاهل هذا القسم والتركيز على التجربة اللعبية.",
            "color": 0xE74C3C,
        },
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
                "اختر العالم الذي ترغب بالدخول إليه، ثم حدّد التصنيف فالقصة لبدء التجربة.\n\n"
                "✨ إن كانت هذه زيارتك الأولى: ابدأ من `/اختبار_الشخصية` ثم عُد إلى `/ابدأ`."
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
    def world_explanation_embed(world_type: str) -> discord.Embed:
        data = EmbedBuilder.WORLD_EXPLANATIONS.get(world_type)
        style = EmbedBuilder.WORLD_STYLES.get(world_type, {})

        if not data:
            return discord.Embed(
                title="❌ عالم غير مدعوم",
                description="لا يوجد شرح متاح لهذا العالم حالياً.",
                color=discord.Color.red(),
            )

        embed = discord.Embed(
            title=data["title"],
            description=data["identity"],
            color=discord.Color(style.get("color", 0x5865F2)),
        )
        embed.add_field(name="🧬 هوية العالم", value=data["identity"], inline=False)
        embed.add_field(name="🎭 ماذا ستجد هنا؟", value=data["expect"], inline=False)
        embed.add_field(name="🚀 كيف تبدأ؟", value=data["begin"], inline=False)
        embed.set_footer(text=data["footer"])
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
            title="🧭 مركز المساعدة — The Nexus",
            description=(
                "مرحباً بك! اختر من الأزرار بالأسفل لتنتقل مباشرة إلى الشرح الذي تحتاجه.\n"
                "الشروحات قصيرة وواضحة لتناسب الجوال والكمبيوتر."
            ),
            color=discord.Color.blurple(),
        )
        embed.add_field(
            name="✨ ماذا ستجد هنا؟",
            value=(
                "• كيف تبدأ من الصفر\n"
                "• شرح القصص العالمية والفردية\n"
                "• اختبار الشخصية وملفك وتقدمك\n"
                "• أدوات المجتمع والإدارة"
            ),
            inline=False,
        )
        embed.add_field(
            name="🎯 البداية المقترحة",
            value="ابدأ بـ `/اختبار_الشخصية` ثم استخدم `/ابدأ` لاختيار أول قصة.",
            inline=False,
        )
        embed.set_footer(text="اضغط أي زر للتفاصيل • يمكنك الرجوع للقائمة الرئيسية في أي وقت.")
        return embed

    @staticmethod
    def help_topic_embed(topic_key: str) -> discord.Embed:
        topic = EmbedBuilder.HELP_TOPICS.get(topic_key)
        if not topic:
            return discord.Embed(
                title="❌ القسم غير متاح",
                description="هذا القسم غير موجود حالياً. ارجع إلى القائمة الرئيسية.",
                color=discord.Color.red(),
            )

        embed = discord.Embed(
            title=topic["title"],
            description=topic["description"],
            color=discord.Color(topic["color"]),
        )
        embed.add_field(name="✅ ماذا يمكنك أن تفعل؟", value=topic["do"], inline=False)
        embed.add_field(name="⌨️ أوامر مفيدة", value=topic["commands"], inline=False)
        embed.set_footer(text=topic["footer"])
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