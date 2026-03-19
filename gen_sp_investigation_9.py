import json
import os

def generate_story():
    story = {
        "id": 109,
        "title": "جريمة في الظلال: المرايا المحطمة",
        "theme": "التحقيق الجنائي (عقول إجرامية)",
        "series": 9,
        "game_mode": "single",
        "description": "أنت الطبيب النفسي الجنائي 'هشام'. الجريمة: تم العثور على جثة فتاة في مصنع مهجور. المشتبه به الوحيد هو 'آدم'، شخص يعاني من اضطراب الهوية الانفصالية (تعدد الشخصيات). داخل رأس آدم تعيش ثلاث شخصيات: (آدم: الضعيف والخائف)، (صخر: الغاضب والمدافع)، و(الحكيم: المتلاعب والبارد). هدفك: استخدام الكلمات المناسبة لاستدعاء الشخصية المناسبة في الوقت المناسب لجمع أجزاء الحقيقة. (النقاط هنا تمثل 'السيطرة النفسية' على الجلسة).",
        "start_scene": "scene_01_session",
        "image_url": "https://images.unsplash.com/photo-1510525009512-ad7fc13eefab?q=80&w=600&auto=format&fit=crop",
        "scenes": [
            {
                "id": "scene_01_session",
                "title": "الجلسة الأولى",
                "text": "الغرفة مبطنة باللون الأبيض. يجلس 'آدم' مقيداً بقميص المجانين. عيناه ترتجفان وينظر للأرض بخوف. 'أنا... أنا لم أفعل شيئاً. استيقظت ووجدت الدماء على يدي. أقسم لك يا دكتور.' جسده يرتعد بشدة. لكي تعرف ما حدث في المصنع، يجب أن تتحدث مع الشخصية التي تولت القيادة تلك الليلة. كيف تبدأ؟",
                "image_url": "https://images.unsplash.com/photo-1509822926718-f09c6ebf24af?q=80&w=600&auto=format&fit=crop",
                "choices": [
                    {
                        "text": "[تهدئة آدم] 'أنا أصدقك يا آدم. لكن يجب أن تساعدني لأساعدك. من كان معك؟'",
                        "next_scene": "scene_02_adam",
                        "color": "primary",
                        "points_reward": 5
                    },
                    {
                        "text": "[استفزاز المدافع] 'أنت ضعيف ومثير للشفقة! من كان يحميك تلك الليلة؟ أظهر نفسك!'",
                        "next_scene": "scene_03_sakhr",
                        "color": "danger",
                        "points_reward": 10
                    },
                    {
                        "text": "[استدعاء المتلاعب] 'أعرف أن هناك من يراقبني من الداخل الآن. أريد التحدث مع العقل المدبر.'",
                        "next_scene": "scene_04_hakeem",
                        "color": "secondary",
                        "points_reward": 5
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_02_adam",
                "title": "ذاكرة آدم",
                "text": "يبكي آدم. 'لا أتذكر! كل ما أذكره هو أنني كنت أمشي في الشارع، ثم رأيت... رأيت رجلاً يلحق بالفتاة. شعرت بالرعب، ثم أظلم كل شيء.' آدم لا يملك تفاصيل الجريمة لأنه (نام) في تلك اللحظة.",
                "choices": [
                    {
                        "text": "الضغط عليه بشدة ليتذكر المزيد.",
                        "next_scene": "scene_03_sakhr",
                        "color": "danger",
                        "points_reward": 5
                    },
                    {
                        "text": "سؤاله بلطف: 'من تولى القيادة عندما أظلمت الرؤية؟'",
                        "next_scene": "scene_05_transition",
                        "color": "primary",
                        "points_reward": 5
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_03_sakhr",
                "title": "ظهور (صخر)",
                "text": "فجأة، تتغير ملامح وجهه. تتصلب عضلاته ويصرخ بصوت خشن: 'لا تصرخ عليه أيها الطبيب الأحمق! أنا (صخر)، وأنا من يحمي هذا الجسد الضعيف. ذلك الرجل في الشارع كان يحمل سكيناً، فاضطررت للتدخل لحماية آدم.'",
                "choices": [
                    {
                        "text": "'هل أنت من قتل الفتاة إذن بحجة الحماية؟'",
                        "next_scene": "scene_06_sakhr_anger",
                        "color": "danger",
                        "points_reward": -10
                    },
                    {
                        "text": "'كيف حميته يا صخر؟ ماذا فعلت بالرجل ذو السكين؟'",
                        "next_scene": "scene_06_sakhr_fight",
                        "color": "primary",
                        "points_reward": 10
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_04_hakeem",
                "title": "ظهور (الحكيم)",
                "text": "يهدأ جسد آدم تماماً. يرفع رأسه ببطء، وتظهر على شفتيه ابتسامة متعجرفة وباردة. 'دكتور هشام. يسعدني أنك تتمتع بالذكاء الكافي لتتجاوز الدمى. أنا (الحكيم). الجريمة في المصنع كانت لوحة فنية، أليس كذلك؟ لكننا لم نرسمها.'",
                "choices": [
                    {
                        "text": "'إذا لم تكونوا أنتم، فمن فعلها؟'",
                        "next_scene": "scene_07_hakeem_game",
                        "color": "primary",
                        "points_reward": 5
                    },
                    {
                        "text": "'أنت تكذب لتبعد الشبهات. أنت العقل المدبر للقتل.'",
                        "next_scene": "scene_fail_hakeem_lock",
                        "color": "danger",
                        "points_reward": -15
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_05_transition",
                "title": "صراع داخلي",
                "text": "يصرخ آدم ممسكاً برأسه: 'لا! إنه غاضب! يريد الخروج!' يبدأ آدم بضرب رأسه بالطاولة.",
                "choices": [
                    {
                        "text": "تثبيته بالقوة وإعطاؤه مهدئاً خفيفاً.",
                        "next_scene": "scene_01_session",
                        "color": "secondary",
                        "points_reward": -5
                    },
                    {
                        "text": "تركه يواجه الصراع. 'دعه يخرج يا آدم! أنا مستعد.'",
                        "next_scene": "scene_03_sakhr",
                        "color": "primary",
                        "points_reward": 10
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_06_sakhr_anger",
                "title": "غضب صخر",
                "text": "يضرب (صخر) الطاولة بقوة كادت تكسر قيوده. 'أنا لا أقتل الأبرياء! أنا أقتل من يحاول إيذاءنا! أنت لا تفهم شيئاً!' يعود آدم للبكاء مجدداً بعد أن استنفذ صخر طاقته. لقد فقدت فرصة استجوابه.",
                "choices": [
                    {
                        "text": "محاولة استدعاء الحكيم الآن.",
                        "next_scene": "scene_04_hakeem",
                        "color": "primary",
                        "points_reward": 0
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_06_sakhr_fight",
                "title": "ذاكرة المعركة",
                "text": "يقول صخر بفخر: 'ضربت الرجل حتى فقد الوعي. أخذت السكين منه لكي لا يؤذينا. ثم أخذت الفتاة لنختبئ في المصنع القديم بعيداً عن الشارع. لكني كنت أنزف من ذراعي، ففقدت الوعي أيضاً.'",
                "choices": [
                    {
                        "text": "'إذا كنت فاقداً للوعي، فكيف قُتلت الفتاة في المصنع؟'",
                        "next_scene": "scene_08_who_killed",
                        "color": "primary",
                        "points_reward": 10
                    },
                    {
                        "text": "'أنت تكذب! السكين وُجدت بجانبها وعليها بصماتكم!'",
                        "next_scene": "scene_06_sakhr_anger",
                        "color": "danger",
                        "points_reward": -10
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_07_hakeem_game",
                "title": "لعبة الحكيم",
                "text": "'الحكيم' يميل برأسه. 'سأعطيك تلميحاً يا دكتور. (صخر) يظن أنه البطل، لكنه غبي. هو أحضر الفتاة للمصنع لتخبئتها، لكنه لم يلاحظ أن الرجل الذي ضربه... لم يكن وحده.'",
                "choices": [
                    {
                        "text": "'تقصد أن هناك قاتل آخر تبعهما للمصنع؟'",
                        "next_scene": "scene_09_the_second_killer",
                        "color": "primary",
                        "points_reward": 10
                    },
                    {
                        "text": "'لماذا لم تحذر (صخر) إذن بما أنك العقل المدبر؟'",
                        "next_scene": "scene_10_hakeem_ego",
                        "color": "secondary",
                        "points_reward": 5
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_08_who_killed",
                "title": "السؤال الحاسم",
                "text": "يرتبك صخر لأول مرة. 'لا أعلم... عندما أغمي عليّ بسبب النزيف، لا بد أن (الحكيم) هو من استيقظ. اسأله هو! هو الماكر بيننا!' يغلق عينيه ويأخذ نفساً عميقاً.",
                "choices": [
                    {
                        "text": "استدعاء الحكيم لمعرفة ماذا حدث في المصنع.",
                        "next_scene": "scene_04_hakeem",
                        "color": "primary",
                        "points_reward": 5
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_09_the_second_killer",
                "title": "الشريك الخفي",
                "text": "'بالضبط.' يبتسم الحكيم. 'صخر أغمي عليه، فاستيقظت أنا. رأيت رجلاً طويلاً يرتدي معطفاً جلدياً يدخل المصنع. كان يبحث عن الفتاة. اختبأت أنا في الظلام لأننا كنا ننزف وبلا سلاح. الرجل قتلها ببرود، ثم وضع السكين في يدنا ليلفق لنا التهمة.'",
                "choices": [
                    {
                        "text": "'هل رأيت وجهه؟ هل ترك أي دليل خلفه؟'",
                        "next_scene": "scene_11_the_evidence",
                        "color": "primary",
                        "points_reward": 10
                    },
                    {
                        "text": "'هذه قصة خيالية لتبرئة أنفسكم.'",
                        "next_scene": "scene_fail_hakeem_lock",
                        "color": "danger",
                        "points_reward": -20
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_10_hakeem_ego",
                "title": "غرور المتلاعب",
                "text": "'لا يمكننا التحدث مع بعضنا البعض في نفس الوقت يا دكتور. عندما يسيطر صخر، أكون أنا مراقباً صامتاً. وعندما أغمي عليه، أخذت أنا القيادة لإنقاذ الجسد.'",
                "choices": [
                    {
                        "text": "العودة للتركيز على الجريمة: 'ماذا حدث عندما أخذت القيادة؟'",
                        "next_scene": "scene_09_the_second_killer",
                        "color": "primary",
                        "points_reward": 5
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_11_the_evidence",
                "title": "دليل الحكيم",
                "text": "'لم أرَ وجهه بسبب الظلام.' يقول الحكيم. 'لكنني لست غبياً. عندما انحنى لوضع السكين في يدنا، سرقت شيئاً من جيبه دون أن يلاحظ، وخبأته في المصنع قبل أن تأتي الشرطة وتعتقل (آدم) الباكي.'",
                "choices": [
                    {
                        "text": "'ما هو هذا الشيء؟ وأين خبأته؟' (يتطلب 25 نقطة سيطرة)",
                        "required_points": 25,
                        "next_scene": "scene_12_the_location",
                        "color": "success",
                        "points_reward": 15
                    },
                    {
                        "text": "'أنت تكذب! لم تجد الشرطة أي شيء غريب في المصنع.'",
                        "next_scene": "scene_fail_hakeem_lock",
                        "color": "danger",
                        "points_reward": 0
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_12_the_location",
                "title": "الخريطة الذهنية",
                "text": "يقترب الحكيم ويهمس: 'خلف خزان المياه الصدئ في الطابق الثاني. هناك ولاعة معدنية محفور عليها اسم نادي ليلي (القمر الأحمر). القاتل الحقيقي يعمل هناك كحارس شخصي.'",
                "choices": [
                    {
                        "text": "إرسال فريق فوراً للمصنع للبحث.",
                        "next_scene": "scene_13_police_dispatch",
                        "color": "primary",
                        "points_reward": 10
                    },
                    {
                        "text": "الذهاب بنفسك للتحقق دون إخبار الشرطة.",
                        "next_scene": "scene_fail_lone_wolf",
                        "color": "danger",
                        "points_reward": -10
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_13_police_dispatch",
                "title": "العدالة الخفية",
                "text": "يتصل بك المفتش بعد ساعة: 'لقد وجدنا الولاعة! عليها بصمات مطابقة لقاتل مأجور معروف يعمل في ذلك النادي. تم إلقاء القبض عليه، وقد اعترف بأنها كانت عملية تصفية.'",
                "choices": [
                    {
                        "text": "إبلاغ آدم بخبر براءته.",
                        "next_scene": "scene_win_perfect",
                        "color": "success",
                        "points_reward": 10
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_fail_hakeem_lock",
                "title": "النهاية: عقل مغلق",
                "text": "اتهامك للحكيم بالكذب جعله يغلق عقله تماماً. 'أنت لا تستحق عبقريتي.' انسحب الحكيم وعاد آدم للبكاء. لم تتمكن من استخراج الدليل، وتم إعدام آدم بجريمة لم يرتكبها. (لقد خسرت).",
                "choices": [],
                "is_ending": True
            },
            {
                "id": "scene_fail_lone_wolf",
                "title": "النهاية: فخ القاتل",
                "text": "ذهبت للمصنع بمفردك. القاتل كان يراقب المكان ليتأكد من عدم وجود أدلة ضده. بمجرد أن وجدت الولاعة، تلقيت رصاصة في ظهرك. (لقد خسرت حياتك).",
                "choices": [],
                "is_ending": True
            },
            {
                "id": "scene_win_perfect",
                "title": "النهاية: العقل المنتصر",
                "text": "تدخل الغرفة وتخبر آدم أنه بريء. يعود صخر ليقول 'شكراً لك'، ثم يبتسم الحكيم ابتسامة خفيفة ويقول 'عمل جيد يا دكتور'. لقد استطعت التنقل بين الشخصيات المعقدة واستخراج الحقيقة، وأنقذت مريضاً من حبل المشنقة. (فوز مثالي ومذهل).",
                "choices": [],
                "is_ending": True
            }
        ]
    }

    os.makedirs("data/stories", exist_ok=True)
    with open("data/stories/sp_investigation_9.json", "w", encoding="utf-8") as f:
        json.dump(story, f, ensure_ascii=False, indent=4)
    print("Story 9 generated successfully!")

if __name__ == "__main__":
    generate_story()
