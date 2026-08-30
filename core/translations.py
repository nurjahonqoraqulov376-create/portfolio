"""
Interfeys (tugma, sarlavha, yorliq) matnlari.

Bazadagi kontent modellardagi `*_uz` / `*_en` maydonlarda saqlanadi, saytning
o'zgarmas yozuvlari esa shu yerda. Shablonda `{{ t.projects }}` ko'rinishida
ishlatiladi (`core.context_processors.site_context` orqali qo'shiladi).
"""

from .i18n import FALLBACK_LANG, current_lang

UI = {
    "uz": {
        # navigatsiya
        "nav_home": "Bosh sahifa",
        "nav_about": "Men haqimda",
        "nav_skills": "Ko'nikmalar",
        "nav_experience": "Tajriba",
        "nav_education": "Ta'lim",
        "nav_projects": "Loyihalar",
        "nav_blog": "Blog",
        "nav_contact": "Bog'lanish",
        "menu": "Menyu",
        "theme_toggle": "Mavzuni almashtirish",
        # hero
        "hero_greeting": "Assalomu alaykum, men",
        "available": "Ish takliflariga ochiq",
        "not_available": "Hozircha band",
        "download_cv": "CV yuklab olish",
        "view_projects": "Loyihalarni ko'rish",
        "contact_me": "Bog'lanish",
        "scroll_down": "Pastga",
        # bo'lim sarlavhalari
        "about_title": "Men haqimda",
        "about_subtitle": "Qisqacha tanishuv",
        "skills_title": "Ko'nikmalar",
        "skills_subtitle": "Men ishlatadigan texnologiyalar",
        "skills_count": "Ko'nikma",
        "experience_title": "Tajriba",
        "experience_subtitle": "Ish va amaliyot yo'lim",
        "education_title": "Ta'lim",
        "education_subtitle": "O'qish va kurslar",
        "projects_title": "Loyihalar",
        "featured_projects": "Tanlangan loyihalar",
        "projects_subtitle": "Men yaratgan ishlar",
        "blog_title": "Blog",
        "blog_subtitle": "O'rganganlarim haqida yozuvlar",
        "contact_title": "Bog'lanish",
        "contact_subtitle": "Savolingiz bormi? Yozing",
        # loyihalar
        "view_all": "Hammasini ko'rish",
        "view_details": "Batafsil",
        "source_code": "Kod",
        "live_demo": "Sayt",
        "filter_all": "Hammasi",
        "filter_by_tech": "Texnologiya bo'yicha",
        "no_projects": "Hozircha loyiha qo'shilmagan.",
        "tech_used": "Ishlatilgan texnologiyalar",
        "other_projects": "Boshqa loyihalar",
        "back_to_projects": "Loyihalarga qaytish",
        "started_at": "Boshlangan",
        # blog
        "read_more": "To'liq o'qish",
        "views": "ko'rish",
        "no_posts": "Hozircha maqola yo'q.",
        "back_to_blog": "Blogga qaytish",
        "related_posts": "O'xshash maqolalar",
        "published_at": "Chop etilgan",
        # kontakt formasi
        "form_name": "Ismingiz",
        "form_email": "Email",
        "form_subject": "Mavzu",
        "form_message": "Xabar",
        "form_send": "Yuborish",
        "form_success": "Rahmat! Xabaringiz yuborildi, tez orada javob beraman.",
        "form_error": "Formada xatolik bor, iltimos tekshirib qayta yuboring.",
        "form_too_many": (
            "Juda ko'p xabar yubordingiz. Bir ozdan keyin qayta urinib ko'ring "
            "yoki to'g'ridan-to'g'ri email orqali yozing."
        ),
        "contact_email": "Email",
        "contact_phone": "Telefon",
        "contact_location": "Manzil",
        "social_links": "Ijtimoiy tarmoqlar",
        # umumiy
        "footer_rights": "Barcha huquqlar himoyalangan.",
        "built_with": "Django bilan yozilgan",
        "page_of": "sahifa",
        "prev": "Oldingi",
        "next": "Keyingi",
        "not_found_title": "Sahifa topilmadi",
        "not_found_text": "Siz izlagan sahifa mavjud emas yoki ko'chirilgan.",
        "server_error_title": "Serverda xatolik",
        "server_error_text": "Kutilmagan xatolik yuz berdi. Birozdan so'ng urinib ko'ring.",
        "back_home": "Bosh sahifaga",
        "present": "hozirgacha",
        "language": "Til",
    },
    "en": {
        # navigation
        "nav_home": "Home",
        "nav_about": "About",
        "nav_skills": "Skills",
        "nav_experience": "Experience",
        "nav_education": "Education",
        "nav_projects": "Projects",
        "nav_blog": "Blog",
        "nav_contact": "Contact",
        "menu": "Menu",
        "theme_toggle": "Toggle theme",
        # hero
        "hero_greeting": "Hello, I'm",
        "available": "Open to opportunities",
        "not_available": "Currently unavailable",
        "download_cv": "Download CV",
        "view_projects": "View projects",
        "contact_me": "Get in touch",
        "scroll_down": "Scroll",
        # section titles
        "about_title": "About me",
        "about_subtitle": "A short introduction",
        "skills_title": "Skills",
        "skills_subtitle": "Technologies I work with",
        "skills_count": "Skills",
        "experience_title": "Experience",
        "experience_subtitle": "My professional path",
        "education_title": "Education",
        "education_subtitle": "Studies and courses",
        "projects_title": "Projects",
        "featured_projects": "Featured projects",
        "projects_subtitle": "Things I have built",
        "blog_title": "Blog",
        "blog_subtitle": "Notes on what I learn",
        "contact_title": "Contact",
        "contact_subtitle": "Have a question? Write to me",
        # projects
        "view_all": "View all",
        "view_details": "Details",
        "source_code": "Source",
        "live_demo": "Live",
        "filter_all": "All",
        "filter_by_tech": "Filter by technology",
        "no_projects": "No projects yet.",
        "tech_used": "Tech stack",
        "other_projects": "Other projects",
        "back_to_projects": "Back to projects",
        "started_at": "Started",
        # blog
        "read_more": "Read more",
        "views": "views",
        "no_posts": "No posts yet.",
        "back_to_blog": "Back to blog",
        "related_posts": "Related posts",
        "published_at": "Published",
        # contact form
        "form_name": "Your name",
        "form_email": "Email",
        "form_subject": "Subject",
        "form_message": "Message",
        "form_send": "Send",
        "form_success": "Thank you! Your message has been sent, I'll reply soon.",
        "form_error": "Please fix the errors below and try again.",
        "form_too_many": (
            "You have sent too many messages. Please try again later "
            "or email me directly."
        ),
        "contact_email": "Email",
        "contact_phone": "Phone",
        "contact_location": "Location",
        "social_links": "Social links",
        # common
        "footer_rights": "All rights reserved.",
        "built_with": "Built with Django",
        "page_of": "page",
        "prev": "Previous",
        "next": "Next",
        "not_found_title": "Page not found",
        "not_found_text": "The page you are looking for does not exist or has moved.",
        "server_error_title": "Server error",
        "server_error_text": "Something went wrong. Please try again a bit later.",
        "back_home": "Back home",
        "present": "present",
        "language": "Language",
    },
}


def ui(key, lang=None):
    """Bitta yorliqni olish: ui('nav_projects') -> 'Loyihalar'."""
    lang = lang or current_lang()
    table = UI.get(lang, UI[FALLBACK_LANG])
    return table.get(key, UI[FALLBACK_LANG].get(key, key))


def ui_table(lang=None):
    """Joriy til uchun butun lug'at (shablonlarda `t` nomi bilan)."""
    return UI.get(lang or current_lang(), UI[FALLBACK_LANG])


def choice_label(labels, value, lang=None):
    """
    Model `choices` yorliqlarini tarjima qilish uchun.

    labels = {"done": {"uz": "Tugallangan", "en": "Completed"}, ...}
    """
    lang = lang or current_lang()
    entry = labels.get(value)
    if not entry:
        return value
    return entry.get(lang) or entry.get(FALLBACK_LANG, value)
