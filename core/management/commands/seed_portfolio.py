"""
Saytni namuna ma'lumot bilan to'ldiradi.

    python manage.py seed_portfolio
    python manage.py seed_portfolio --flush   # avval eskisini o'chirib

Bu — Django'ning "management command" imkoniyati. `handle()` metodi
buyruq chaqirilganda ishlaydi. Yozuvlar `get_or_create` orqali qo'shilgani
uchun komandani bir necha marta ishga tushirish xavfsiz.
"""

import datetime as dt

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from blog.models import Post
from core.models import Education, Experience, Profile, Skill, SkillCategory
from projects.models import Project, Technology

TECHNOLOGIES = [
    ("Python", "python", "#3776ab"),
    ("Django", "django", "#0c4b33"),
    ("Django REST Framework", "drf", "#a30000"),
    ("PostgreSQL", "postgresql", "#336791"),
    ("SQLite", "sqlite", "#0f80cc"),
    ("Redis", "redis", "#d82c20"),
    ("Celery", "celery", "#37814a"),
    ("Docker", "docker", "#2496ed"),
    ("Git", "git", "#f05033"),
    ("Nginx", "nginx", "#009639"),
    ("HTML/CSS", "html-css", "#e34f26"),
    ("JavaScript", "javascript", "#f7df1e"),
    ("Telegram Bot API", "telegram-bot", "#2aabee"),
    ("Linux", "linux", "#fcc624"),
]

SKILL_CATEGORIES = [
    {
        "name_uz": "Backend",
        "name_en": "Backend",
        "icon": "🐍",
        "order": 1,
        "skills": [
            ("Python", 4),
            ("Django", 4),
            ("Django REST Framework", 3),
            ("Django ORM", 4),
            ("Celery", 2),
        ],
    },
    {
        "name_uz": "Ma'lumotlar bazasi",
        "name_en": "Databases",
        "icon": "🗄️",
        "order": 2,
        "skills": [("PostgreSQL", 3), ("SQLite", 4), ("Redis", 2), ("SQL", 3)],
    },
    {
        "name_uz": "Vositalar va DevOps",
        "name_en": "Tools & DevOps",
        "icon": "🛠️",
        "order": 3,
        "skills": [("Git / GitHub", 4), ("Docker", 3), ("Linux", 3), ("Nginx", 2)],
    },
    {
        "name_uz": "Frontend asoslari",
        "name_en": "Frontend basics",
        "icon": "🎨",
        "order": 4,
        "skills": [("HTML / CSS", 3), ("JavaScript", 3), ("Bootstrap", 3)],
    },
]

