import json
from pathlib import Path

# Act 1 (nodes 1-15)
nodes = {
    "start": {
        "text": "تستيقظ من سبات عميق، نصلك البارد مغروس في الطين. يد مرتعشة تمتد إليك. شاب، ربما خادم فارس مات للتو في هذه المعركة. عيناه مليئتان بالخوف، لكن يده تبحث عن سلاح.",
        "choices": [
            {
                "label": "امنحه القوة المظلمة",
                "emoji": "🔥",
                "next": "empower_squire",
                "points_reward": 2,
                "color": "danger",
                "sets_flag": "squire_corrupted"
            },
            {
                "label": "اسحب طاقته الضعيفة",
                "emoji": "🧛",
                "next": "drain_squire",
                "points_reward": 1,
                "color": "danger"
            },
            {
                "label": "ابق ساكنا وعاديا",
                "emoji": "🗡️",
                "next": "stay_silent",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "empower_squire": {
        "text": "بمجرد أن يلمس مقبضك، تبث في عروقه قوة خارقة. يصرخ الشاب بينما تشتعل عيناه بنور أحمر. ينهض ويذبح جنديين يقتربان منه بضربة واحدة.",
        "choices": [
            {
                "label": "ادفعه لمطاردة القائد",
                "emoji": "👑",
                "next": "hunt_leader",
                "points_reward": 2,
                "color": "danger"
            },
            {
                "label": "أمره بالهرب للغابة",
                "emoji": "🌲",
                "next": "flee_woods",
                "points_reward": 1,
                "color": "secondary"
            }
        ]
    },
    "drain_squire": {
        "text": "تمتص حرارة جسده في ثوان. يسقط الشاب ميتا بجوارك. طعم روحه الضعيفة يوقظ حواسك، لكنك الآن بلا حامل في ساحة معركة تعج بالنهابين.",
        "choices": [
            {
                "label": "انتظر قدوم الناهبين",
                "emoji": "💰",
                "next": "wait_looters",
                "points_reward": 1,
                "color": "secondary"
            },
            {
                "label": "أصدر طنينا سحريا",
                "emoji": "✨",
                "next": "magic_hum",
                "points_reward": 0,
                "color": "primary"
            }
        ]
    },
    "stay_silent": {
        "text": "يتناولك الشاب كأي سيف عادي. يحاول الدفاع عن نفسه ضد مرتزق ضخم يقترب، لكن يده ترتعش بشدة ولا يجيد القتال.",
        "choices": [
            {
                "label": "تدخل في اللحظة الأخيرة",
                "emoji": "⚔️",
                "next": "intervene_last_moment",
                "points_reward": 1,
                "color": "success"
            },
            {
                "label": "دعه يموت بصمت",
                "emoji": "💀",
                "next": "death_muddy_puddle",
                "points_reward": 0,
                "color": "danger"
            }
        ]
    },
    "death_muddy_puddle": {
        "text": "يموت الشاب ويسقط فوقك. تغوص أعمق في الوحل، وتتراكم فوقك الجثث. تمر عقود وتتحول إلى مجرد صدأ في مستنقع منسي. لو منحت القليل من قوتك، لربما نجوتما.",
        "is_ending": True,
        "choices": []
    },
    "hunt_leader": {
        "text": "الشاب يندفع كالمجنون نحو قائد المرتزقة. قوتك تجعل ضرباته مدمرة، لكن جسد الشاب لا يتحمل هذه الطاقة. عروقه تتمزق مع كل ضربة.",
        "choices": [
            {
                "label": "اسحب قوتك قليلا",
                "emoji": "📉",
                "next": "withdraw_power",
                "points_reward": 1,
                "color": "success"
            },
            {
                "label": "زد من الطاقة",
                "emoji": "⚡",
                "next": "max_power_burst",
                "points_reward": 2,
                "color": "danger"
            }
        ]
    },
    "flee_woods": {
        "text": "يهرب الشاب إلى الغابة المظلمة. يعسكر هناك وهو يلهث، ينظر إليك برعب وإعجاب. يهمس: 'من أنت؟ ماذا تكون؟'",
        "choices": [
            {
                "label": "تحدث في عقله",
                "emoji": "🧠",
                "next": "speak_mind",
                "points_reward": 1,
                "color": "primary"
            },
            {
                "label": "اعرض له رؤيا",
                "emoji": "👁️",
                "next": "show_vision",
                "points_reward": 2,
                "color": "primary"
            }
        ]
    },
    "wait_looters": {
        "text": "يقترب ناهب جثث. يرى مقبضك المزخرف وعينيه تلمعان جشعا. يلتقطك، تشعر بنواياه الدنيئة. إنه ينوي بيعك في سوق سوداء.",
        "choices": [
            {
                "label": "سيطر على عقله",
                "emoji": "🕸️",
                "next": "control_looter",
                "points_reward": 2,
                "color": "danger",
                "sets_flag": "mind_control"
            },
            {
                "label": "انتظر الوصول للسوق",
                "emoji": "🛒",
                "next": "black_market",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "magic_hum": {
        "text": "تصدر طنينا خافتا. ساحر يمر بالصدفة يلاحظك. يرفعك بحذر، يدرك أنك لست سيفا عاديا، بل وعي محبوس.",
        "choices": [
            {
                "label": "اخدعه بنور ملائكي",
                "emoji": "👼",
                "next": "angelic_light",
                "points_reward": 1,
                "color": "primary"
            },
            {
                "label": "أظهر طبيعتك المظلمة",
                "emoji": "😈",
                "next": "dark_nature",
                "points_reward": 2,
                "color": "danger",
                "sets_flag": "revealed_darkness"
            }
        ]
    },
    "intervene_last_moment": {
        "text": "تعدل مسار الضربة بوزنك وتصد سيف المرتزق. الشاب يكتسب ثقة مفاجئة ويهزم خصمه، لكنه يلاحظ أنك تتحرك من تلقاء نفسك.",
        "choices": [
            {
                "label": "اجعله يعتقد أنها مهارته",
                "emoji": "🤥",
                "next": "fake_skill",
                "points_reward": 1,
                "color": "primary"
            },
            {
                "label": "اكشف وعيك له",
                "emoji": "👁️",
                "next": "reveal_consciousness",
                "points_reward": 2,
                "color": "secondary"
            }
        ]
    },
    "withdraw_power": {
        "text": "تسحب قوتك لحمايته. لكن القائد يستغل اللحظة ويوجه ضربة قاضية. يسقط الشاب وتنتقل أنت ليد القائد القاسي.",
        "choices": [
            {
                "label": "تسميم دم القائد",
                "emoji": "☠️",
                "next": "poison_blood",
                "points_reward": 2,
                "color": "danger"
            },
            {
                "label": "اخدم القائد مؤقتا",
                "emoji": "🛡️",
                "next": "serve_leader",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "max_power_burst": {
        "text": "الجسد يتمزق. الشاب يقتل القائد لكنه ينفجر من شدة الطاقة. أنت الآن مرمي بين جثتين قويتين.",
        "choices": [
            {
                "label": "استحوذ على القائد الميت",
                "emoji": "🧟",
                "next": "possess_corpse",
                "points_reward": 3,
                "color": "danger",
                "sets_flag": "corpse_walker"
            },
            {
                "label": "انتظر حاملا جديدا",
                "emoji": "⏳",
                "next": "wait_new_wielder",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "speak_mind": {
        "text": "تهمس في عقله بأنك سيف الأبطال القدماء. الشاب يصدقك ويقسم على خدمتك. يقرر التوجه نحو قلعة النور القريبة.",
        "choices": [
            {
                "label": "شجعه على ذلك",
                "emoji": "👍",
                "next": "encourage_light",
                "points_reward": 1,
                "color": "success"
            },
            {
                "label": "وجهه نحو الأطلال",
                "emoji": "🏰",
                "next": "redirect_ruins",
                "points_reward": 2,
                "color": "danger"
            }
        ]
    },
    "show_vision": {
        "text": "تعرض له رؤيا لمجد زائف، ملوك يسجدون له. يمتلئ بالغرور ويتجه نحو معسكر قطاع الطرق ليختبر قوته الجديدة.",
        "choices": [
            {
                "label": "ساعده في المعركة",
                "emoji": "⚔️",
                "next": "help_bandit_fight",
                "points_reward": 1,
                "color": "danger"
            },
            {
                "label": "دعه يقاتل وحده",
                "emoji": "⚖️",
                "next": "let_fight_alone",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "control_looter": {
        "text": "عقل الناهب ضعيف. تكسر إرادته بسهولة وتحوله إلى دمية طيعة. ينهض وعيناه سوداوان، مستعدا لتنفيذ أوامرك.",
        "choices": [
            {
                "label": "امره بقتل رفاقه",
                "emoji": "🩸",
                "next": "kill_companions",
                "points_reward": 2,
                "color": "danger"
            },
            {
                "label": "امره بالتوجه للحدّاد",
                "emoji": "🔨",
                "next": "go_blacksmith",
                "points_reward": 1,
                "color": "primary"
            }
        ]
    }
}


# Act 2 (nodes 16-30)
act_2_nodes = {
    "black_market": {
        "text": "تباع لتاجر أسلحة ثري. يعرضك في متجره. في الليل، يقتحم لص المتجر لسرقتك. اللص محترف ومجهز جيدا.",
        "choices": [
            {
                "label": "سهل له السرقة",
                "emoji": "🔓",
                "next": "help_thief",
                "points_reward": 1,
                "color": "secondary"
            },
            {
                "label": "أيقظ التاجر بقوة",
                "emoji": "🔔",
                "next": "wake_merchant",
                "points_reward": 0,
                "color": "primary"
            }
        ]
    },
    "angelic_light": {
        "text": "يقتنع الساحر أنك قطعة مقدسة. يأخذك إلى طائفة النور. في المعبد، يقرر الكهنة وضعك في ختم التطهير لكشف حقيقتك.",
        "choices": [
            {
                "label": "قاوم الختم بعنف",
                "emoji": "💥",
                "next": "resist_seal",
                "points_reward": 2,
                "color": "danger"
            },
            {
                "label": "اخضع للختم",
                "emoji": "🛐",
                "next": "submit_seal",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "dark_nature": {
        "text": "يدرك الساحر خطورتك، يحاول تدميرك. يلقي تعويذة تفكيك نارية، معدنك يبدأ في الانصهار ببطء.",
        "choices": [
            {
                "label": "امتص طاقة التعويذة",
                "emoji": "🌪️",
                "next": "absorb_spell",
                "points_reward": 2,
                "color": "danger"
            },
            {
                "label": "حطم تركيزه الرابط",
                "emoji": "🧠",
                "next": "break_focus",
                "points_reward": 1,
                "color": "primary"
            }
        ]
    },
    "fake_skill": {
        "text": "يعتقد الشاب أنه عبقري سيف. يزداد تهوره، يتحدى فارسا مدرعا في الطريق. الفارس يضحك ويسحب مطرقته.",
        "choices": [
            {
                "label": "اقطع درع الفارس",
                "emoji": "⚔️",
                "next": "cut_armor",
                "points_reward": 2,
                "color": "danger"
            },
            {
                "label": "تجاهله دعه يتلقى الضربة",
                "emoji": "💀",
                "next": "death_shattered_fool",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "death_shattered_fool": {
        "text": "المطرقة تهوي بقوة. الشاب يسحق، وأنت تتحطم إلى نصفين. غرورك في إخفاء قوتك جعلك أداة بلا قيمة. تموت محطما في التراب.",
        "is_ending": True,
        "choices": []
    },
    "reveal_consciousness": {
        "text": "يرى الشاب وجهك في انعكاس النصل. يرتعب ويرميك في بئر قديم ويهرب. تغوص في الظلام الرطب.",
        "choices": [
            {
                "label": "نادي في الأعماق",
                "emoji": "🗣️",
                "next": "call_depths",
                "points_reward": 1,
                "color": "primary"
            },
            {
                "label": "انتظر بصمت طويل",
                "emoji": "⏳",
                "next": "death_rusty_grave",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "death_rusty_grave": {
        "text": "تمر القرون وأنت في قاع البئر. المياه تأكل معدنك ببطء. وعيك يتلاشى قطرة بقطرة حتى تصبح مجرد ذكرى صدئة. كان عليك ألا تخيف حاملك.",
        "is_ending": True,
        "choices": []
    },
    "poison_blood": {
        "text": "يسري سمك في عروق القائد. يتألم ويسقط في جنون الدم، يقتل رجاله واحدا تلو الآخر حتى ينهار قلبه.",
        "choices": [
            {
                "label": "امتص أرواح الجميع",
                "emoji": "👻",
                "next": "absorb_all_souls",
                "points_reward": 3,
                "color": "danger",
                "sets_flag": "mass_murderer"
            },
            {
                "label": "ابحث عن ناج قوي",
                "emoji": "🔍",
                "next": "find_survivor",
                "points_reward": 1,
                "color": "primary"
            }
        ]
    },
    "serve_leader": {
        "text": "تخدم القائد لسنوات. يصبح سفاحا معروفا. في يوم، يواجه بطل النور في مبارزة ملحمية.",
        "choices": [
            {
                "label": "اخن القائد",
                "emoji": "🗡️",
                "next": "betray_leader",
                "points_reward": 2,
                "color": "primary"
            },
            {
                "label": "اقتل بطل النور",
                "emoji": "☠️",
                "next": "kill_hero",
                "points_reward": 2,
                "color": "danger"
            }
        ]
    },
    "possess_corpse": {
        "text": "الجثة تنهض وأنت تتحكم بها. حركاتها بطيئة، لكنك لا تشعر بالألم. تتجه نحو المدينة لتجد جسدا أفضل أو حدادا ماهرا.",
        "choices": [
            {
                "label": "اذهب للحداد السري",
                "emoji": "🔨",
                "next": "secret_blacksmith",
                "points_reward": 2,
                "color": "primary",
                "sets_flag": "forge_secret"
            },
            {
                "label": "هاجم حراس المدينة",
                "emoji": "🛡️",
                "next": "attack_guards",
                "points_reward": 1,
                "color": "danger"
            }
        ]
    },
    "wait_new_wielder": {
        "text": "طائر غراب ضخم يهبط، يلتقطك بمنقاره القوي محلقا بك بعيدا. يسقطك فوق جبل بركاني حيث يقيم تنين نائم.",
        "choices": [
            {
                "label": "أيقظ التنين بطنينك",
                "emoji": "🐉",
                "next": "wake_dragon",
                "points_reward": 2,
                "color": "danger"
            },
            {
                "label": "ابق ساكنا لتختبئ",
                "emoji": "🤫",
                "next": "hide_dragon",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "encourage_light": {
        "text": "في قلعة النور، يشعر الكهنة بظلامك. يقررون صهرك في نار مقدسة لتطهير الشاب.",
        "choices": [
            {
                "label": "توسل للشاب لينقذك",
                "emoji": "🥺",
                "next": "beg_squire",
                "points_reward": 1,
                "color": "secondary"
            },
            {
                "label": "هاجم الكهنة بالظلام",
                "emoji": "🌑",
                "next": "attack_priests",
                "points_reward": 2,
                "color": "danger"
            }
        ]
    },
    "redirect_ruins": {
        "text": "في الأطلال الملعونة، يجد الشابแท่น طقوس قديم. القوة تتسرب منه إليك. يطلب منك أن تمنحه الخلود.",
        "choices": [
            {
                "label": "حوله إلى خادم زومبي",
                "emoji": "🧟",
                "next": "turn_zombie",
                "points_reward": 2,
                "color": "danger"
            },
            {
                "label": "ارفض وامتص الطقس",
                "emoji": "🚫",
                "next": "absorb_ritual",
                "points_reward": 3,
                "color": "primary",
                "sets_flag": "ritual_power"
            }
        ]
    },
    "help_bandit_fight": {
        "text": "الشاب يقتل قطاع الطرق واحدا تلو الآخر بقسوة. زعيم القطاع يعرض عليه صفقة: أن يصبح هو الزعيم الجديد.",
        "choices": [
            {
                "label": "اقبل وكن زعيمهم",
                "emoji": "👑",
                "next": "become_bandit_king",
                "points_reward": 2,
                "color": "danger"
            },
            {
                "label": "اقتل الزعيم أيضا",
                "emoji": "🩸",
                "next": "kill_bandit_boss",
                "points_reward": 1,
                "color": "primary"
            }
        ]
    },
    "let_fight_alone": {
        "text": "الشاب يقاتل وحده بدون قوتك. يكثر عليه الأعداء ويمزقونه إربا. يلتقطك أحد القطاع ويستخدمك لتقطيع الحطب.",
        "choices": [
            {
                "label": "حطم يد الحطاب",
                "emoji": "💥",
                "next": "shatter_hand",
                "points_reward": 1,
                "color": "danger"
            },
            {
                "label": "انتظر فرصة أفضل",
                "emoji": "⏳",
                "next": "wait_better_chance",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    }
}
nodes.update(act_2_nodes)

# Act 3 (nodes 31-45)
act_3_nodes = {
    "help_thief": {
        "text": "اللص يسرقك ويهرب ببراعة. يبيعك لنبيل مختل يعشق جمع الأسلحة الملعونة في قبو قصره.",
        "choices": [
            {
                "label": "اهمس للنبيل بالجنون",
                "emoji": "🗣️",
                "next": "whisper_madness",
                "points_reward": 2,
                "color": "danger"
            },
            {
                "label": "اسر وعي السلاح المجاور",
                "emoji": "🗡️",
                "next": "steal_weapon_soul",
                "points_reward": 1,
                "color": "primary"
            }
        ]
    },
    "wake_merchant": {
        "text": "التاجر يستيقظ ويطلق النار من بندقيته السحرية. اللص يسقط، لكن التعويذة تصيبك بالخطأ، مما يسبب شرخا في نصلك.",
        "choices": [
            {
                "label": "امتص دم اللص للشفاء",
                "emoji": "🩸",
                "next": "heal_with_blood",
                "points_reward": 2,
                "color": "danger"
            },
            {
                "label": "تحمل الألم واصمت",
                "emoji": "🤐",
                "next": "death_shattered_blade",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "death_shattered_blade": {
        "text": "الشرخ يزداد مع كل حركة للتاجر الذي يحملك. في أول اختبار لصلابتك، تنكسر إلى ألف قطعة. تتناثر شظايا وعيك في الهواء.",
        "is_ending": True,
        "choices": []
    },
    "resist_seal": {
        "text": "تنفجر طاقتك المظلمة محطمة الختم. المعبد يحترق بنار سوداء. الكهنة يفرون، وأنت مرمي في وسط الرماد كشيطان حر.",
        "choices": [
            {
                "label": "اتصل بشياطين الرماد",
                "emoji": "👿",
                "next": "summon_ash_demons",
                "points_reward": 3,
                "color": "danger",
                "sets_flag": "demon_lord"
            },
            {
                "label": "انتظر بين الأنقاض",
                "emoji": "🏚️",
                "next": "wait_ruins",
                "points_reward": 1,
                "color": "secondary"
            }
        ]
    },
    "submit_seal": {
        "text": "تستسلم للختم. يمحو النور ذكرياتك وهويتك تدريجيا. تصبح سيفا عاديا لامعا، خاليا من أي روح أو وعي.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "💀",
                "next": "death_holy_seal",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "death_holy_seal": {
        "text": "تم محو وعيك بالكامل. لقد أصبحت أداة مقدسة بلا إرادة، ينحني لك الناس دون أن يعلموا أن روحك قد مُحيت للأبد.",
        "is_ending": True,
        "choices": []
    },
    "absorb_spell": {
        "text": "تمتص التعويذة النارية. نصلك يتوهج بحرارة الجحيم. الساحر يصرخ محترقا. يمسك بك محارب متمرد رأى المشهد.",
        "choices": [
            {
                "label": "امنحه قوة النار",
                "emoji": "🔥",
                "next": "grant_fire_power",
                "points_reward": 2,
                "color": "danger"
            },
            {
                "label": "احرق يده لترهيبه",
                "emoji": "♨️",
                "next": "burn_hand",
                "points_reward": 1,
                "color": "primary"
            }
        ]
    },
    "break_focus": {
        "text": "تصدر صوتا حادا يكسر تركيز الساحر. التعويذة ترتد عليه وتجمده. الساحر يتحول إلى تمثال جليدي وأنت بيده.",
        "choices": [
            {
                "label": "حطم التمثال الجليدي",
                "emoji": "🧊",
                "next": "shatter_statue",
                "points_reward": 2,
                "color": "danger"
            },
            {
                "label": "ابق مجمدا وانتظر",
                "emoji": "❄️",
                "next": "stay_frozen",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "call_depths": {
        "text": "صوتك يتردد في الأعماق. وحش مائي أعمى يبتلعك. في بطنه المظلم، تدرك أنك تسافر نحو مدينة غارقة أسفل البئر.",
        "choices": [
            {
                "label": "مزق أحشاء الوحش",
                "emoji": "🩸",
                "next": "tear_monster",
                "points_reward": 2,
                "color": "danger"
            },
            {
                "label": "اخرج سلميا في المدينة",
                "emoji": "🌊",
                "next": "exit_peacefully",
                "points_reward": 1,
                "color": "primary"
            }
        ]
    },
    "absorb_all_souls": {
        "text": "تشرب أرواح الجميع. تصبح ثقيلا جدا، ممتلئا بالخطايا. لا أحد يستطيع حملك الآن سوى مخلوق من الجحيم.",
        "choices": [
            {
                "label": "افتح بوابة الجحيم",
                "emoji": "🚪",
                "next": "open_hell_gate",
                "points_reward": 3,
                "color": "danger",
                "sets_flag": "hell_opened"
            },
            {
                "label": "اغفو لتستوعب القوة",
                "emoji": "💤",
                "next": "sleep_power",
                "points_reward": 1,
                "color": "secondary"
            }
        ]
    },
    "find_survivor": {
        "text": "تجد طفلا يتيما بين الجثث. يحملك بصعوبة. براءته تمنعك من إيذائه، لكن العالم قاس.",
        "choices": [
            {
                "label": "كن حارسه الشخصي",
                "emoji": "🛡️",
                "next": "guard_orphan",
                "points_reward": 2,
                "color": "success",
                "sets_flag": "guardian_path"
            },
            {
                "label": "افسد براءته ببطء",
                "emoji": "🐍",
                "next": "corrupt_orphan",
                "points_reward": 2,
                "color": "danger"
            }
        ]
    },
    "betray_leader": {
        "text": "في لحظة الحسم، تجعل نصلك ينحرف. بطل النور يقطع رأس القائد. البطل يلتقطك، يشعر بوجودك لكنه يعتقد أنك تبت عن الشر.",
        "choices": [
            {
                "label": "اخدعه وتظاهر بالتوبة",
                "emoji": "😇",
                "next": "fake_repentance",
                "points_reward": 1,
                "color": "primary"
            },
            {
                "label": "تمرد عليه فورا",
                "emoji": "⚔️",
                "next": "rebel_hero",
                "points_reward": 2,
                "color": "danger"
            }
        ]
    },
    "kill_hero": {
        "text": "تقطع درع بطل النور. القائد يرفعك منتصرا. لكن طاقة النور من دم البطل تبدأ في حرق معدنك من الداخل.",
        "choices": [
            {
                "label": "تخلص من دم البطل",
                "emoji": "💦",
                "next": "purge_blood",
                "points_reward": 2,
                "color": "danger"
            },
            {
                "label": "تحمل الحرق",
                "emoji": "🔥",
                "next": "endure_burn",
                "points_reward": 1,
                "color": "primary"
            }
        ]
    },
    "secret_blacksmith": {
        "text": "تصل جثتك للحداد الأسطوري. يرى الحقيقة، يعرض عليك صفقة: يصنع لك جسما حقيقيا مقابل تدمير المملكة.",
        "choices": [
            {
                "label": "اقبل الصفقة العظيمة",
                "emoji": "🤝",
                "next": "accept_forge_deal",
                "points_reward": 3,
                "color": "danger",
                "requires_flag": "forge_secret"
            },
            {
                "label": "اقتل الحداد واستخدم ناره",
                "emoji": "🔥",
                "next": "kill_blacksmith",
                "points_reward": 2,
                "color": "danger"
            }
        ]
    },
    "attack_guards": {
        "text": "الجثة تهاجم الحراس ببطء. يقطعونها إربا ويقذفونك في النهر كخردة ملعونة.",
        "choices": [
            {
                "label": "اغرق",
                "emoji": "🌊",
                "next": "death_ocean_bottom",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    }
}
nodes.update(act_3_nodes)

# Act 4 and Endings (nodes 46-60+)
act_4_nodes = {
    "death_ocean_bottom": {
        "text": "تستقر في قاع المحيط البارد المظلم. لا نور، لا حرارة، ولا أحد ليحملك. الأسماك تمر بجانبك دون اكتراث. وعيك يتلاشى في عزلة أبدية.",
        "is_ending": True,
        "choices": []
    },
    "wake_dragon": {
        "text": "التنين يفتح عينا ذهبية عملاقة. ينظر إليك، يدرك أنك واعٍ. ينفث نارا بركانية لصهرك.",
        "choices": [
            {
                "label": "امتص نار التنين",
                "emoji": "🐉",
                "next": "absorb_dragon_fire",
                "points_reward": 3,
                "color": "danger"
            },
            {
                "label": "حاول عكس النار",
                "emoji": "🛡️",
                "next": "death_dragon_fire",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "death_dragon_fire": {
        "text": "النار التنينية تفوق أي سحر عرفته. معدنك ينصهر في ثوان. قطرة حارقة واحدة تنزل على الصخر وتتصلب. لقد انتهيت.",
        "is_ending": True,
        "choices": []
    },
    "hide_dragon": {
        "text": "تبقى ساكنا. التنين لا يلاحظك. تمر مئات السنين. أنت مدفون تحت أطنان من الذهب والكنوز في عرين التنين. سجن ذهبي.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "💀",
                "next": "death_buried_alive",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "death_buried_alive": {
        "text": "تحت أطنان من الذهب، صراخك العقلي لا يصل لأحد. التنين ينام فوقك كجبل لا يتحرك. عزلة أبدية في قبر ذهبي.",
        "is_ending": True,
        "choices": []
    },
    "beg_squire": {
        "text": "تتوسل للشاب في عقله. الشاب يبكي ويحاول إخراجك من النار، لكن الكهنة يضربونه ويمنعونه. تشاهد حاملك يُعذب بينما تنصهر أنت.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "💀",
                "next": "death_melted_down",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "death_melted_down": {
        "text": "النار المقدسة تصهرك تماما. وعيك يتبخر في الدخان الأبيض. لقد عشت كسلاح ملعون ومت كأداة مطهرة. وداعا.",
        "is_ending": True,
        "choices": []
    },
    "attack_priests": {
        "text": "تطلق موجة ظلام تخنق الكهنة. الشاب يهرب بك من القلعة. هو الآن مطلوب للعدالة، وتطارده قوى النور.",
        "choices": [
            {
                "label": "دله على الملاذ المظلم",
                "emoji": "🦇",
                "next": "dark_sanctuary",
                "points_reward": 2,
                "color": "danger"
            },
            {
                "label": "اطلب منه القتال",
                "emoji": "⚔️",
                "next": "fight_light",
                "points_reward": 1,
                "color": "primary"
            }
        ]
    },
    "turn_zombie": {
        "text": "تحوله لزومبي. الآن أنت تتحكم في جسد ميت لا يتعب. تتوجه نحو عاصمة المملكة لنشر الطاعون المظلم.",
        "choices": [
            {
                "label": "انشر الطاعون",
                "emoji": "🦠",
                "next": "spread_plague",
                "points_reward": 2,
                "color": "danger"
            },
            {
                "label": "ابحث عن الملك",
                "emoji": "👑",
                "next": "seek_king",
                "points_reward": 2,
                "color": "danger"
            }
        ]
    },
    "absorb_ritual": {
        "text": "تمتص قوة الطقس بالكامل. الشاب يسقط مغشيا عليه. أنت الآن مشع بالطاقة، تطفو في الهواء من تلقاء نفسك.",
        "choices": [
            {
                "label": "اخترق السماء",
                "emoji": "🌌",
                "next": "pierce_sky",
                "points_reward": 3,
                "color": "danger"
            },
            {
                "label": "ايقظ الشاب كخادم",
                "emoji": "🧟",
                "next": "wake_servant",
                "points_reward": 1,
                "color": "secondary"
            }
        ]
    },
    "become_bandit_king": {
        "text": "يصبح الشاب زعيم القطاع. يبني إمبراطورية إجرامية. لكنه يصبح مهووسا بك ويرفض استخدام أي سلاح آخر.",
        "choices": [
            {
                "label": "قد حملته ضد المملكة",
                "emoji": "🏰",
                "next": "campaign_kingdom",
                "points_reward": 2,
                "color": "danger"
            },
            {
                "label": "اغدر به لزعيم أقوى",
                "emoji": "🗡️",
                "next": "betray_for_stronger",
                "points_reward": 2,
                "color": "danger"
            }
        ]
    },
    "kill_bandit_boss": {
        "text": "تقتل الزعيم، فيهرب بقية القطاع رعبا. الشاب يصبح وحيدا ومرعبا. يقرر دفنك ليهرب من اللعنة.",
        "choices": [
            {
                "label": "الاستسلام للدفن",
                "emoji": "🪦",
                "next": "death_abandoned",
                "points_reward": 0,
                "color": "secondary"
            },
            {
                "label": "قطع يده قبل الدفن",
                "emoji": "🩸",
                "next": "cut_hand",
                "points_reward": 1,
                "color": "danger"
            }
        ]
    },
    "death_abandoned": {
        "text": "يتم دفنك تحت شجرة قديمة. لا أحد يعرف مكانك. الشاب يعيش حياة طبيعية، وأنت تبقى في الظلام، منسيا إلى الأبد.",
        "is_ending": True,
        "choices": []
    },
    "shatter_hand": {
        "text": "تفجر طاقة مظلمة تحطم يد الحطاب. يصرخ ويرميك في بئر صرف صحي قريب.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "💀",
                "next": "death_sewers",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "death_sewers": {
        "text": "في المجاري العفنة، تُنسى كخردة صدئة. لا وحوش هنا، فقط قذارة. وعيك يتلاشى من الملل واليأس.",
        "is_ending": True,
        "choices": []
    },
    "wait_better_chance": {
        "text": "تنتظر، لكن الحطاب يستخدمك بقسوة على الأحجار، نصلك يتهشم ويتحول لأداة زراعية عمياء.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "💀",
                "next": "death_shattered_blade",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "whisper_madness": {
        "text": "النبيل يقتل حراسه ويغرق في الجنون. يقرر إقامة طقس استدعاء شيطاني.",
        "choices": [
            {
                "label": "ساعده في الطقس",
                "emoji": "👿",
                "next": "help_summon",
                "points_reward": 2,
                "color": "danger"
            },
            {
                "label": "عرقل الطقس",
                "emoji": "🚫",
                "next": "death_devoured_by_demon",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "death_devoured_by_demon": {
        "text": "الشيطان المستدعى يغضب من عرقلتك. يكسرك ويبتلع شظاياك ليمتص وعيك. عذابك أبدي في معدة شيطانية.",
        "is_ending": True,
        "choices": []
    },
    "steal_weapon_soul": {
        "text": "تسرق روح رمح ملعون بجوارك. قوتك تتضاعف. يمكنك الآن التحدث بوضوح وإطلاق شرارات قاتلة.",
        "choices": [
            {
                "label": "اقتل النبيل واهرب",
                "emoji": "⚡",
                "next": "kill_noble",
                "points_reward": 2,
                "color": "danger"
            },
            {
                "label": "سيطرة على النبيل",
                "emoji": "🧠",
                "next": "control_noble",
                "points_reward": 1,
                "color": "primary"
            }
        ]
    },
    "heal_with_blood": {
        "text": "تمتص دماء اللص وتلتحم شقوقك. التاجر يلاحظ ذلك ويقرر رميك في فرن الصهر خوفا منك.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "💀",
                "next": "death_melted_down",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "summon_ash_demons": {
        "text": "شياطين الرماد تتجمع حولك. يرفعونك كقائدهم. أنت الآن تقود جيشا صغيرا نحو أقرب مدينة.",
        "choices": [
            {
                "label": "احرق المدينة",
                "emoji": "🔥",
                "next": "burn_city",
                "points_reward": 2,
                "color": "danger"
            },
            {
                "label": "ابحث عن جسد قوي",
                "emoji": "🧟",
                "next": "seek_strong_body",
                "points_reward": 1,
                "color": "primary"
            }
        ]
    },
    "wait_ruins": {
        "text": "تنتظر في الأنقاض. ساحر آخر يأتي ويختمك في صندوق رصاصي للأبد.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "💀",
                "next": "death_abandoned",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "grant_fire_power": {
        "text": "المتمرد يشعر بالنار تتدفق فيه. يقود ثورة دموية ضد الملك باستخدام قوتك الحارقة.",
        "choices": [
            {
                "label": "دمر جيش الملك",
                "emoji": "⚔️",
                "next": "destroy_kings_army",
                "points_reward": 2,
                "color": "danger"
            },
            {
                "label": "اقتل الملك بنفسك",
                "emoji": "👑",
                "next": "ending_b_dark_god",
                "points_reward": 3,
                "color": "danger"
            }
        ]
    },
    "burn_hand": {
        "text": "تحرق يده، يرميك بعيدا وتسقط في صدع عميق في الأرض.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "💀",
                "next": "death_rusty_grave",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "shatter_statue": {
        "text": "تحطم تمثال الساحر الجليدي وتهرب حرا في الهواء. قوتك السحرية تسمح لك بالطيران لبعض الوقت.",
        "choices": [
            {
                "label": "طر نحو قلعة الملك",
                "emoji": "🏰",
                "next": "fly_to_castle",
                "points_reward": 2,
                "color": "danger"
            },
            {
                "label": "طر نحو بركان",
                "emoji": "🌋",
                "next": "ending_a_broken_chains",
                "points_reward": 2,
                "color": "success"
            }
        ]
    },
    "stay_frozen": {
        "text": "الجليد لا يذوب أبدا. أنت محبوس في جليد أبدي.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "💀",
                "next": "death_buried_alive",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "tear_monster": {
        "text": "تمزق الوحش من الداخل وتطفو إلى سطح بحيرة جوفية، حيث تجد حضارة مفقودة تعبدك كإله.",
        "choices": [
            {
                "label": "اقبل الألوهية",
                "emoji": "🛐",
                "next": "ending_b_dark_god",
                "points_reward": 3,
                "color": "danger"
            },
            {
                "label": "ارشد عبادك للسطح",
                "emoji": "⬆️",
                "next": "lead_surface",
                "points_reward": 2,
                "color": "primary"
            }
        ]
    },
    "exit_peacefully": {
        "text": "تخرج من فمه، وحوش الأعماق تتجاهلك. تجلس في ظلام المياه.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "💀",
                "next": "death_ocean_bottom",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "open_hell_gate": {
        "text": "تفتح بوابة الجحيم. الشياطين تتدفق وتدمر العالم. تصبح أنت السيف الرئيسي لسيد الجحيم.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "👑",
                "next": "ending_b_dark_god",
                "points_reward": 0,
                "color": "danger"
            }
        ]
    },
    "sleep_power": {
        "text": "تنام. يجدك كاهن ويختمك في صندوق للأبد.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "💀",
                "next": "death_holy_seal",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "guard_orphan": {
        "text": "تحرس الطفل. يكبر ليصبح بطل النور الجديد. يواجه سيد الظلام في معركة ملحمية.",
        "choices": [
            {
                "label": "ضح بنفسك لحمايته",
                "emoji": "🛡️",
                "next": "ending_c_eternal_guardian",
                "points_reward": 3,
                "color": "success"
            },
            {
                "label": "اطلب منه الهرب",
                "emoji": "🏃",
                "next": "death_shattered_blade",
                "points_reward": 1,
                "color": "secondary"
            }
        ]
    },
    "corrupt_orphan": {
        "text": "يفسد الطفل ويصبح طاغية صغيرا. يتم اغتياله لاحقا، وترمى في البحر.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "💀",
                "next": "death_ocean_bottom",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "fake_repentance": {
        "text": "البطل يصدقك ويأخذك للمعبد. هناك تكتشف خدعتك.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "💀",
                "next": "death_holy_seal",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "rebel_hero": {
        "text": "تتمرد عليه. يكسرك بضربة من درعه المقدس.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "💀",
                "next": "death_shattered_blade",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "purge_blood": {
        "text": "تتخلص من دم البطل وتقتل القائد. تصبح حرا.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "🦅",
                "next": "ending_a_broken_chains",
                "points_reward": 3,
                "color": "success"
            }
        ]
    },
    "endure_burn": {
        "text": "النور يحرقك من الداخل حتى تتفتت.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "💀",
                "next": "death_melted_down",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "accept_forge_deal": {
        "text": "الحداد يصنع لك جسدا بشريا من الفولاذ الحي. تنهض كإنسان كامل لأول مرة منذ قرون.",
        "choices": [
            {
                "label": "المضي نحو الغروب",
                "emoji": "🌅",
                "next": "ending_d_human_again",
                "points_reward": 5,
                "color": "success",
                "requires_flag": "forge_secret"
            }
        ]
    },
    "kill_blacksmith": {
        "text": "تقتل الحداد. تضيع فرصتك الوحيدة للحرية. تبقى سلاحا ملعونا للأبد.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "💀",
                "next": "ending_b_dark_god",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "absorb_dragon_fire": {
        "text": "تمتص النار التنينية وتقتل التنين بطاقته نفسها. تصبح سيفا أسطوريا ناريا.",
        "choices": [
            {
                "label": "سيطر على العالم",
                "emoji": "🌍",
                "next": "ending_b_dark_god",
                "points_reward": 2,
                "color": "danger"
            }
        ]
    },
    "dark_sanctuary": {
        "text": "تصلان للملاذ المظلم. تصبحان أسياد الطائفة المظلمة.",
        "choices": [
            {
                "label": "احكم العالم الظلامي",
                "emoji": "👑",
                "next": "ending_b_dark_god",
                "points_reward": 2,
                "color": "danger"
            }
        ]
    },
    "fight_light": {
        "text": "تقاتلان قوى النور، لكنكما تهزمان وتقتلان.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "💀",
                "next": "death_holy_seal",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "spread_plague": {
        "text": "الطاعون يدمر العاصمة. تصبح إله الموت.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "👑",
                "next": "ending_b_dark_god",
                "points_reward": 2,
                "color": "danger"
            }
        ]
    },
    "seek_king": {
        "text": "تهاجم الملك، لكن حرسه الملكي يمزق جسدك الزومبي ويكسرك.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "💀",
                "next": "death_shattered_blade",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "pierce_sky": {
        "text": "تخترق السماء بقوتك. تنفجر طاقة الطقس، وتحررك من جسد السيف. وعيك يتحرر كروح طليقة.",
        "choices": [
            {
                "label": "نحو النجوم",
                "emoji": "✨",
                "next": "ending_a_broken_chains",
                "points_reward": 3,
                "color": "success"
            }
        ]
    },
    "wake_servant": {
        "text": "توقظ الشاب. يسيء استخدام الطقس وتنفجران معا.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "💀",
                "next": "death_shattered_blade",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "campaign_kingdom": {
        "text": "تقود حملة ضد المملكة وتسقطها. تصبح سيف الطاغية.",
        "choices": [
            {
                "label": "احكم للأبد",
                "emoji": "👑",
                "next": "ending_b_dark_god",
                "points_reward": 2,
                "color": "danger"
            }
        ]
    },
    "betray_for_stronger": {
        "text": "تغدر به لصالح قائد أقوى. القائد الجديد يكسرك خوفا من خيانتك له.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "💀",
                "next": "death_shattered_blade",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "cut_hand": {
        "text": "تقطع يده. يتركك وينزف حتى الموت. تبقى وحيدا في الغابة.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "💀",
                "next": "death_abandoned",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "help_summon": {
        "text": "تساعد في الاستدعاء. الشيطان يكافئك بجعلك سيفه المفضل.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "👿",
                "next": "ending_b_dark_god",
                "points_reward": 2,
                "color": "danger"
            }
        ]
    },
    "kill_noble": {
        "text": "تقتل النبيل وتهرب كروح في السيف. تصبح أسطورة حية.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "✨",
                "next": "ending_a_broken_chains",
                "points_reward": 2,
                "color": "success"
            }
        ]
    },
    "control_noble": {
        "text": "تسيطر عليه، لكن السحر يستهلك وعيك.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "💀",
                "next": "death_holy_seal",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "burn_city": {
        "text": "تحرق المدينة. تصبح إله الدمار.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "🔥",
                "next": "ending_b_dark_god",
                "points_reward": 2,
                "color": "danger"
            }
        ]
    },
    "seek_strong_body": {
        "text": "تبحث عن جسد قوي. تجد عملاقا وتستحوذ عليه.",
        "choices": [
            {
                "label": "حطم الجبال",
                "emoji": "⛰️",
                "next": "ending_b_dark_god",
                "points_reward": 2,
                "color": "danger"
            }
        ]
    },
    "destroy_kings_army": {
        "text": "تدمر الجيش وتتوج ملكا.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "👑",
                "next": "ending_b_dark_god",
                "points_reward": 2,
                "color": "danger"
            }
        ]
    },
    "fly_to_castle": {
        "text": "تطير للقلعة وتقتل الملك.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "🏰",
                "next": "ending_b_dark_god",
                "points_reward": 2,
                "color": "danger"
            }
        ]
    },
    "lead_surface": {
        "text": "ترشدهم للسطح وتصبح إلها.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "🛐",
                "next": "ending_b_dark_god",
                "points_reward": 2,
                "color": "danger"
            }
        ]
    },
    "ending_a_broken_chains": {
        "text": "نجحت أخيرا في تحطيم القيود التي ربطت وعيك بهذا المعدن الملعون. روحك تصعد، تاركة وراءها سيفا فارغا. لقد حققت النصر، لكن العالم فقد أداة كانت قادرة على تغيير التاريخ. هل الحرية تستحق ترك العالم لمصيره المجهول؟",
        "is_ending": True,
        "choices": []
    },
    "ending_b_dark_god": {
        "text": "لقد استهلكت أرواح الملوك والمحاربين، وأصبحت أنت الحاكم الفعلي للعالم متخفيا كسلاح. من يحملك يظن أنه سيدك، بينما هو مجرد بيدق في يدك الدموية. حققت مبتغاك، لكن هل هذا هو الخلود الذي كنت تتمناه، أم مجرد سجن بحجم العالم؟",
        "is_ending": True,
        "choices": []
    },
    "ending_c_eternal_guardian": {
        "text": "ضحيت بقوتك وطموحك لحماية براءة طفل سيصبح بطل النور. لقد صهرت طاقتك المظلمة لتصبح درعا أبديا له ولأحفاده. لم تعد وعيا مستقلا، بل صرخة صامتة للحماية. لقد أنقذت العالم، ولكن من سينقذك أنت من صمت الأبدية؟",
        "is_ending": True,
        "choices": []
    },
    "ending_d_human_again": {
        "text": "في نار الحداد الأسطوري السري، تشكل لك جسد من الفولاذ الحي واللحم السحري. لأول مرة منذ ألف عام، تتنفس، تشعر بنسيم الريح، وتنزف دما. لقد عدت إنسانا، خاسرا خلود السلاح وقوته، لكنك اكتسبت شيئا أعظم. هل ستستخدم حياتك الجديدة للخير، أم أن قلبك الفولاذي سيقودك للشر مجددا؟",
        "is_ending": True,
        "choices": []
    }
}
nodes.update(act_4_nodes)

story_json = {
    "id": "fb3_sentient_sword",
    "title": "نصل الخطايا",
    "world": "الفانتازيا",
    "world_type": "fantasy",
    "theme": "الظلام يحكم",
    "category": "الظلام يحكم",
    "summary": "أنت وعي محبوس في نصل ملعون. مصيرك يتأرجح بين التحرر، أو السيطرة على العالم، أو الاندثار كقطعة خردة.",
    "difficulty": "صعب جدا",
    "estimated_length": "طويلة جدا",
    "game_mode": "single",
    "perspective": {
        "id": "sentient_blade",
        "label": "السيف الملعون",
        "emoji": "🗡️",
        "description": "نصل واعٍ يبحث عن الحرية أو القوة",
        "start_node": "start"
    },
    "nodes": nodes
}

# Add dummy lines to force > 1000 lines count if needed.
# But JSON dumping with indent=4 of ~60 nodes with multiple choices usually exceeds 1000 lines.

import json
output_path = Path("data/stories/fb3_sentient_sword.json")
with output_path.open("w", encoding="utf-8") as f:
    json.dump(story_json, f, ensure_ascii=False, indent=4)

print(f"Generated successfully. Node count: {len(nodes)}")

missing_nodes = {
    "kill_companions": {
        "text": "يقوم الناهب الممسوس بقتل رفاقه وهم نيام. تستمتع بطعم دمائهم. في الصباح، يكتشف الحراس الجثث.",
        "choices": [
            {
                "label": "اجعله يقاتل الحراس",
                "emoji": "⚔️",
                "next": "fight_guards",
                "points_reward": 1,
                "color": "danger"
            },
            {
                "label": "اجعله ينتحر لتهرب",
                "emoji": "☠️",
                "next": "force_suicide",
                "points_reward": 2,
                "color": "primary"
            }
        ]
    },
    "go_blacksmith": {
        "text": "يتوجه الناهب لحداد مشبوه لبيعك. الحداد يلاحظ أنك لست مجرد سيف، ويحاول سرقتك من الناهب.",
        "choices": [
            {
                "label": "اترك الحداد يأخذك",
                "emoji": "🔨",
                "next": "black_market",
                "points_reward": 0,
                "color": "secondary"
            },
            {
                "label": "اقتل الحداد بالناهب",
                "emoji": "🩸",
                "next": "kill_blacksmith_early",
                "points_reward": 2,
                "color": "danger"
            }
        ]
    },
    "fight_guards": {
        "text": "يقاتل الناهب الحراس بشراسة، لكنهم يتكاثرون عليه ويمزقونه إربا. يرمونك في خندق مليء بالجثث.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "💀",
                "next": "death_rusty_grave",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "force_suicide": {
        "text": "تجبره على الانتحار وتهرب وعيك لتبحث عن جسد آخر. تضعف طاقتك تدريجيا في الهواء.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "💀",
                "next": "death_shattered_blade",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "kill_blacksmith_early": {
        "text": "يقتل الناهب الحداد. لكن الناهب يسقط ميتا بسبب سحر حماية كان الحداد يضعه. تنتظر في المحل.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "💀",
                "next": "death_rusty_grave",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    },
    "cut_armor": {
        "text": "تقطع الدرع، لكن الفارس يضربك بمطرقته. تتصدع، والشاب يموت.",
        "choices": [
            {
                "label": "النهاية",
                "emoji": "💀",
                "next": "death_shattered_fool",
                "points_reward": 0,
                "color": "secondary"
            }
        ]
    }
}
nodes.update(missing_nodes)

story_json["nodes"] = nodes
with output_path.open("w", encoding="utf-8") as f:
    json.dump(story_json, f, ensure_ascii=False, indent=4)

print(f"Generated successfully. Node count: {len(nodes)}")
