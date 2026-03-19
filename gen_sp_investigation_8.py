import json
import os

def generate_story():
    story = {
        "id": 108,
        "title": "جريمة في الظلال: الدائرة المغلقة",
        "theme": "التحقيق الجنائي (عقول إجرامية)",
        "series": 8,
        "game_mode": "single",
        "description": "أنت المحقق السري 'سيف'. أُرسلت للتحقيق في مقتل شريكك السابق 'سامي'، الذي وُجد مقتولاً داخل شقته المقفلة من الداخل في الطابق العاشر. الباب موصد، النوافذ مغلقة، ومفتاحه الوحيد داخل الشقة. الشرطة المحلية تعتبرها حالة انتحار، لكنك تعرف 'سامي' جيداً، كان يحقق في شبكة تهريب آثار كبرى. الجاني إما ساحر محترف، أو قاتل ترك دليلاً خفياً وراءه... ابحث في 'الغرفة المغلقة' ولا تفقد صوابك.",
        "start_scene": "scene_01_locked_room",
        "image_url": "https://images.unsplash.com/photo-1549419166-51eebe8eb7ce?q=80&w=600&auto=format&fit=crop",
        "scenes": [
            {
                "id": "scene_01_locked_room",
                "title": "اللغز المستحيل",
                "text": "تقف داخل الشقة المظلمة. الباب المكسور لا يزال به آثار القفل، والمفتاح الأصلي ملقى على طاولة الوسط. الجثة في منتصف الغرفة مضروبة برصاصة واحدة. لا أثر لدخول عنيف، ولا يوجد مخرج آخر. نافذة غرفة النوم مفتوحة، لكننا في الطابق العاشر ولا توجد شرفة أو درج طوارئ.",
                "image_url": "https://images.unsplash.com/photo-1594912953531-e37ea3097b69?q=80&w=600&auto=format&fit=crop",
                "choices": [
                    {
                        "text": "[فحص الباب والمفتاح بعناية]",
                        "next_scene": "scene_02_door_trick",
                        "color": "primary",
                        "points_reward": 10
                    },
                    {
                        "text": "[فحص النافذة المفتوحة في غرفة النوم]",
                        "next_scene": "scene_02_window",
                        "color": "secondary",
                        "points_reward": 5
                    },
                    {
                        "text": "[سؤال الجيران عما سمعوه]",
                        "next_scene": "scene_fail_neighbors",
                        "color": "danger",
                        "points_reward": -5
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_02_door_trick",
                "title": "خدعة المفتاح",
                "text": "تضع المفتاح في القفل، ثم تلاحظ شيئاً: هناك خيط صيد دقيق جداً (نايلون شفاف) مقطوع وملفوف حول جزء من المقبض من الداخل، وممتد نحو أسفل الباب. 'القاتل ترك المفتاح بالداخل، أغلق الباب من الخارج، وسحب المفتاح ليسقط على الطاولة باستخدام الخيط من تحت الباب!' هذا يفسر لغز الغرفة المغلقة.",
                "choices": [
                    {
                        "text": "[البحث عن أداة الجريمة]",
                        "next_scene": "scene_03_weapon",
                        "color": "primary",
                        "points_reward": 5
                    },
                    {
                        "text": "[الاستمرار في تفحص الخيط لجمع الحمض النووي]",
                        "next_scene": "scene_04_dna",
                        "color": "secondary",
                        "points_reward": 10
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_02_window",
                "title": "الهواء البارد",
                "text": "تقترب من النافذة. تنظر للأسفل نحو الشارع، مسافة مميتة. لا يمكن لأحد النزول أو الصعود. تلاحظ غباراً غير عادي (أبيض اللون) متناثراً على حافة النافذة من الداخل.",
                "choices": [
                    {
                        "text": "[جمع عينة من الغبار لتحليلها]",
                        "next_scene": "scene_05_dust",
                        "color": "primary",
                        "points_reward": 10
                    },
                    {
                        "text": "[التخمين بأن القاتل استخدم طائرة مسيرة (Drone)]",
                        "next_scene": "scene_fail_drone",
                        "color": "danger",
                        "points_reward": -10
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_03_weapon",
                "title": "السلاح المفقود",
                "text": "لا يوجد سلاح في الشقة. الساحر القاتل أخذ سلاحه معه، مما ينفي تماماً نظرية الانتحار. لكنك تجد ظَرْفَ رصاصة فارغاً أسفل الأريكة. عيار 9 ملم خاص بالشرطة.",
                "choices": [
                    {
                        "text": "الذهاب لمكتب الشريك (سامي) في المركز للبحث في ملفاته.",
                        "next_scene": "scene_06_police_station",
                        "color": "primary",
                        "points_reward": 10
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_04_dna",
                "title": "أثر غير متوقع",
                "text": "أنت ترسل الخيط المعمل الجنائي. بعد ساعات يتصلون بك: 'وجدنا خلايا جلدية مطابقة لشخص في قاعدة بياناتنا: الضابط (محمود)، رئيس وحدة الآثار المهربة.' محمود هو قائد سامي المباشر!",
                "choices": [
                    {
                        "text": "الذهاب لمواجهة الضابط محمود في مكتبه.",
                        "next_scene": "scene_07_confront_mahmoud",
                        "color": "primary",
                        "points_reward": 15
                    },
                    {
                        "text": "مراقبة محمود ليلاً لاصطياده متلبساً بالجرم.",
                        "next_scene": "scene_08_tailing",
                        "color": "secondary",
                        "points_reward": 10
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_05_dust",
                "title": "سر الغبار",
                "text": "الغبار الأبيض هو (جص) ناتج عن كسر الجدران القديمة. سامي كان يحقق في عصابة تهريب الآثار التي كانت تحفر سراديب في المدينة القديمة. القاتل دخل الشقة بملابسه الملطخة בגص الحفر.",
                "choices": [
                    {
                        "text": "الذهاب لموقع حفريات الآثار في المدينة القديمة فوراً.",
                        "next_scene": "scene_09_ancient_city",
                        "color": "primary",
                        "points_reward": 15
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_06_police_station",
                "title": "مكتب الشريك",
                "text": "مكتب سامي مقفل. عندما تحاول فتحه، تجد الضابط (محمود) يقف خلفك. 'ماذا تفعل هنا يا سيف؟ ملف سامي تم إغلاقه.'",
                "choices": [
                    {
                        "text": "'لدي شكوك، أريد مراجعة ملف شبكة الآثار.'",
                        "next_scene": "scene_10_mahmoud_suspicion",
                        "color": "primary",
                        "points_reward": 5
                    },
                    {
                        "text": "'لا شيء، أجمع متعلقاته الشخصية فقط.'",
                        "next_scene": "scene_11_steal_files",
                        "color": "secondary",
                        "points_reward": 10
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_07_confront_mahmoud",
                "title": "مواجهة الخائن",
                "text": "تدخل مكتب محمود وتغلق الباب. 'الحمض النووي الخاص بك كان على خيط في مسرح الجريمة.' محمود يتوقف عن الكتابة ويرفع مسدسه من الدرج. 'أنت تدس أنفك في أمور أكبر منك يا سيف. الآثار تدر ملايين.'",
                "choices": [
                    {
                        "text": "[الرد بإطلاق النار السريع]",
                        "next_scene": "scene_fail_shootout_station",
                        "color": "danger",
                        "points_reward": -20
                    },
                    {
                        "text": "[رفع يديك واستخدام المفاوضات لكسب الوقت] (يتطلب 20 نقطة)",
                        "required_points": 20,
                        "next_scene": "scene_win_arrest_boss",
                        "color": "success",
                        "points_reward": 15
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_08_tailing",
                "title": "لعبة المراقبة",
                "text": "تراقب محمود حتى منتصف الليل. يقود سيارته نحو المدينة القديمة. يدخل مستودعاً مهجوراً حيث تضيء مصابيح قوية وتسمع أصوات حفر. عصابة التهريب تفرغ الشاحنة.",
                "choices": [
                    {
                        "text": "[تجاوز الحراس والتسلل للداخل لالتقاط صور كدليل] (يتطلب 25 نقطة تسلل)",
                        "required_points": 25,
                        "next_scene": "scene_12_stealth_photo",
                        "color": "success",
                        "points_reward": 15
                    },
                    {
                        "text": "[طلب الدعم اللاسلكي وانتظار القوات]",
                        "next_scene": "scene_win_mafia_bust",
                        "color": "secondary",
                        "points_reward": 5
                    },
                    {
                        "text": "[اقتحام المكان بمفردك كبطل]",
                        "next_scene": "scene_fail_hero_complex",
                        "color": "danger",
                        "points_reward": -30
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_09_ancient_city",
                "title": "السراديب المظلمة",
                "text": "تدخل سراديب الحفر في المدينة القديمة وحدك بناءً على دليل الغبار. المكان بارد ورطب. تسمع خطوات تقترب وتختبئ خلف عمود حجري.",
                "choices": [
                    {
                        "text": "الانقضاض على الرجل المتقدم في الظلام.",
                        "next_scene": "scene_13_capture_smuggler",
                        "color": "primary",
                        "points_reward": 10
                    },
                    {
                        "text": "التراجع للخارج وطلب التعزيزات.",
                        "next_scene": "scene_win_mafia_bust",
                        "color": "secondary",
                        "points_reward": 5
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_10_mahmoud_suspicion",
                "title": "العداء المكشوف",
                "text": "'الآثار؟ لا تتدخل.' محمود يصادر مفتاحك. أصبحت الآن تحت المراقبة اللصيقة وتم منعك من التحقيق في القضية. خطوة غبية جعلته يدرك أنك تعرف أكثر من اللازم.",
                "choices": [
                    {
                        "text": "الانسحاب بهدوء...",
                        "next_scene": "scene_fail_fired",
                        "color": "danger",
                        "points_reward": 0
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_11_steal_files",
                "title": "السرقة المشروعة",
                "text": "تنتظر حتى الليل وتتسلل لمكتب سامي. تجد ملفاً في قاع درج سري مسجل فيه: (محمود - رئيس الوحدة هو الممول لعمليات التهريب. موعد التسليم القادم في المدينة القديمة).",
                "choices": [
                    {
                        "text": "الذهاب للمدينة القديمة.",
                        "next_scene": "scene_08_tailing",
                        "color": "primary",
                        "points_reward": 10
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_12_stealth_photo",
                "title": "التسلل المحترف",
                "text": "تتسلل بين الصناديق دون إصدار أي صوت. تلتقط صوراً لمحمود وهو يتبادل الأموال مع تجار أجانب. ترسل الصور فوراً لمدير شرطة العاصمة متجاوزاً إدارتك الفاسدة. الدليل موثق ولا مجال للهرب.",
                "choices": [
                    {
                        "text": "تنتظر وصول القوات الخاصة.",
                        "next_scene": "scene_win_perfect",
                        "required_points": 35,
                        "color": "success",
                        "points_reward": 20
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_13_capture_smuggler",
                "title": "اعتراف قسري",
                "text": "تطرحه أرضاً وتضع المسدس في رأسه. إنه أحد اللصوص. 'من أمر بقتل سامي؟' تصرخ. اللص يبكي: 'الضابط محمود! هو من دبر كل شيء وأدخل القاتل للشقة.'",
                "choices": [
                    {
                        "text": "أخذه كرهينة ومواجهة العصابة.",
                        "next_scene": "scene_fail_hero_complex",
                        "color": "danger",
                        "points_reward": -20
                    },
                    {
                        "text": "الانسحاب واعتقاله كشاهد ملك.",
                        "next_scene": "scene_win_witness",
                        "color": "success",
                        "points_reward": 15
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_fail_neighbors",
                "title": "النهاية: تحقيق سطحي",
                "text": "الجيران لم يسمعوا شيئاً بسبب كاتم الصوت. تركيزك على الخارج أضاع الدليل الحاسم داخل الشقة. تم إغلاق القضية كحالة انتحار، وروح صديقك لم ترتح. (لقد خسرت).",
                "choices": [],
                "is_ending": True
            },
             {
                "id": "scene_fail_drone",
                "title": "النهاية: الخيال العلمي",
                "text": "افتراضك بأن طائرة مسيرة قتلت سامي جعلك أضحوكة بين المحققين. أضعت وقتك في البحث عن كاميرات الشوارع، بينما هرب القاتل ونظف محمود مسرح الجريمة من بقايا الجص والخيط. (لقد خسرت).",
                "choices": [],
                "is_ending": True
            },
             {
                "id": "scene_fail_shootout_station",
                "title": "النهاية: محقق قاتل",
                "text": "تبادلت النار داخل المركز. قتلت محمود، لكن تم اعتقالك بتهمة قتل ضابط مسؤول. لا أحد صدق قصتك بدون أدلة قاطعة. السجن المؤبد بانتظارك. (لقد خسرت).",
                "choices": [],
                "is_ending": True
            },
             {
                "id": "scene_fail_hero_complex",
                "title": "النهاية: متلازمة البطل",
                "text": "اقتحام مستودع مليء بـ 20 مسلحاً بمسدس واحد؟ مجرد انتحار. تم تمزيق جسدك بالرصاص بمجرد كشفك. الآثار هُربت ومحمود لا يزال رئيساً لوحدته. (لقد خسرت حياتك).",
                "choices": [],
                "is_ending": True
            },
            {
                "id": "scene_fail_fired",
                "title": "النهاية: إيقاف عن العمل",
                "text": "محمود استغل سلطته ليلفق لك تهمة إهمال وطردك من السلك الشرطي. سامي مات، وأنت عاطل عن العمل، والعصابة تتوسع. (فشل كارثي).",
                "choices": [],
                "is_ending": True
            },
            {
                "id": "scene_win_arrest_boss",
                "title": "النهاية: فخ التسجيل",
                "text": "استخدمت مهاراتك التفاوضية لتجعل محمود يعترف بتفاصيل سرقة الآثار وقتل سامي، بينما كان هاتفك يسجل المكالمة ويبثها للرئيس المباشر. تم اقتحام المكتب واعتقال محمود. انتقمت لصديقك! (لقد فزت بذكاء).",
                "choices": [],
                "is_ending": True
            },
             {
                "id": "scene_win_mafia_bust",
                "title": "النهاية: سقوط العصابة",
                "text": "وصلت القوات واعتقلت العصابة في المستودع. محمود حاول الهرب لكن تم القبض عليه. تم تفكيك شبكة الآثار العظمى واستعادة الكنوز. (لقد فزت بجدارة).",
                "choices": [],
                "is_ending": True
            },
             {
                "id": "scene_win_witness",
                "title": "النهاية: شاهد الملك",
                "text": "استخدامك للص كشاهد ملك أطاح بمحمود أمام النيابة العامة. تم كشف اللغز بنجاح ووضعت حداً للفساد. لقد أرحت روح سامي أخيراً. (لقد فزت بقوة القانون).",
                "choices": [],
                "is_ending": True
            },
            {
                "id": "scene_win_perfect",
                "title": "النهاية (نجاح مذهل): الضربة القاضية",
                "text": "الصور التي أرسلتها مع أدلة الخيط من مسرح الجريمة أدت لتدخل القوات الخاصة فوراً. تم القبض على العصابة، وصودرت الآثار وملايين الدولارات. محمود وُضع في السجن وواجه حكماً بالإعدام، وأنت أصبحت رئيساً للوحدة! (أفضل نهاية مسار).",
                "choices": [],
                "is_ending": True
            }
        ]
    }

    os.makedirs("data/stories", exist_ok=True)
    with open("data/stories/sp_investigation_8.json", "w", encoding="utf-8") as f:
        json.dump(story, f, ensure_ascii=False, indent=4)
    print("Story 8 generated successfully!")

if __name__ == "__main__":
    generate_story()