PROJECTS = [
    {
        "slug": "blog-api",
        "title_uz": "Blog REST API",
        "title_en": "Blog REST API",
        "summary_uz": "DRF asosidagi blog API: JWT autentifikatsiya, izohlar, teglar va sahifalash.",
        "summary_en": "A blog API built with DRF: JWT auth, comments, tags and pagination.",
        "description_uz": (
            "Django REST Framework yordamida yozilgan to'liq blog API.\n\n"
            "Imkoniyatlari: foydalanuvchi ro'yxatdan o'tishi va JWT token orqali kirishi, "
            "maqola yaratish/tahrirlash/o'chirish, izohlar, teglar bo'yicha filtrlash va qidiruv.\n\n"
            "Loyihada ViewSet va Router, custom permission klasslari, serializer validatsiyasi "
            "hamda `select_related`/`prefetch_related` bilan so'rovlarni optimallashtirish o'rganildi. "
            "API hujjatlari drf-spectacular orqali avtomatik generatsiya qilinadi."
        ),
        "description_en": (
            "A complete blog API written with Django REST Framework.\n\n"
            "Features: user registration and JWT login, full CRUD for posts, comments, "
            "tag filtering and search.\n\n"
            "Along the way I practised ViewSets and Routers, custom permission classes, "
            "serializer validation and query optimisation with select_related/prefetch_related. "
            "API docs are generated automatically with drf-spectacular."
        ),
        "technologies": ["python", "django", "drf", "postgresql", "docker"],
        "github_url": "https://github.com/username/blog-api",
        "status": Project.Status.DONE,
        "is_featured": True,
        "started_at": dt.date(2025, 9, 1),
        "order": 1,
    },
    {
        "slug": "telegram-shop-bot",
        "title_uz": "Telegram do'kon boti",
        "title_en": "Telegram shop bot",
        "summary_uz": "Django admin orqali boshqariladigan Telegram bot: katalog, savat va buyurtma.",
        "summary_en": "A Telegram bot managed from Django admin: catalog, cart and orders.",
        "description_uz": (
            "Mahsulotlar Django admin panelidan boshqariladi, bot esa aiogram orqali "
            "foydalanuvchi bilan muloqot qiladi.\n\n"
            "Savatga qo'shish, buyurtma berish va operatorga xabar yuborish ishlaydi. "
            "Uzoq davom etadigan vazifalar (xabar yuborish, hisobot) Celery navbatiga tushadi.\n\n"
            "Bu loyihada Django'ni tashqi xizmat bilan bog'lash va webhook bilan ishlashni o'rgandim."
        ),
        "description_en": (
            "Products are managed from the Django admin while the bot talks to users via aiogram.\n\n"
            "It supports adding to cart, placing an order and notifying the operator. "
            "Long running work (broadcasts, reports) is pushed to a Celery queue.\n\n"
            "This project taught me how to connect Django to an external service and work with webhooks."
        ),
        "technologies": ["python", "django", "telegram-bot", "redis", "celery", "postgresql"],
        "github_url": "https://github.com/username/telegram-shop-bot",
        "status": Project.Status.DONE,
        "is_featured": True,
        "started_at": dt.date(2025, 11, 15),
        "order": 2,
    },
    {
        "slug": "task-manager",
        "title_uz": "Vazifalar menejeri",
        "title_en": "Task manager",
        "summary_uz": "Jamoaviy vazifalar taxtasi: loyihalar, muddatlar va rollar bo'yicha ruxsatlar.",
        "summary_en": "A team task board with projects, deadlines and role based permissions.",
        "description_uz": (
            "Klassik Django loyihasi: modellar, class-based viewlar, formalar va shablonlar.\n\n"
            "Har bir jamoada rollar bor (egasi, a'zo, kuzatuvchi) — ruxsatlar mixin'lar orqali "
            "tekshiriladi. Vazifalar holati bo'yicha filtrlanadi, muddati o'tganlari ajratib ko'rsatiladi.\n\n"
            "Testlar `django.test.TestCase` bilan yozilgan, coverage 80% dan yuqori."
        ),
        "description_en": (
            "A classic Django project: models, class based views, forms and templates.\n\n"
            "Each team has roles (owner, member, viewer) and permissions are checked through mixins. "
            "Tasks can be filtered by status and overdue ones are highlighted.\n\n"
            "Tests are written with django.test.TestCase, coverage is above 80%."
        ),
        "technologies": ["python", "django", "postgresql", "html-css", "javascript"],
        "github_url": "https://github.com/username/task-manager",
        "live_url": "",
        "status": Project.Status.DONE,
        "is_featured": True,
        "started_at": dt.date(2026, 1, 10),
        "order": 3,
    },
    {
        "slug": "url-shortener",
        "title_uz": "URL qisqartirgich",
        "title_en": "URL shortener",
        "summary_uz": "Qisqa havolalar xizmati: statistika, QR kod va Redis kesh.",
        "summary_en": "A short link service with click stats, QR codes and Redis caching.",
        "description_uz": (
            "Uzun havolani qisqa kodga aylantiradi va har bosishni hisoblaydi.\n\n"
            "Eng ko'p so'raladigan havolalar Redis'da keshlanadi, shuning uchun yo'naltirish "
            "bazaga murojaat qilmasdan ishlaydi. Har bir havola uchun QR kod generatsiya qilinadi.\n\n"
            "Bu yerda keshlash strategiyalari va Django'da signal'lar bilan ishlashni mashq qildim."
        ),
        "description_en": (
            "Turns a long URL into a short code and counts every click.\n\n"
            "Hot links are cached in Redis so redirects do not hit the database. "
            "A QR code is generated for every link.\n\n"
            "Here I practised caching strategies and Django signals."
        ),
        "technologies": ["python", "django", "redis", "sqlite"],
        "github_url": "https://github.com/username/url-shortener",
        "status": Project.Status.IN_PROGRESS,
        "is_featured": False,
        "started_at": dt.date(2026, 3, 5),
        "order": 4,
    },
    {
        "slug": "ecommerce-backend",
        "title_uz": "E-commerce backend",
        "title_en": "E-commerce backend",
        "summary_uz": "Onlayn do'kon uchun backend: katalog, savat, to'lov va buyurtma holati.",
        "summary_en": "Backend for an online store: catalog, cart, payments and order status.",
        "description_uz": (
            "Kategoriyalar, mahsulot variantlari (rang/o'lcham), savat va buyurtma jarayoni.\n\n"
            "To'lov provayderi bilan integratsiya sinov rejimida ishlaydi, buyurtma holati "
            "o'zgarganda mijozga email yuboriladi.\n\n"
            "Loyiha Docker Compose bilan ishga tushadi: Django, PostgreSQL va Nginx alohida konteynerda."
        ),
        "description_en": (
            "Categories, product variants (colour/size), cart and the checkout flow.\n\n"
            "Payment provider integration runs in sandbox mode and customers get an email "
            "whenever the order status changes.\n\n"
            "The project runs with Docker Compose: Django, PostgreSQL and Nginx in separate containers."
        ),
        "technologies": ["python", "django", "drf", "postgresql", "docker", "nginx"],
        "github_url": "https://github.com/username/ecommerce-backend",
        "status": Project.Status.IN_PROGRESS,
        "is_featured": True,
        "started_at": dt.date(2026, 4, 20),
        "order": 5,
    },
    {
        "slug": "portfolio-site",
        "title_uz": "Shu portfolio sayti",
        "title_en": "This portfolio site",
        "summary_uz": "Ikki tilli portfolio: kontent admin paneldan boshqariladi.",
        "summary_en": "A bilingual portfolio where all content is managed from the admin panel.",
        "description_uz": (
            "Siz hozir ko'rib turgan sayt. Django'da yozilgan, barcha kontent "
            "(profil, ko'nikmalar, loyihalar, maqolalar) admin paneldan tahrirlanadi.\n\n"
            "Ikki tillilik `.po` fayllarsiz amalga oshirilgan: har matn modelda `*_uz` va `*_en` "
            "maydonlarda saqlanadi, interfeys yozuvlari esa oddiy Python lug'atida.\n\n"
            "Qo'shimcha: JSON API endpoint, sitemap.xml, kontakt formasi va dark/light mavzu."
        ),
        "description_en": (
            "The site you are looking at right now. Built with Django, with every piece of content "
            "(profile, skills, projects, posts) editable from the admin panel.\n\n"
            "Bilingual support works without .po files: each text lives in `*_uz` and `*_en` model "
            "fields while interface labels sit in a plain Python dictionary.\n\n"
            "Extras: a JSON API endpoint, sitemap.xml, a contact form and a dark/light theme."
        ),
        "technologies": ["python", "django", "sqlite", "html-css", "javascript"],
        "github_url": "https://github.com/username/portfolio",
        "status": Project.Status.DONE,
        "is_featured": True,
        "started_at": dt.date(2026, 8, 1),
        "order": 6,
    },
]

