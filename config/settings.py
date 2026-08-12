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


# ---------------------------------------------------------------- xavfsizlik

SECRET_KEY = env("SECRET_KEY", "dev-only-insecure-key-almashtiring")

DEBUG = env_bool("DEBUG", True)

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1,[::1]")

CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")

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
        "NAME": BASE_DIR / "db.sqlite3",
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
MEDIA_ROOT = BASE_DIR / "media"

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

# Dev rejimida xatlar terminalga chiqadi — SMTP sozlash shart emas.
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = env("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(env("EMAIL_PORT", "587"))
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = env("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "portfolio@example.com")


# -------------------------------------------------------------------- turli

# Kontakt formasi orqali kelgan xabar haqida shu manzilga ogohlantirish yuboriladi
CONTACT_NOTIFY_EMAIL = env("CONTACT_NOTIFY_EMAIL")

SITE_DOMAIN = env("SITE_DOMAIN", "127.0.0.1:8000")

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"
