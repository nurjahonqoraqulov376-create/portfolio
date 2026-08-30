"""
Sayt hodisalari haqida xabar berish — bitta kirish nuqtasi.

Har hodisa ikki joyga boradi:
  1. `Notification` jadvali -> admin paneldagi bildirishnomalar markazi
  2. Telegram (sozlangan bo'lsa) -> telefonga darhol

Nega bitta funksiya: hodisa turli joyda tug'iladi (kontakt formasi, CV
yuklash, 500 xato). Har birida "avval bazaga yoz, keyin Telegram'ga yubor,
xatolikni yut" deb takrorlamaslik uchun hammasi shu yerda.

Muhim qoida: bu funksiya hech qachon istisno ko'tarmaydi. Bildirishnoma —
yordamchi narsa; u ishlamagani uchun mehmonning so'rovi buzilmasligi kerak.
"""

import logging

from . import telegram
from .models import Notification

logger = logging.getLogger(__name__)


def notify(kind, title, body="", link="", request=None, quiet=None):
    """
    Hodisani qayd etadi va Telegram'ga yuboradi.

    `quiet=True` — Telegram xabari ovozsiz keladi (telefon jiringlamaydi).
    Berilmasa, hodisa turiga qarab o'zi hal qilinadi: spam va oddiy
    ma'lumotlar jimgina, xabar/CV/xatolik ovozli.
    """
    if request is not None:
        context = describe_request(request)
        body = f"{body}\n\n{context}".strip() if body else context

    notification = None
    try:
        notification = Notification.objects.create(
            kind=kind, title=title, body=body, link=link or ""
        )
    except Exception:
        # Baza yiqilgan bo'lsa ham Telegram'ga yuborishga urinib ko'ramiz —
        # aynan shunday paytda xabardor bo'lish eng kerak.
        logger.exception("Bildirishnomani bazaga yozib bo'lmadi")

    if quiet is None:
        quiet = kind not in Notification.IMPORTANT_KINDS

    telegram.send_notification(
        kind=kind, title=title, body=body, link=link, quiet=quiet
    )
    return notification


# ------------------------------------------------------- so'rov haqida kontekst


def _client_ip(request):
    """Mijoz IP'si. Proxy sarlavhasiga faqat TRUST_PROXY_IP yoqilganda ishonamiz."""
    from django.conf import settings

    if getattr(settings, "TRUST_PROXY_IP", False):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "") or "noma'lum"


def _device(user_agent):
    """User-Agent'dan qurilma turini taxminlaydi (aniq emas, mo'ljal uchun)."""
    agent = user_agent.lower()
    if not agent:
        return "noma'lum"
    if "bot" in agent or "spider" in agent or "crawl" in agent:
        return "🤖 bot"
    if "mobile" in agent or "android" in agent or "iphone" in agent:
        return "📱 telefon"
    if "ipad" in agent or "tablet" in agent:
        return "📱 planshet"
    return "💻 kompyuter"


def _source(referer, host):
    """
    Mehmon qayerdan kelgani.

    Referer sarlavhasi mehmon brauzeri yuboradi — ishonchli emas, lekin
    "LinkedIn'danmi yoki Google'danmi" degan savolga taxminiy javob beradi.
    """
    if not referer:
        return "to'g'ridan-to'g'ri"
    if host and host in referer:
        return "sayt ichidan"

    known = {
        "google.": "Google",
        "yandex.": "Yandex",
        "t.me": "Telegram",
        "telegram.": "Telegram",
        "linkedin.": "LinkedIn",
        "github.": "GitHub",
        "facebook.": "Facebook",
        "instagram.": "Instagram",
        "twitter.": "Twitter/X",
        "x.com": "Twitter/X",
        "youtube.": "YouTube",
        "hh.uz": "hh.uz",
    }
    for needle, name in known.items():
        if needle in referer:
            return name
    return referer[:80]


def describe_request(request):
    """
    So'rov haqida qisqa ma'lumot: kim, qayerdan, qaysi tilda.

    Nega kerak: "yangi xabar keldi" degan quruq xabardan ko'ra "LinkedIn'dan
    kelgan, ingliz tilida yozgan, telefondan" degani javob berishdan oldin
    ancha ko'p narsa aytadi.
    """
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    referer = request.META.get("HTTP_REFERER", "")
    host = request.get_host().split(":")[0]

    lang = getattr(request, "LANGUAGE_CODE", "") or "—"
    parts = [
        f"🌐 Til: {lang}",
        f"🔗 Manba: {_source(referer, host)}",
        f"🖥 Qurilma: {_device(user_agent)}",
        f"📍 IP: {_client_ip(request)}",
    ]
    return "\n".join(parts)
