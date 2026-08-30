"""
Serverni birinchi marta ishga tushirishga tayyorlaydi.

    python manage.py bootstrap

`Procfile` da har deployda chaqiriladi, shuning uchun komanda **idempotent**:
ikkinchi marta ishlaganda hech narsani takrorlamaydi. Ish bajarilganini
DATA_DIR ichidagi `.bootstrapped` belgisi bildiradi — u doimiy diskda (Railway
Volume) yotgani uchun keyingi deploylarda ham saqlanib qoladi.

Ikki ish qiladi:

1. Admin foydalanuvchi yaratadi — `DJANGO_SUPERUSER_USERNAME` va
   `DJANGO_SUPERUSER_PASSWORD` muhit o'zgaruvchilari berilgan bo'lsa va
   bazada hali birorta superuser bo'lmasa.
2. `deploy_seed/` papkasidagi boshlang'ich kontentni (JSON + rasmlar)
   bo'sh bazaga yuklaydi.

Server `railway ssh` bo'lmasa ham to'liq ishga tushsin uchun shunday qilingan.
"""

import os
import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand

SEED_DIR = settings.BASE_DIR / "deploy_seed"


class Command(BaseCommand):
    help = "Deploydan keyingi birinchi sozlash: admin va boshlang'ich kontent."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Belgi fayli bo'lsa ham kontentni qayta yuklash.",
        )

    def handle(self, *args, **options):
        self._ensure_superuser()
        self._load_seed(force=options["force"])

    # ------------------------------------------------------------- admin

    def _ensure_superuser(self):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "").strip()
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()

        User = get_user_model()
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write("Admin allaqachon bor — o'tkazib yuborildi.")
            return
        if not username or not password:
            self.stdout.write(
                "DJANGO_SUPERUSER_USERNAME/PASSWORD berilmagan — admin yaratilmadi."
            )
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Admin yaratildi: {username}"))

    # --------------------------------------------------- boshlang'ich kontent

    def _load_seed(self, force=False):
        marker = settings.DATA_DIR / ".bootstrapped"
        if marker.exists() and not force:
            self.stdout.write("Kontent avval yuklangan — o'tkazib yuborildi.")
            return

        fixture = SEED_DIR / "data.json"
        if fixture.exists():
            call_command("loaddata", str(fixture), verbosity=1)
        else:
            self.stdout.write("deploy_seed/data.json topilmadi.")

        # Rasm va CV fayllarini doimiy diskka ko'chiramiz. Bazadagi yozuvlar
        # shu yo'llarga ishora qiladi, shuning uchun ular birga kelishi kerak.
        seed_media = SEED_DIR / "media"
        if seed_media.is_dir():
            copied = 0
            for src in seed_media.rglob("*"):
                if not src.is_file():
                    continue
                dst = settings.MEDIA_ROOT / src.relative_to(seed_media)
                if dst.exists():
                    continue
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                copied += 1
            self.stdout.write(f"Media fayllar ko'chirildi: {copied} ta")

        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text("ok\n", encoding="utf-8")
        self.stdout.write(self.style.SUCCESS("Boshlang'ich kontent yuklandi."))
