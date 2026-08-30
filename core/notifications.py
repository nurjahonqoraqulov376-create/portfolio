"""
Sayt hodisalari haqida xabar berish — bitta kirish nuqtasi.

Har hodisa ikki joyga boradi:
  1. `Notification` jadvali -> admin paneldagi bildirishnomalar markazi
  2. Telegram (sozlangan bo'lsa) -> telefonga darhol

Nega bitta funksiya: hodisa turli joyda tug'iladi (kontakt formasi, CV
yuklash, 500 xato). Har birida "avval bazaga yoz, keyin Telegram'ga yubor,
xatolikni yut" deb takrorlamaslik uchun hammasi shu yerda.

Uchta muhim qoida bu modulda:

* **Hech qachon istisno ko'tarmaydi.** Bildirishnoma — yordamchi narsa; u
  ishlamagani uchun mehmonning so'rovi buzilmasligi kerak.
* **So'rovni ushlab turmaydi.** Telegram'ga murojaat alohida oqimda (thread)
  ketadi, aks holda Telegram sekinlashsa sahifa ham u bilan birga osilardi.
* **Toshib ketmaydi.** Takrorlanuvchi hodisalar (spam, xato) yangi qator
  ochmaydi va yangi Telegram xabari yubormaydi — sanoq oshadi, xolos.
"""

import logging
import threading
from datetime import timedelta

from django.conf import settings
from django.db.models import F
from django.utils import timezone

from . import telegram
from .models import Notification

logger = logging.getLogger(__name__)

# Takrorlanuvchi hodisalar shu oyna ichida bitta yozuvga yig'iladi.
THROTTLE_WINDOW_SECONDS = 600  # 10 daqiqa

# Bir xil hodisa qayta-qayta kelganda yangi yozuv ochmaydigan turlar.
# Kontakt xabari va CV yuklash bunga kirmaydi — ularning har biri qimmatli.
THROTTLED_KINDS = {Notification.KIND_SPAM, Notification.KIND_ERROR}

# Jadvalda saqlanadigan maksimal yozuv soni. Oshsa, eng eskilari o'chadi.
# SQLite doimiy diskda yotadi va u cheksiz emas.
MAX_ROWS = 1000

# Bir vaqtda nechta Telegram yuboruvchi oqim ishlashi mumkin.
#
# Nega chegara kerak: oqim arzon, lekin bepul emas — har biri xotira va
# tarmoq ulanishini ushlab turadi. Telegram javob bermay qolgan paytda
# oqimlar to'planib qoladi. Chegarasiz qoldirilsa, ko'p so'rov kelgan
# lahzada server oqimlar ostida qolib, saytning o'zi javob bermay qo'yardi.
# To'lib qolganda yangi xabar yuborilmaydi — lekin u baribir bazada bor,
# ya'ni admin panelda ko'rinadi va hech narsa yo'qolmaydi.
MAX_CONCURRENT_SENDS = 4
_send_slots = threading.Semaphore(MAX_CONCURRENT_SENDS)


def notify(kind, title, body="", link="", request=None, quiet=None):
    """
    Hodisani qayd etadi va Telegram'ga yuboradi.

    `quiet=True` — Telegram xabari ovozsiz keladi (telefon jiringlamaydi).
    Berilmasa, hodisa turiga qarab o'zi hal qilinadi: spam va oddiy
    ma'lumotlar jimgina, xabar/CV/xatolik ovozli.

    Butun tanasi `try` ichida: bu funksiya kontakt formasi va 500 xatosi
    ishlov beruvchisidan chaqiriladi — u yerda ko'tarilgan istisno mehmonga
    bo'sh ekran ko'rsatishi mumkin.
    """
    try:
        return _notify(kind, title, body, link, request, quiet)
    except Exception:
        logger.exception("Bildirishnoma yaratib bo'lmadi: %s", title)
        return None


def _notify(kind, title, body, link, request, quiet):
    if request is not None:
        context = describe_request(request)
        body = f"{body}\n\n{context}".strip() if body else context

    if kind in THROTTLED_KINDS:
        existing = _recent_duplicate(kind, title)
        if existing is not None:
            # Yangi qator ham, yangi Telegram xabari ham yo'q — faqat sanoq.
            # Aynan shu narsa formaga urilgan botni "bepul kuchaytirgich"
            # bo'lishdan to'xtatadi: 10 000 urinish = 1 yozuv, 1 xabar.
            Notification.objects.filter(pk=existing).update(
                repeat_count=F("repeat_count") + 1, is_read=False
            )
            return None

    notification = None
    try:
        notification = Notification.objects.create(
            kind=kind, title=title, body=body, link=link or ""
        )
        _prune()
    except Exception:
        # Baza yiqilgan bo'lsa ham Telegram'ga yuborishga urinib ko'ramiz —
        # aynan shunday paytda xabardor bo'lish eng kerak.
        logger.exception("Bildirishnomani bazaga yozib bo'lmadi")

    if quiet is None:
        quiet = kind not in Notification.IMPORTANT_KINDS

    _send_async(kind, title, body, link, quiet)
    return notification


