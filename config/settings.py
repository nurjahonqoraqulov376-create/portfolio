"""
Django sozlamalari — shaxsiy portfolio loyihasi.

Maxfiy qiymatlar (SECRET_KEY, DEBUG, ALLOWED_HOSTS) `.env` faylidan o'qiladi.
Namuna uchun `.env.example` fayliga qarang.
"""

from pathlib import Path

from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# .env faylini o'qiymiz (fayl bo'lmasa ham xato bermaydi)
load_dotenv(BASE_DIR / ".env")


def env(name, default=""):
    """Muhit o'zgaruvchisini o'qish uchun qisqa yordamchi."""
    return os.environ.get(name, default)


def env_bool(name, default=False):
    return env(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def env_list(name, default=""):
    return [item.strip() for item in env(name, default).split(",") if item.strip()]


# O'zgaruvchan ma'lumotlar — SQLite bazasi va admin orqali yuklangan media
# fayllar — shu papkada yashaydi. Railway kabi hostinglarda konteyner diski
# har deployda tozalanadi, shuning uchun u yerda DATA_DIR doimiy Volume'ga
# (masalan `/app/data`) qaratiladi. Lokalda bo'sh qoladi -> loyiha papkasi.
DATA_DIR = Path(env("DATA_DIR") or BASE_DIR)
DATA_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------- xavfsizlik

DEBUG = env_bool("DEBUG", True)

SECRET_KEY = env("SECRET_KEY")

# `.env` dagi namuna kalitlar. Ular repozitoriyda ochiq turadi, ya'ni ularni
# bilgan odam sessiya cookie'sini va parol tiklash havolasini o'zi yasay oladi.
_INSECURE_KEYS = {
    "dev-only-insecure-key-almashtiring",
    "dev-l0kal-kalit-almashtiring-produksiyada",
}

if DEBUG:
    # Lokal ishlaganda kalit bo'lmasa ham loyiha ishga tushaversin
    SECRET_KEY = SECRET_KEY or "dev-only-insecure-key-almashtiring"
elif not SECRET_KEY or SECRET_KEY in _INSECURE_KEYS or len(SECRET_KEY) < 50:
    # Produksiyada jim o'tib ketmaydi — ataylab yiqiladi.
    # Yangi kalit:
    #   python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
    from django.core.exceptions import ImproperlyConfigured

    raise ImproperlyConfigured(
        "DEBUG=False bo'lganda kuchli SECRET_KEY majburiy. "
        "`.env` faylida kamida 50 belgili tasodifiy kalit bering."
    )

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1,[::1]")

CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")

# Railway har bir servisga `xxx.up.railway.app` domenini beradi va uni shu
# o'zgaruvchida uzatadi. Qo'lda yozib yurmaslik uchun avtomatik qo'shamiz.
# O'z domeningizni ALLOWED_HOSTS/CSRF_TRUSTED_ORIGINS orqali qo'shasiz.
_railway_domain = env("RAILWAY_PUBLIC_DOMAIN")
if _railway_domain:
    if _railway_domain not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(_railway_domain)
    if f"https://{_railway_domain}" not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(f"https://{_railway_domain}")

# Sayt reverse-proxy (nginx, Cloudflare) ortida tursagina yoqing.
# Yoqilgan bo'lsa mijoz IP'si `X-Forwarded-For` sarlavhasidan olinadi.
# Proxy bo'lmasa yoqmang: bu sarlavhani istalgan odam o'zi yozib yuborishi
# mumkin, ya'ni rate limit'ni chetlab o'tish oson bo'lib qoladi.
TRUST_PROXY_IP = env_bool("TRUST_PROXY_IP", False)

if not DEBUG:
    # Produksiyada HTTPS bilan bog'liq qat'iylashtirish.
    # `manage.py check --deploy` shu sozlamalarni tekshiradi.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
    SECURE_HSTS_SECONDS = 31536000  # 1 yil
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True


# --------------------------------------------------------------- ilovalar

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    # o'z ilovalarimiz
    "core",
    "projects",
    "blog",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # LocaleMiddleware Session'dan KEYIN, Common'dan OLDIN turishi shart
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if not DEBUG:
    # WhiteNoise statik fayllarni produksiyada Django orqali beradi.
    # Dev'da runserver o'zi uddalaydi, shuning uchun faqat DEBUG=False da qo'shamiz.
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # profil, UI tarjimalari va til ma'lumotlari har shablonda bo'lsin
                "core.context_processors.site_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# ------------------------------------------------------------ ma'lumotlar bazasi

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DATA_DIR / "db.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ------------------------------------------------------------------ parollar

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ----------------------------------------------------------------- til / vaqt

LANGUAGE_CODE = "uz"

LANGUAGES = [
    ("uz", "O'zbekcha"),
    ("en", "English"),
]

# Diqqat: bu loyihada .po/.mo tarjima fayllari ISHLATILMAYDI.
# Sayt matni ikki manbadan keladi:
#   1) baza kontenti  -> modellarda `*_uz` / `*_en` maydonlar juftligi
#   2) interfeys matni -> core/translations.py dagi UI lug'ati
# LocaleMiddleware faqat joriy tilni aniqlash uchun kerak.
USE_I18N = True

TIME_ZONE = "Asia/Tashkent"

USE_TZ = True


# --------------------------------------------------------- statik va media

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = DATA_DIR / "media"

# Admin orqali yuklangan rasmlarni produksiyada ham Django o'zi beradi
# (WhiteNoise buni uddalay olmaydi: u fayl ro'yxatini ishga tushganda bir
# marta o'qiydi, keyin yuklangan rasm 404 bo'lib qolardi). Kichik portfolio
# uchun yetarli; S3 kabi tashqi storage ulasangiz SERVE_MEDIA=False qiling.
SERVE_MEDIA = env_bool("SERVE_MEDIA", True)

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        # DEBUG=True da oddiy storage — har o'zgarishda collectstatic talab qilmaydi
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}


