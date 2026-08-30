"""
Har bir shablonga avtomatik qo'shiladigan umumiy ma'lumotlar.

`config/settings.py` -> TEMPLATES -> context_processors ro'yxatida ulangan.
"""

from django.conf import settings

from .i18n import current_lang
from .translations import ui_table


def site_context(request):
    # Import shu yerda — modellar yuklanish tartibida aylanma import bo'lmasin
    from .models import Education, Experience, Profile

    lang = current_lang()
    return {
        "profile": Profile.objects.get_active(),
        "t": ui_table(lang),          # interfeys yozuvlari: {{ t.nav_projects }}
        "LANG": lang,                 # 'uz' yoki 'en'
        "LANGUAGES": settings.LANGUAGES,
        "OTHER_LANG": "en" if lang == "uz" else "uz",
        # Menyudagi havola bo'sh bo'limga olib bormasin: bo'lim faqat yozuv
        # bo'lganda chiziladi, demak havola ham shunda ko'rinishi kerak.
        "has_experience": Experience.objects.exists(),
        "has_education": Education.objects.exists(),
    }