POSTS = [
    {
        "slug": "django-orm-select-related",
        "title_uz": "Django ORM: select_related va prefetch_related farqi",
        "title_en": "Django ORM: select_related vs prefetch_related",
        "excerpt_uz": "N+1 muammosi nima va uni ikki metod bilan qanday hal qilinadi.",
        "excerpt_en": "What the N+1 problem is and how these two methods solve it.",
        "body_uz": (
            "Django ORM juda qulay, lekin ehtiyot bo'lmasa bitta sahifa uchun yuzlab so'rov yuborishi mumkin. "
            "Bu \"N+1 so'rov\" muammosi deyiladi.\n\n"
            "`select_related` — ForeignKey va OneToOne uchun. U SQL JOIN qiladi, ya'ni bitta so'rovda "
            "bog'liq jadvalni ham olib keladi.\n\n"
            "`prefetch_related` — ManyToMany va teskari ForeignKey uchun. U alohida so'rov yuboradi, "
            "keyin natijani Python tomonda birlashtiradi.\n\n"
            "Amaliy maslahat: `django-debug-toolbar` o'rnating va har sahifada nechta so'rov "
            "ketayotganini ko'ring. Shu portfolio saytida ham loyihalar ro'yxati `prefetch_related` "
            "bilan olinadi — aks holda har bir loyihaning texnologiyalari uchun alohida so'rov ketardi."
        ),
        "body_en": (
            "The Django ORM is convenient, but without care a single page can fire hundreds of queries. "
            "This is the \"N+1 query\" problem.\n\n"
            "`select_related` is for ForeignKey and OneToOne. It performs a SQL JOIN and fetches the "
            "related table in the same query.\n\n"
            "`prefetch_related` is for ManyToMany and reverse ForeignKey. It runs a second query and "
            "joins the results in Python.\n\n"
            "Practical tip: install django-debug-toolbar and watch the query count on every page. "
            "On this very portfolio the project list uses prefetch_related — otherwise each project "
            "would trigger its own query for technologies."
        ),
        "tags": ["django", "python", "postgresql"],
        "days_ago": 12,
    },
    {
        "slug": "django-settings-env",
        "title_uz": "SECRET_KEY ni koddan qanday chiqarish kerak",
        "title_en": "Getting SECRET_KEY out of your code",
        "excerpt_uz": "`.env` fayli, python-dotenv va nima uchun sozlamalarni ajratish muhim.",
        "excerpt_en": "The .env file, python-dotenv, and why separating settings matters.",
        "body_uz": (
            "`startproject` bergan `settings.py` da SECRET_KEY to'g'ridan-to'g'ri kodda turadi. "
            "Uni GitHub'ga yuklash — eng ko'p uchraydigan xato.\n\n"
            "Yechim oddiy: qiymatlarni `.env` fayliga chiqaring, `.gitignore` ga qo'shing va "
            "`python-dotenv` orqali o'qing. DEBUG ham shu yerdan kelishi kerak — "
            "produksiyada DEBUG=True qolishi xavfsizlik teshigi.\n\n"
            "Men shu portfolio loyihasida aynan shunday qildim: `.env.example` faylini "
            "repozitoriyda qoldirdim, haqiqiy `.env` esa faqat kompyuterimda."
        ),
        "body_en": (
            "The settings.py produced by startproject keeps SECRET_KEY right in the code. "
            "Pushing that to GitHub is one of the most common beginner mistakes.\n\n"
            "The fix is simple: move values into a .env file, add it to .gitignore and read it with "
            "python-dotenv. DEBUG belongs there too — leaving DEBUG=True in production is a security hole.\n\n"
            "That is exactly what I did in this portfolio project: .env.example stays in the repo "
            "while the real .env never leaves my machine."
        ),
        "tags": ["django", "python", "linux"],
        "days_ago": 26,
    },
    {
        "slug": "django-i18n-without-gettext",
        "title_uz": "Gettext'siz ikki tilli sayt qilish",
        "title_en": "A bilingual site without gettext",
        "excerpt_uz": "Windows'da .po fayllar bilan ovora bo'lmasdan uz/en saytni qanday qildim.",
        "excerpt_en": "How I built a uz/en site without fighting .po files on Windows.",
        "body_uz": (
            "Django'ning standart tarjima tizimi `.po`/`.mo` fayllarga tayanadi, ular esa "
            "GNU gettext dasturini talab qiladi. Windows'da uni o'rnatish alohida ish.\n\n"
            "Muqobil yo'l: tarjima qilinadigan kontentni bazaning o'zida saqlash. Har matn uchun "
            "ikki maydon — `title_uz` va `title_en`. Joriy tilni `get_language()` qaytaradi, "
            "kichik yordamchi funksiya keraklisini tanlaydi.\n\n"
            "Interfeys yozuvlari (tugmalar, sarlavhalar) esa oddiy Python lug'atida turadi. "
            "Til almashtirish uchun `i18n_patterns` va `LocaleMiddleware` ishlatiladi — ular "
            "tarjima fayllarisiz ham to'liq ishlaydi.\n\n"
            "Natija: kontentni admin paneldan ikki tilda tahrirlash mumkin, hech qanday "
            "qo'shimcha dastur o'rnatish shart emas."
        ),
        "body_en": (
            "Django's standard translation system relies on .po/.mo files, which in turn require "
            "the GNU gettext toolchain. Installing that on Windows is a project of its own.\n\n"
            "An alternative: keep translatable content in the database itself. Two fields per text — "
            "title_uz and title_en. get_language() tells you the active language and a tiny helper "
            "picks the right one.\n\n"
            "Interface labels (buttons, headings) live in a plain Python dictionary. Language "
            "switching still uses i18n_patterns and LocaleMiddleware, which work fine without any "
            "translation files.\n\n"
            "The result: content is editable in both languages from the admin, with no extra "
            "tooling to install."
        ),
        "tags": ["django", "python", "html-css"],
        "days_ago": 3,
    },
]


