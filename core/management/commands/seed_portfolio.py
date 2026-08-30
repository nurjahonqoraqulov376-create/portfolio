"""
Saytni ma'lumot bilan to'ldiradi.

    python manage.py seed_portfolio
    python manage.py seed_portfolio --flush   # avval eskisini o'chirib

Bu — Django'ning "management command" imkoniyati. `handle()` metodi
buyruq chaqirilganda ishlaydi. Yozuvlar `get_or_create` orqali qo'shilgani
uchun komandani bir necha marta ishga tushirish xavfsiz.

MUHIM: bu yerdagi matnlar — saytning haqiqiy kontenti. O'zgartirgandan keyin
`--flush` bilan qayta ishga tushiring, aks holda eski yozuvlar bazada qoladi.
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
    ("Git", "git", "#f05033"),
    ("HTML/CSS", "html-css", "#e34f26"),
    ("Telegram Bot API", "telegram-bot", "#2aabee"),
]

SKILL_CATEGORIES = [
    {
        "name_uz": "Backend",
        "name_en": "Backend",
        "icon": "🐍",
        "order": 1,
        "skills": [
            ("Python", 3),
            ("Django", 3),
            ("Django ORM", 3),
            ("Django REST Framework", 2),
        ],
    },
    {
        "name_uz": "Ma'lumotlar bazasi",
        "name_en": "Databases",
        "icon": "🗄️",
        "order": 2,
        "skills": [("PostgreSQL", 2), ("SQLite", 3)],
    },
    {
        "name_uz": "Vositalar",
        "name_en": "Tools",
        "icon": "🛠️",
        "order": 3,
        "skills": [("Git / GitHub", 3)],
    },
    {
        "name_uz": "Frontend asoslari",
        "name_en": "Frontend basics",
        "icon": "🎨",
        "order": 4,
        "skills": [("HTML / CSS", 3)],
    },
]

PROJECTS = [
    {
        "slug": "parda-dokoni-sayti",
        "title_uz": "Parda do'koni sayti",
        "title_en": "Curtain shop website",
        "summary_uz": "Parda do'koni uchun Django sayti: katalog, mahsulot rasmlari va admin paneldan boshqaruv.",
        "summary_en": "A Django site for a curtain shop: catalog, product photos and full admin control.",
        "description_uz": (
            "Parda sotadigan do'kon uchun yozgan birinchi to'liq loyiham.\n\n"
            "Saytda mahsulot katalogi bor: pardalar kategoriyalarga bo'lingan, har biri uchun "
            "rasm va batafsil sahifa mavjud. Mijoz yoqqan mahsulotini ko'rib, sayt orqali "
            "buyurtma yoki so'rov qoldirishi mumkin.\n\n"
            "Barcha kontent — kategoriyalar, mahsulotlar, rasmlar va kelib tushgan buyurtmalar — "
            "Django admin panelidan boshqariladi, ya'ni do'kon egasi kodga tegmasdan o'zi "
            "yangi mahsulot qo'sha oladi.\n\n"
            "Shu loyihada Django modellari, ForeignKey bog'lanishlari, rasm yuklash (ImageField va "
            "MEDIA sozlamalari), shablonlar va formalar bilan ishlashni amalda o'rgandim."
        ),
        "description_en": (
            "My first complete project, built for a shop that sells curtains.\n\n"
            "The site has a product catalog: curtains are split into categories, each with photos "
            "and a detail page. A customer can browse the products and leave an order or an "
            "enquiry through the site.\n\n"
            "Everything — categories, products, images and incoming orders — is managed from the "
            "Django admin, so the shop owner can add new products without touching any code.\n\n"
            "This project is where I really learned Django models, ForeignKey relations, image "
            "uploads (ImageField and MEDIA settings), templates and forms."
        ),
        "technologies": ["python", "django", "sqlite", "html-css"],
        # 🪟 (parda/deraza) emoji eski Windows shriftlarida bo'sh kvadrat bo'lib
        # chiqadi — shuning uchun keng qo'llab-quvvatlanadigan belgi olindi
        "icon": "🛍️",
        "github_url": "",
        "live_url": "",
        "status": Project.Status.DONE,
        "is_featured": True,
        "started_at": dt.date(2026, 2, 1),
        "order": 1,
    },
    {
        "slug": "parda-dokoni-telegram-bot",
        "title_uz": "Parda do'koni Telegram boti",
        "title_en": "Curtain shop Telegram bot",
        "summary_uz": "Shu do'kon uchun bot: katalog, buyurtma va adminga xabar. To'lov cheki qo'lda tasdiqlanadi.",
        "summary_en": "A bot for the same shop: catalog, orders and operator notifications, with manual receipt approval.",
        "description_uz": (
            "Parda do'koni sayti bilan bir vaqtda yozilgan Telegram bot — mijozlarning "
            "ko'pchiligi saytga emas, Telegramga o'rganib qolgani uchun.\n\n"
            "Bot katalogni ko'rsatadi, mijozdan buyurtmani qabul qiladi va yangi buyurtma "
            "haqida do'kon admini (operatori) ga darhol xabar yuboradi.\n\n"
            "To'lov bo'yicha ikki variant bor: onlayn va do'kondan olib ketishda naqd. "
            "Onlayn to'lov tizimi (Payme/Click kabi) hali integratsiya qilinmagan — mijoz "
            "to'lov chekining rasmini botga yuboradi, admin esa uni ko'rib qo'lda tasdiqlaydi. "
            "Keyingi bosqichda haqiqiy to'lov provayderini ulashni rejalashtiryapman.\n\n"
            "Bu loyihada Django'ni tashqi xizmat bilan bog'lash, foydalanuvchi bilan bosqichma-bosqich "
            "suhbat qurish va rasm (chek) qabul qilishni o'rgandim."
        ),
        "description_en": (
            "A Telegram bot written alongside the curtain shop website, because most of the "
            "customers live in Telegram rather than on websites.\n\n"
            "The bot shows the catalog, takes the customer's order and immediately notifies the "
            "shop admin (operator) about every new order.\n\n"
            "There are two payment options: online, and cash on pickup. A real payment provider "
            "(Payme/Click) is not integrated yet — the customer sends a photo of the payment "
            "receipt to the bot and the admin approves it manually. Connecting an actual payment "
            "provider is the next step I have planned.\n\n"
            "This project taught me how to connect Django to an external service, build a "
            "step-by-step conversation with the user, and handle image (receipt) uploads."
        ),
        "technologies": ["python", "telegram-bot", "django", "sqlite"],
        "icon": "🤖",
        "github_url": "",
        "live_url": "",
        "status": Project.Status.DONE,
        "is_featured": True,
        "started_at": dt.date(2026, 4, 1),
        "order": 2,
    },
]

# Blog bo'limi hozircha ishlatilmayapti — maqola yozilganda shu ro'yxatga
# qo'shiladi (yoki to'g'ridan-to'g'ri admin paneldan kiritiladi).
POSTS = []

# Ish tajribasi hali yo'q. Bo'lim bo'sh bo'lsa, bosh sahifada o'zi ko'rinmaydi
# (`templates/core/home.html` dagi `{% if experiences %}`).
EXPERIENCES = []

EDUCATIONS = [
    {
        "degree_uz": "Django backend dasturlash kursi",
        "degree_en": "Django backend development course",
        "institution_uz": "Najot Ta'lim",
        "institution_en": "Najot Ta'lim",
        "description_uz": (
            "Python asoslaridan Django'da to'liq loyiha yozishgacha: modellar va ORM, "
            "class-based viewlar, shablonlar, formalar, autentifikatsiya va REST API.\n\n"
            "Kurs 2026-yil sentabrida tugaydi."
        ),
        "description_en": (
            "From Python fundamentals to building a complete Django project: models and the ORM, "
            "class based views, templates, forms, authentication and REST APIs.\n\n"
            "The course finishes in September 2026."
        ),
        "start_date": dt.date(2025, 9, 1),
        "end_date": None,
        "order": 1,
    },
]


class Command(BaseCommand):
    help = "Portfolio kontentini bazaga yozadi"

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
                "full_name": "Nurjahon Qoraqulov",
                "headline_uz": "Junior Python / Django Dasturchi",
                "headline_en": "Junior Python / Django Developer",
                "bio_uz": (
                    "Salom! Men Nurjahon — Python va Django bilan backend dasturlashni o'rganyapman.\n\n"
                    "2025-yil sentabridan beri Najot Ta'limda Django backend yo'nalishida o'qiyman. "
                    "O'rganganlarimni faqat darsda qoldirmay, amalda sinab ko'rdim: parda do'koni "
                    "uchun to'liq sayt va shu do'konning Telegram botini yozdim — ikkalasi ham "
                    "Django admin panelidan boshqariladi.\n\n"
                    "Menga eng qiziq tomoni — ma'lumotlar bazasini to'g'ri loyihalash va Django ORM "
                    "bilan ishlash. Hozir REST API (DRF) va PostgreSQL bilan chuqurroq "
                    "shug'ullanyapman.\n\n"
                    "Amaliyot (stajirovka) yoki junior backend pozitsiyasiga ochiqman."
                ),
                "bio_en": (
                    "Hi! I'm Nurjahon, and I'm learning backend development with Python and Django.\n\n"
                    "Since September 2025 I have been studying Django backend development at "
                    "Najot Ta'lim. I didn't want what I learned to stay in the classroom, so I put "
                    "it into practice: I built a complete website for a curtain shop and a Telegram "
                    "bot for the same shop — both managed from the Django admin.\n\n"
                    "What I enjoy most is designing the database properly and working with the "
                    "Django ORM. Right now I'm going deeper into REST APIs (DRF) and PostgreSQL.\n\n"
                    "I'm open to an internship or a junior backend position."
                ),
                "location_uz": "Angor tumani, Surxondaryo viloyati",
                "location_en": "Angor district, Surkhandarya region, Uzbekistan",
                "email": "nurjahonqoraqulov376@gmail.com",
                "phone": "+998 99 986 71 99",
                "github": "https://github.com/nurjahonqoraqulov376-create",
                "linkedin": "",
                "telegram": "https://t.me/nurik_developerr07",
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
        for item in EXPERIENCES:
            Experience.objects.get_or_create(
                role_uz=item["role_uz"], company=item["company"], defaults=item
            )
        self.stdout.write(f"Tajriba: {Experience.objects.count()} ta")

    def _seed_education(self):
        for item in EDUCATIONS:
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