def _recent_duplicate(kind, title):
    """
    Yaqinda shu turdagi va shu sarlavhali yozuv bo'lganmi.

    Bo'lsa, uning `pk` sini qaytaradi. Baza bilan bog'liq xatolik chiqsa
    `None` — u holda oddiy yo'l bilan yangi yozuv yaratiladi.
    """
    since = timezone.now() - timedelta(seconds=THROTTLE_WINDOW_SECONDS)
    try:
        return (
            Notification.objects.filter(kind=kind, title=title, created_at__gte=since)
            .values_list("pk", flat=True)
            .first()
        )
    except Exception:
        logger.exception("Takroriy bildirishnomani tekshirib bo'lmadi")
        return None


def _prune():
    """
    Jadval belgilangan chegaradan oshsa, eng eski yozuvlarni o'chiradi.

    Nega kerak: bildirishnomalar hech qachon o'z-o'zidan o'chmaydi. Bir
    yillik spam va xato yozuvlari SQLite faylini shishirib, Railway
    Volume'ini to'ldirib qo'yishi mumkin — bu esa saytni butunlay to'xtatadi.
    """
    try:
        total = Notification.objects.count()
        if total <= MAX_ROWS:
            return
        # Chegaradan oshgan qismni bir yo'la o'chiramiz. `pk__in` — SQLite
        # `DELETE ... LIMIT` ni qo'llab-quvvatlamagani uchun.
        extra = total - MAX_ROWS
        old_ids = list(
            Notification.objects.order_by("created_at").values_list("pk", flat=True)[:extra]
        )
        Notification.objects.filter(pk__in=old_ids).delete()
        logger.info("Eski bildirishnomalar tozalandi: %s ta", len(old_ids))
    except Exception:
        logger.exception("Eski bildirishnomalarni tozalab bo'lmadi")


def _send_async(kind, title, body, link, quiet):
    """
    Telegram'ga alohida oqimda yuboradi.

    Nega fonda: `urlopen` tarmoq chaqiruvi. Uni so'rov ichida bajarsak,
    Telegram sekinlashgan paytda kontakt formasini yuborgan mehmon shuncha
    vaqt kutib qoladi. Gunicorn'da oqimlar soni cheklangan (2 worker x 4
    thread), ya'ni bir nechta osilgan so'rov butun saytni band qilishi mumkin.

    Xato sahifasi (500) uchun bu ayniqsa muhim — u tez qaytishi shart.
    """
    if not telegram.is_configured():
        logger.info("Telegram sozlanmagan — bildirishnoma yuborilmadi")
        return

    # `blocking=False` — bo'sh joy bo'lmasa kutib turmaymiz. Kutish so'rovni
    # ushlab qolardi, ya'ni fonda yuborishdan ko'zlangan maqsad yo'qqa chiqardi.
    if not _send_slots.acquire(blocking=False):
        logger.warning(
            "Telegram yuboruvchi oqimlar band (%s ta) — bu xabar faqat "
            "admin panelda qoladi: %s",
            MAX_CONCURRENT_SENDS,
            title,
        )
        return

    def worker():
        try:
            telegram.send_notification(
                kind=kind, title=title, body=body, link=link, quiet=quiet
            )
        except Exception:
            logger.exception("Telegram oqimida kutilmagan xatolik")
        finally:
            # `finally` shart: joy qaytarilmasa, bir nechta xatodan keyin
            # yuborish butunlay to'xtab qolardi
            _send_slots.release()

    try:
        # daemon=True — server o'chayotganda bu oqim uni ushlab turmaydi
        threading.Thread(target=worker, name="telegram-notify", daemon=True).start()
    except Exception:
        _send_slots.release()
        logger.exception("Yuboruvchi oqimni boshlab bo'lmadi")


# ------------------------------------------------------- so'rov haqida kontekst


def client_ip(request):
    """
    Mijozning IP manzili.

    `X-Forwarded-For` sarlavhasiga faqat sayt proxy ortida turgani aniq
    bo'lgandagina ishonamiz (`TRUST_PROXY_IP`). Aks holda uni istalgan odam
    o'zi yozib yuborib, har so'rovda yangi IP ko'rsatib rate limit'ni
    chetlab o'tishi mumkin edi.
    """
    if getattr(settings, "TRUST_PROXY_IP", False):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if forwarded:
            # Faqat birinchisi — qolganini mijoz o'zi yozgan bo'lishi mumkin.
            # Uzunligini ham cheklaymiz: bu qiymat kesh kalitiga tushadi.
            return forwarded.split(",")[0].strip()[:45]
    return request.META.get("REMOTE_ADDR", "")[:45] or "noma'lum"


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

    Ichida `try`: `get_host()` noto'g'ri `Host` sarlavhasida istisno ko'taradi,
    va bu funksiya 500 xatosiga ishlov berishda ham chaqiriladi.
    """
    try:
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        referer = request.META.get("HTTP_REFERER", "")
        try:
            host = request.get_host().split(":")[0]
        except Exception:
            host = ""

        lang = getattr(request, "LANGUAGE_CODE", "") or "—"
        parts = [
            f"🌐 Til: {lang}",
            f"🔗 Manba: {_source(referer, host)}",
            f"🖥 Qurilma: {_device(user_agent)}",
            f"📍 IP: {client_ip(request)}",
        ]
        return "\n".join(parts)
    except Exception:
        logger.exception("So'rov ma'lumotini o'qib bo'lmadi")
        return ""
