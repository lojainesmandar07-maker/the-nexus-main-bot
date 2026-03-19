import json
import os

def generate_story():
    story = {
        "id": 110,
        "title": "جريمة في الظلال: متاهة الهاكر",
        "theme": "التحقيق الجنائي (عقول إجرامية)",
        "series": 10,
        "game_mode": "single",
        "description": "أنت المحقق السيبراني 'طارق'. مجموعة قراصنة تسمى (الديدان البيضاء) اخترقت شبكة بنك الدم الوطني وهددت بتدمير السجلات إذا لم تدفع الحكومة فدية. أنت الآن داخل خادمهم السري (الطرفية Terminal). لا يوجد أشخاص هنا، فقط أكواد، جدران نارية (Firewalls)، وملفات مشفرة. هدفك: اختيار أوامر الاختراق الصحيحة لاكتشاف موقعهم الحقيقي وإيقاف المؤقت قبل تدمير البيانات. (النقاط تمثل نسبة قوة المعالجة/الرام).",
        "start_scene": "scene_01_terminal",
        "image_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?q=80&w=600&auto=format&fit=crop",
        "scenes": [
            {
                "id": "scene_01_terminal",
                "title": "واجهة سطر الأوامر",
                "text": "> الاتصال بالخادم 192.168.x.x تم...\n> مرحباً بك في بوابة الديدان البيضاء.\n> المؤقت: 60 دقيقة لتدمير السجلات.\nيظهر أمامك ثلاث بوابات أمنية رقمية. البوابة (A) محمية بجدار ناري تقليدي. البوابة (B) تبدو كفخ عسل (Honeypot). البوابة (C) تحتوي على ملف مخفي بحجم كبير جداً. ماذا تفعل؟",
                "image_url": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?q=80&w=600&auto=format&fit=crop",
                "choices": [
                    {
                        "text": "> تنفيذ أمر اختراق القوة الغاشمة (Brute-force) على البوابة A",
                        "next_scene": "scene_02_bruteforce",
                        "color": "primary",
                        "points_reward": -5
                    },
                    {
                        "text": "> فحص البوابة B للتأكد من أنها فخ عسل قبل تجاهلها",
                        "next_scene": "scene_03_honeypot",
                        "color": "secondary",
                        "points_reward": 10
                    },
                    {
                        "text": "> سحب الملف المخفي من البوابة C لتحليله",
                        "next_scene": "scene_04_download",
                        "color": "danger",
                        "points_reward": 5
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_02_bruteforce",
                "title": "تنبيه النظام",
                "text": "> جاري فك التشفير... فشل.\n> تم رصد هجوم. تم رفع مستوى الأمان.\nخسرت 5 نقاط من المعالجة. البوابة A كانت تخفي مسار توجيه بسيط، لكنك الآن لفت انتباه النظام إليك. يجب أن تجد طريقة أهدأ للدخول.",
                "choices": [
                    {
                        "text": "> استخدام ثغرة الحقن (SQL Injection) على صفحة الدخول المجاورة",
                        "next_scene": "scene_05_sql_injection",
                        "color": "primary",
                        "points_reward": 10
                    },
                    {
                        "text": "> التوجه نحو البوابة C وتحميل الملف",
                        "next_scene": "scene_04_download",
                        "color": "secondary",
                        "points_reward": 0
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_03_honeypot",
                "title": "فخ العسل المزدوج",
                "text": "> فحص حزم البيانات... اكتمل.\nهذا فخ، لكنه فخ (مزدوج). الفخ يرسل إحداثيات وهمية لمن يخترقه، ولكنه يستقبل أوامر تحديث من جهاز رئيسي (Admin) كل 10 دقائق. إذا التقطت حزمة التحديث، قد تجد الـ IP الحقيقي للمقر.",
                "choices": [
                    {
                        "text": "> زراعة أداة تنصت (Sniffer) وانتظار التحديث القادم",
                        "next_scene": "scene_06_sniffer",
                        "color": "primary",
                        "points_reward": 15
                    },
                    {
                        "text": "> اختراق الفخ مباشرة لكشف الخادم المتصل",
                        "next_scene": "scene_fail_honeypot_trap",
                        "color": "danger",
                        "points_reward": -20
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_04_download",
                "title": "فيروس الفدية",
                "text": "> جاري التحميل... 99%...\n> تحذير: تم اكتشاف فيروس فدية (Ransomware) في الحزمة.\nالملف لم يكن بيانات، بل قنبلة موقوتة لتشفير جهازك أنت كمحقق!",
                "choices": [
                    {
                        "text": "> قطع الاتصال بالإنترنت فوراً للنجاة بحاسوبك",
                        "next_scene": "scene_fail_disconnected",
                        "color": "danger",
                        "points_reward": -100
                    },
                    {
                        "text": "> عزل الملف في صندوق حماية (Sandbox) وتحليله",
                        "next_scene": "scene_07_sandbox",
                        "color": "success",
                        "points_reward": 10
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_05_sql_injection",
                "title": "الحقن الناجح",
                "text": "> تم تجاوز التحقق من الهوية.\nأنت الآن تملك صلاحيات مستخدم عادي داخل النظام. لا يمكنك إيقاف المؤقت، ولكن يمكنك الوصول إلى سجل الدردشة الداخلي (Logs) للقراصنة.",
                "choices": [
                    {
                        "text": "> قراءة الدردشة بحثاً عن أسماء أو مواقع",
                        "next_scene": "scene_08_logs",
                        "color": "primary",
                        "points_reward": 10
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_06_sniffer",
                "title": "التقاط الهدف",
                "text": "> تم التقاط حزمة المشرف (Admin_Packet).\nالحزمة تحتوي على مفتاح تشفير وبصمة جغرافية. لكنها مشفرة بخوارزمية AES-256. تحتاج لكسرها بسرعة، المؤقت ينفد.",
                "choices": [
                    {
                        "text": "> إرسال الحزمة לחاسوبك الخارق (يتطلب 25 نقطة معالجة)",
                        "required_points": 25,
                        "next_scene": "scene_09_decrypt_success",
                        "color": "success",
                        "points_reward": 20
                    },
                    {
                        "text": "> محاولة فك التشفير محلياً على السيرفر الضعيف",
                        "next_scene": "scene_fail_timeout",
                        "color": "danger",
                        "points_reward": -10
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_07_sandbox",
                "title": "تشريح الفيروس",
                "text": "قمت بتشغيل الفيروس في بيئة آمنة معزولة. الفيروس يتواصل مع خادم تحكم وسيطرة (C&C Server) لإرسال مفاتيح التشفير. هذا الخادم هو ما تبحث عنه تماماً!",
                "choices": [
                    {
                        "text": "> تتبع مسار (Ping) لخادم التحكم",
                        "next_scene": "scene_10_ping_trace",
                        "color": "primary",
                        "points_reward": 15
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_08_logs",
                "title": "دردشة القراصنة",
                "text": "> user1: تم نقل الخادم إلى المخبأ الجديد في المنطقة الصناعية، شارع 4.\n> admin: جيد، المؤقت سيعمل تلقائياً. تأكد من مسح الـ Logs.\nلقد نسوا مسحها! لديك الموقع، لكنهم قد يمسحون السجلات في أي لحظة. كيف ستوقف التدمير قبل إرسال الشرطة؟",
                "choices": [
                    {
                        "text": "> حذف أداة التدمير (Wiper.exe) من النظام",
                        "next_scene": "scene_11_delete_wiper",
                        "color": "primary",
                        "points_reward": 10
                    },
                    {
                        "text": "> إرسال أمر إيقاف (Shutdown) للخادم بأكمله",
                        "next_scene": "scene_fail_shutdown_lock",
                        "color": "danger",
                        "points_reward": -15
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_09_decrypt_success",
                "title": "الـ IP الحقيقي",
                "text": "> تم فك التشفير. الموقع: شقة رقم 12، مبنى المهندسين.\nلديك الموقع الفعلي للقراصنة! كما حصلت على مفتاح المسؤول (Admin_Key). يمكنك الآن إلغاء تفعيل قنبلة البيانات نهائياً.",
                "choices": [
                    {
                        "text": "> إدخال مفتاح المسؤول وإيقاف المؤقت.",
                        "next_scene": "scene_win_perfect",
                        "required_points": 30,
                        "color": "success",
                        "points_reward": 20
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_10_ping_trace",
                "title": "خادم التحكم",
                "text": "تتبع المسار يوصلك إلى جهاز كمبيوتر متواجد في كافتيريا جامعة محلية. إنه جهاز عام تم اختراقه للتحكم في العملية! القرصان لا يزال متصلاً من جهازه الشخصي عبر الكافتيريا.",
                "choices": [
                    {
                        "text": "> تفعيل كاميرا الويب الخاصة بجهاز الكافتيريا فوراً",
                        "next_scene": "scene_12_webcam",
                        "color": "primary",
                        "points_reward": 15
                    },
                    {
                        "text": "> فصل الاتصال عنه لإنقاذ الملفات",
                        "next_scene": "scene_fail_hacker_escapes",
                        "color": "secondary",
                        "points_reward": 0
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_11_delete_wiper",
                "title": "مواجهة النظام",
                "text": "> خطأ: لا تملك صلاحيات Root لحذف هذا الملف.\nالنظام يرفض أمرك لأنك مستخدم عادي (SQL Injection). المؤقت يشير إلى 5 دقائق متبقية. يجب تصعيد الصلاحيات (Privilege Escalation) فوراً.",
                "choices": [
                    {
                        "text": "> تشغيل أداة ثغرة النواة (Kernel Exploit) لرفع الصلاحيات (يتطلب 30 نقطة معالجة)",
                        "required_points": 30,
                        "next_scene": "scene_13_root_access",
                        "color": "success",
                        "points_reward": 15
                    },
                    {
                        "text": "> محاولة تغيير كلمة مرور المدير بدلاً من ذلك",
                        "next_scene": "scene_fail_admin_alert",
                        "color": "danger",
                        "points_reward": -10
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_12_webcam",
                "title": "وجه القرصان",
                "text": "> تفعيل الكاميرا... تم.\nترى وجه شاب يرتدي قبعة، يكتب بسرعة على حاسوبه المحمول الموصول بجهاز الكافتيريا. تلتقط صورة واضحة لوجهه وتطابقها مع سجلات الجامعة.",
                "choices": [
                    {
                        "text": "إرسال الصورة واسم الطالب للشرطة لاقتحام الكافتيريا.",
                        "next_scene": "scene_win_arrest",
                        "color": "primary",
                        "points_reward": 20
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_13_root_access",
                "title": "صلاحيات الروت",
                "text": "> جاري التصعيد... تم الحصول على صلاحيات ROOT.\nأنت الآن تملك الخادم بالكامل. تلغي مؤقت التدمير، وتقوم بتحميل كل بيانات القراصنة وسجلات اتصالاتهم.",
                "choices": [
                    {
                        "text": "إرسال الموقع للشرطة وتدمير أجهزة القراصنة عن بعد.",
                        "next_scene": "scene_win_perfect",
                        "color": "success",
                        "points_reward": 20
                    }
                ],
                "is_ending": False
            },
            {
                "id": "scene_fail_honeypot_trap",
                "title": "النهاية: فخ النحل",
                "text": "اختراق الفخ مباشرة أدى إلى تفعيل بروتوكول تدمير ذاتي. لم ينفجر خادمهم، بل انفجر خادمك أنت بكمية هائلة من البيانات الخبيثة. تم تدمير أجهزتك وضاع الاتصال إلى الأبد. (لقد خسرت).",
                "choices": [],
                "is_ending": True
            },
            {
                "id": "scene_fail_disconnected",
                "title": "النهاية: انقطاع الاتصال",
                "text": "قطعت الإنترنت لإنقاذ نفسك. أنقذت حاسوبك، لكنك فقدت مسار الاختراق. تم تدمير بنك الدم الوطني بالكامل لأنك انسحبت. (فشل كبير).",
                "choices": [],
                "is_ending": True
            },
            {
                "id": "scene_fail_timeout",
                "title": "النهاية: انتهاء الوقت",
                "text": "السيرفر الضعيف لم يتمكن من كسر التشفير قبل انتهاء المؤقت. انتهى الوقت، وبدأت ملفات السجلات بالمسح التلقائي. القراصنة فازوا. (لقد خسرت).",
                "choices": [],
                "is_ending": True
            },
            {
                "id": "scene_fail_shutdown_lock",
                "title": "النهاية: إغلاق فاشل",
                "text": "إرسال أمر إيقاف التشغيل أثار ارتياب النظام. قام الخادم بفصل الشبكة الخارجية تلقائياً وأكمل عملية التدمير داخلياً. لم تستطع إيقافه. (لقد خسرت).",
                "choices": [],
                "is_ending": True
            },
            {
                "id": "scene_fail_admin_alert",
                "title": "النهاية: تنبيه المدير",
                "text": "محاولة تغيير الباسوورد أرسلت تنبيهاً فورياً للقرصان. دخل النظام وطردك في ثوانٍ. لقد خسرت الاتصال وأداة التدمير عملت عملها. (لقد خسرت).",
                "choices": [],
                "is_ending": True
            },
            {
                "id": "scene_fail_hacker_escapes",
                "title": "النهاية: هروب ذكي",
                "text": "فصلت الاتصال عنه. حافظت على بيانات بنك الدم، لكنك لم تملك وقتاً لمعرفة من هو. أخذ حاسوبه من الكافتيريا واختفى. سيعود مجدداً يوماً ما. (فشل في القبض عليه).",
                "choices": [],
                "is_ending": True
            },
            {
                "id": "scene_win_arrest",
                "title": "النهاية: القبض المباشر",
                "text": "الشرطة حاصرت الكافتيريا والقت القبض على الشاب. تم إجباره على إدخال الكود لإيقاف التدمير. أنقذت البيانات وقبضت على الفاعل بفضل تفكيرك السريع كهاكر أخلاقي. (لقد فزت ببراعة).",
                "choices": [],
                "is_ending": True
            },
            {
                "id": "scene_win_perfect",
                "title": "النهاية: السيد المطلق للشبكة",
                "text": "> إيقاف مؤقت التدمير: تم بنجاح.\n> استخراج ملفات القراصنة: تم.\n> إرسال الإحداثيات لفريق SWAT: تم.\nبصفتك (ROOT)، مسحت وجودك كشبح، تاركاً القراصنة ينتظرون تدميراً لم يحدث، قبل أن تقتحم الشرطة مخبأهم السري. ضربة ساحقة للجرائم السيبرانية في بلدك! (أفضل نهاية).",
                "choices": [],
                "is_ending": True
            }
        ]
    }

    os.makedirs("data/stories", exist_ok=True)
    with open("data/stories/sp_investigation_10.json", "w", encoding="utf-8") as f:
        json.dump(story, f, ensure_ascii=False, indent=4)
    print("Story 10 generated successfully!")

if __name__ == "__main__":
    generate_story()
