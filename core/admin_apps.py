"""
Admin ilovasining konfiguratsiyasi.

INSTALLED_APPS da `django.contrib.admin` o'rniga shu tursa, Django
standart `admin.site` o'rniga `default_site` dagi klassni ishlatadi.

Nega `core/apps.py` da emas: bitta modulda ikkita AppConfig turса,
Django "core" ilovasi uchun qaysi biri asosiy ekanini bilolmay xato beradi.
"""

from django.contrib.admin.apps import AdminConfig


class PortfolioAdminConfig(AdminConfig):
    default_site = "core.admin_site.PortfolioAdminSite"
