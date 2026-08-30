"""
Kontakt formasidan kelgan xabarni Telegram'ga yuborish.

Nega alohida fayl: `views.py` faqat so'rovni boshqarsin, tashqi servis bilan
gaplashish mantiqi shu yerda tursin. Tashqi kutubxona (`requests`) ishlatilmadi —
standart `urllib` yetarli, requirements.txt ham o'smaydi.

Sozlash (ikki qadam):
  1. Telegram'da @BotFather ga `/newbot` yozing -> token oling
     -> `.env` ga TELEGRAM_BOT_TOKEN=... deb qo'ying.
  2. O'z botingizga Telegram'da `/start` bosing (bu SHART: bot o'zi
     birinchi bo'lib yoza olmaydi), so'ng chat ID'ni oling:
         python manage.py telegram_chat_id
     -> `.env` ga TELEGRAM_CHAT_ID=... deb qo'ying.

Diqqat: `@username` (masalan @nurik_developerr07) chat ID o'rniga ishlamaydi —
Bot API oddiy foydalanuvchiga faqat raqamli ID orqali yozadi.
"""

import json
import logging
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)

API_URL = "https://api.telegram.org/bot{token}/{method}"

# Telegram bitta xabarda 4096 belgidan ko'pini qabul qilmaydi.
# Formadagi chegara 4000 edi, lekin ism/email/mavzu ham qo'shilgani uchun
# yig'indi oshib ketishi mumkin — shuning uchun kesib qo'yamiz.
MAX_MESSAGE_LENGTH = 4000

TIMEOUT = 10  # soniya


def _escape(text):
    """HTML parse_mode uchun xavfli belgilarni almashtirish."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def is_configured():
    return bool(
        getattr(settings, "TELEGRAM_BOT_TOKEN", "")
        and getattr(settings, "TELEGRAM_CHAT_ID", "")
    )


def call_api(method, payload):
    """
    Telegram Bot API'ga POST so'rov.

    Javobni dict ko'rinishida qaytaradi. Xato bo'lsa istisno ko'taradi —
    uni chaqiruvchi tomon hal qiladi.
    """
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN sozlanmagan.")

    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        API_URL.format(token=token, method=method),
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


def _absolute(link):
    """Nisbiy havolani (`/admin/...`) to'liq URL'ga aylantiradi."""
    if not link or link.startswith(("http://", "https://")):
        return link
    domain = getattr(settings, "SITE_DOMAIN", "") or ""
    if not domain:
        return ""
    scheme = "http" if domain.startswith(("127.0.0.1", "localhost")) else "https"
    return f"{scheme}://{domain}{link}"


def format_notification(kind, title, body="", link=""):
    """Bildirishnomani Telegram xabari matniga aylantiradi."""
    from .models import Notification

    icon = Notification.KIND_STYLES.get(kind, ("🔔", ""))[0]

    text = f"{icon} <b>{_escape(title)}</b>"
    if body:
        body = _escape(body)
        if len(body) > MAX_MESSAGE_LENGTH:
            body = body[:MAX_MESSAGE_LENGTH] + "\n\n…(kesildi)"
        text += f"\n\n{body}"

    url = _absolute(link)
    if url:
        text += f'\n\n<a href="{_escape(url)}">🔗 Admin panelda ochish</a>'
    return text


def send_notification(kind, title, body="", link="", quiet=False):
    """
    Bildirishnomani Telegram'ga yuboradi. Muvaffaqiyatli bo'lsa True.

    `quiet=True` — xabar keladi, lekin telefon jiringlamaydi (statistika,
    spam kabi shovqinli hodisalar uchun).

    Xatolik yutiladi (faqat logga yoziladi): Telegram ishlamay qolsa ham
    hodisa baribir bazada saqlangan va admin panelda ko'rinadi.
    """
    if not is_configured():
        logger.info("Telegram sozlanmagan — bildirishnoma yuborilmadi")
        return False

    try:
        response = call_api(
            "sendMessage",
            {
                "chat_id": settings.TELEGRAM_CHAT_ID,
                "text": format_notification(kind, title, body, link),
                "parse_mode": "HTML",
                # Havolalarning katta ko'rinishlari xabarni chalg'itmasin
                "disable_web_page_preview": True,
                "disable_notification": bool(quiet),
            },
        )
    except urllib.error.HTTPError as error:
        # Telegram xato sababini javob tanasida tushuntiradi — logga chiqaramiz,
        # aks holda "nega kelmadi?" degan savolga javob topib bo'lmaydi.
        detail = error.read().decode("utf-8", "replace")[:300]
        logger.error("Telegram xatosi (HTTP %s): %s", error.code, detail)
        return False
    except Exception:
        logger.exception("Telegram'ga xabar yuborib bo'lmadi")
        return False

    if not response.get("ok"):
        logger.error("Telegram javobi: %s", response)
        return False

    return True
