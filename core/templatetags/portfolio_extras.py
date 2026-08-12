"""Shablonlar uchun maxsus filtr va teglar."""

from django import template
from django.urls import translate_url
from django.utils.safestring import mark_safe

from core.i18n import translated
from core.translations import ui

register = template.Library()


@register.filter(name="tr")
def tr(obj, field):
    """
    Ikki tilli maydonni joriy tilda chiqaradi.

    Ishlatilishi:  {{ project|tr:"title" }}  ->  title_uz yoki title_en
    """
    if obj is None:
        return ""
    return translated(obj, field)


@register.filter(name="tr_lines")
def tr_lines(obj, field):
    """
    Ikki tilli uzun matnni HTML paragraflarga ajratadi.

    Matndagi bo'sh qator yangi <p> boshlaydi. Kontent admin paneldan
    kelgani uchun HTML teglari qochiriladi (escape).
    """
    from django.utils.html import escape

    text = translated(obj, field) if obj is not None else ""
    blocks = [block.strip() for block in text.replace("\r\n", "\n").split("\n\n")]
    html = "".join(
        f"<p>{escape(block).replace(chr(10), '<br>')}</p>" for block in blocks if block
    )
    return mark_safe(html)


@register.simple_tag(name="ui")
def ui_tag(key):
    """Yorliqni kalit bo'yicha olish: {% ui "nav_projects" %}"""
    return ui(key)


@register.simple_tag(takes_context=True, name="url_for_lang")
def url_for_lang(context, lang_code):
    """
    Joriy sahifaning boshqa tildagi manzili.

    Django'ning `translate_url` funksiyasi i18n_patterns prefikslarini
    (masalan /en/) to'g'ri almashtiradi.
    """
    request = context.get("request")
    if request is None:
        return "/"
    return translate_url(request.get_full_path(), lang_code)


@register.simple_tag(takes_context=True, name="is_active")
def is_active(context, url_name, css_class="is-active"):
    """Menyudagi joriy sahifani belgilash uchun."""
    request = context.get("request")
    match = getattr(request, "resolver_match", None) if request else None
    if match and match.view_name == url_name:
        return css_class
    return ""


@register.filter(name="stars")
def stars(level):
    """Ko'nikma darajasini foizga aylantiradi (1..5 -> 20..100)."""
    try:
        return max(0, min(100, int(level) * 20))
    except (TypeError, ValueError):
        return 0
