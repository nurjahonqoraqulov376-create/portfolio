"""
Ikki tilli kontent uchun yordamchi vositalar.

G'oya oddiy: har bir tarjima qilinadigan matn modelda ikki maydon bo'ladi —
`title_uz` va `title_en`. Joriy tilga qarab kerakligi tanlanadi. Shu tufayli
`.po`/`.mo` fayllar va gettext dasturi umuman kerak emas.
"""

from django.db import models
from django.utils.translation import get_language

FALLBACK_LANG = "uz"


def current_lang(fallback=FALLBACK_LANG):
    """Joriy tilning ikki harfli kodi: 'uz' yoki 'en'."""
    return (get_language() or fallback)[:2]


def translated(obj, field, fallback=FALLBACK_LANG):
    """
    `obj` ning `field` maydonini joriy tilda qaytaradi.

    Masalan translated(project, "title") -> project.title_uz yoki project.title_en.
    Tanlangan til bo'sh bo'lsa, fallback tilga (o'zbekchaga) qaytadi.
    """
    lang = current_lang(fallback)
    value = getattr(obj, f"{field}_{lang}", None)
    if value:
        return value
    return getattr(obj, f"{field}_{fallback}", "") or ""


class TranslatedMixin(models.Model):
    """
    `*_uz` / `*_en` maydonlari bor modellar uchun umumiy abstrakt model.

    Shablonda `{{ obj|tr:"title" }}`, Python kodida `obj.tr("title")`.
    """

    class Meta:
        abstract = True

    def tr(self, field):
        return translated(self, field)