class Command(BaseCommand):
    help = "Portfolio'ni namuna ma'lumot bilan to'ldiradi"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Avval mavjud kontentni o'chirib tashlaydi (foydalanuvchilarga tegmaydi)",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write("Eski kontent o'chirilmoqda…")
            Post.objects.all().delete()
            Project.objects.all().delete()
            Technology.objects.all().delete()
            Skill.objects.all().delete()
            SkillCategory.objects.all().delete()
            Experience.objects.all().delete()
            Education.objects.all().delete()
            Profile.objects.all().delete()

        profile = self._seed_profile()
        technologies = self._seed_technologies()
        self._seed_skills()
        self._seed_experience()
        self._seed_education()
        self._seed_projects(technologies)
        self._seed_posts(technologies)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nTayyor! Profil: {profile.full_name}, "
                f"{Project.objects.count()} loyiha, {Post.objects.count()} maqola, "
                f"{Skill.objects.count()} ko'nikma.\n"
                "Endi `python manage.py createsuperuser` va `runserver` qiling."
            )
        )

    # ------------------------------------------------------------------ qismlar

    def _seed_profile(self):
        profile, created = Profile.objects.get_or_create(
            defaults={
                "full_name": "Ismingiz Familiyangiz",
                "headline_uz": "Django Backend Dasturchi",
                "headline_en": "Django Backend Developer",
                "bio_uz": (
                    "Salom! Men backend dasturlash bilan shug'ullanaman va asosiy vositam — "
                    "Python hamda Django.\n\n"
                    "Men uchun eng qiziq qismi: ma'lumotlar bazasini to'g'ri loyihalash, "
                    "toza va tushunarli API yozish, hamda kodni tez va ishonchli qilish. "
                    "Har bir yangi loyihada o'zim uchun bitta yangi mavzuni ochishga harakat qilaman — "
                    "kesh, navbatlar, Docker yoki testlar bo'ladimi.\n\n"
                    "Hozir REST API va Docker bilan chuqurroq ishlayapman, jamoada ishlash "
                    "yoki junior backend pozitsiyasiga ochiqman."
                ),
                "bio_en": (
                    "Hi! I build backends, and my main tools are Python and Django.\n\n"
                    "What I enjoy most: designing the database properly, writing clean and readable "
                    "APIs, and making code fast and reliable. With every new project I try to open up "
                    "one new topic for myself — caching, queues, Docker or testing.\n\n"
                    "Right now I am going deeper into REST APIs and Docker, and I am open to "
                    "team work or a junior backend position."
                ),
                "location_uz": "Toshkent, O'zbekiston",
                "location_en": "Tashkent, Uzbekistan",
                "email": "sizning@email.uz",
                "phone": "+998 90 123 45 67",
                "github": "https://github.com/username",
                "linkedin": "https://linkedin.com/in/username",
                "telegram": "https://t.me/username",
                "is_available": True,
            }
        )
        self.stdout.write(f"Profil: {'qo`shildi' if created else 'mavjud edi'}")
        return profile

    def _seed_technologies(self):
        technologies = {}
        for name, slug, color in TECHNOLOGIES:
            tech, _ = Technology.objects.get_or_create(
                slug=slug, defaults={"name": name, "color": color}
            )
            technologies[slug] = tech
        self.stdout.write(f"Texnologiyalar: {len(technologies)} ta")
        return technologies

    def _seed_skills(self):
        for data in SKILL_CATEGORIES:
            category, _ = SkillCategory.objects.get_or_create(
                name_uz=data["name_uz"],
                defaults={
                    "name_en": data["name_en"],
                    "icon": data["icon"],
                    "order": data["order"],
                },
            )
            for index, (skill_name, level) in enumerate(data["skills"], start=1):
                Skill.objects.get_or_create(
                    category=category,
                    name=skill_name,
                    defaults={"level": level, "order": index},
                )
        self.stdout.write(f"Ko'nikmalar: {Skill.objects.count()} ta")

    def _seed_experience(self):
        items = [
            {
                "role_uz": "Junior Backend Dasturchi (amaliyot)",
                "role_en": "Junior Backend Developer (internship)",
                "company": "IT Company",
                "description_uz": (
                    "Django loyihasida jamoa bilan ishladim: yangi modellar va API endpointlar qo'shdim, "
                    "mavjud so'rovlarni optimallashtirdim.\n\n"
                    "Code review jarayonida qatnashdim va birinchi marta haqiqiy git flow bilan ishladim."
                ),
                "description_en": (
                    "Worked on a Django project with a team: added new models and API endpoints, "
                    "optimised existing queries.\n\n"
                    "Took part in code review and worked with a real git flow for the first time."
                ),
                "start_date": dt.date(2026, 2, 1),
                "end_date": None,
                "order": 1,
            },
            {
                "role_uz": "Freelance dasturchi",
                "role_en": "Freelance developer",
                "company": "O'z loyihalarim",
                "description_uz": (
                    "Kichik biznes uchun Telegram botlar va oddiy sayt backendlarini yozdim.\n\n"
                    "Mijoz bilan talablarni aniqlash, muddatga yetkazish va loyihani serverga "
                    "joylashtirishni mustaqil bajardim."
                ),
                "description_en": (
                    "Built Telegram bots and simple website backends for small businesses.\n\n"
                    "Handled requirements gathering, deadlines and deployment on my own."
                ),
                "start_date": dt.date(2025, 6, 1),
                "end_date": dt.date(2026, 1, 31),
                "order": 2,
            },
        ]
        for item in items:
            Experience.objects.get_or_create(
                role_uz=item["role_uz"], company=item["company"], defaults=item
            )
        self.stdout.write(f"Tajriba: {Experience.objects.count()} ta")

    def _seed_education(self):
        items = [
            {
                "degree_uz": "Backend dasturlash kursi (Python/Django)",
                "degree_en": "Backend development course (Python/Django)",
                "institution_uz": "IT Akademiya",
                "institution_en": "IT Academy",
                "description_uz": (
                    "Python asoslaridan Django'da to'liq loyiha yozishgacha: ORM, autentifikatsiya, "
                    "REST API, testlar va deploy."
                ),
                "description_en": (
                    "From Python basics to shipping a full Django project: ORM, authentication, "
                    "REST APIs, tests and deployment."
                ),
                "start_date": dt.date(2025, 3, 1),
                "end_date": None,
                "order": 1,
            },
            {
                "degree_uz": "Axborot texnologiyalari",
                "degree_en": "Information Technology",
                "institution_uz": "Universitet",
                "institution_en": "University",
                "description_uz": "Dasturlash asoslari, algoritmlar va ma'lumotlar bazalari.",
                "description_en": "Programming fundamentals, algorithms and databases.",
                "start_date": dt.date(2022, 9, 1),
                "end_date": dt.date(2026, 6, 30),
                "order": 2,
            },
        ]
        for item in items:
            Education.objects.get_or_create(
                degree_uz=item["degree_uz"],
                institution_uz=item["institution_uz"],
                defaults=item,
            )
        self.stdout.write(f"Ta'lim: {Education.objects.count()} ta")

    def _seed_projects(self, technologies):
        for data in PROJECTS:
            # M2M maydonni `defaults` ga bera olmaymiz — uni ajratib olamiz
            fields = {k: v for k, v in data.items() if k != "technologies"}
            project, _ = Project.objects.get_or_create(
                slug=fields["slug"], defaults=fields
            )
            project.technologies.set(
                [technologies[slug] for slug in data["technologies"] if slug in technologies]
            )
        self.stdout.write(f"Loyihalar: {Project.objects.count()} ta")

    def _seed_posts(self, technologies):
        now = timezone.now()
        for data in POSTS:
            fields = {k: v for k, v in data.items() if k not in {"tags", "days_ago"}}
            post, _ = Post.objects.get_or_create(
                slug=fields["slug"],
                defaults={
                    **fields,
                    "published_at": now - dt.timedelta(days=data["days_ago"]),
                    "is_published": True,
                },
            )
            post.tags.set(
                [technologies[slug] for slug in data["tags"] if slug in technologies]
            )
        self.stdout.write(f"Maqolalar: {Post.objects.count()} ta")