# ------------------------------------------------------------------- email

EMAIL_HOST = env("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(env("EMAIL_PORT", "587"))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")

# Backend DEBUG'ga emas, login/parol borligiga qarab tanlanadi.
# Shu tufayli lokal ishlaganda ham haqiqiy xat yuborishni sinab ko'rsa bo'ladi;
# `.env` da EMAIL_HOST_USER/PASSWORD bo'sh bo'lsa — xat terminalga chiqadi.
if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "portfolio@example.com")


# -------------------------------------------------------------------- kesh

# Rate limit hisoblagichi shu keshda saqlanadi. Standart LocMemCache — jarayon
# ichida, ya'ni server qayta ishga tushsa hisob nolga qaytadi va bir nechta
# worker bo'lsa har biri o'z hisobini yuritadi. Bitta jarayonli portfolio uchun
# yetarli; kelajakda gunicorn bir nechta worker bilan ishlasa Redis'ga o'ting.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "portfolio-cache",
    }
}


# -------------------------------------------------------------------- turli

# Kontakt formasi orqali kelgan xabar haqida shu manzilga ogohlantirish yuboriladi
CONTACT_NOTIFY_EMAIL = env("CONTACT_NOTIFY_EMAIL")

# Bitta IP soatiga nechta xabar yubora oladi. Bu — spam va "email bombing"
# himoyasi: har xabar Gmail'ga xat yuboradi, cheklovsiz qoldirib bo'lmaydi.
CONTACT_RATE_LIMIT = int(env("CONTACT_RATE_LIMIT", "5"))
CONTACT_RATE_WINDOW = int(env("CONTACT_RATE_WINDOW", "3600"))  # soniya

# Yuklanadigan fayllar uchun chegara (rasm va CV)
MAX_UPLOAD_SIZE_MB = int(env("MAX_UPLOAD_SIZE_MB", "5"))

SITE_DOMAIN = env("SITE_DOMAIN", "127.0.0.1:8000")

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"


# ------------------------------------------------------------------ logging

# Standart holatda `logger.warning`/`exception` konsolga chiqadi, lekin
# `logger.info` ko'rinmaydi. Xavfsizlik hodisalari (rate limit, xat ketmagani)
# ko'rinib tursin uchun o'z ilovalarimiz uchun handler beramiz.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "[{asctime}] {levelname} {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
    },
    "loggers": {
        "core": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "projects": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "blog": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.security": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}
