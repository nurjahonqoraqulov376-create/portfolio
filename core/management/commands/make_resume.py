"""
Profil ma'lumotidan CV (PDF) yasab, `Profile.resume` maydoniga yozadi.

    python manage.py make_resume              # o'zbekcha
    python manage.py make_resume --lang en    # inglizcha
    python manage.py make_resume --html-only  # faqat HTML, PDF'ga aylantirmaydi

Nima uchun brauzer ishlatiladi: PDF yasovchi Python kutubxonalari
(reportlab, WeasyPrint) qo'shimcha o'rnatishni talab qiladi, WeasyPrint esa
Windows'da alohida tizim kutubxonalarini so'raydi. Chrome/Edge esa deyarli
har kompyuterda bor va `--print-to-pdf` bayrog'i bilan HTML'ni bosma sifatga
aylantirib beradi — hech narsa o'rnatmasdan.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.text import slugify

from blog.models import Post  # noqa: F401  (ilova yuklanishi uchun)
from core.models import Education, Experience, Profile, SkillCategory
from core.translations import ui_table
from projects.models import Project

# Windows'dagi odatiy joylar. Birinchi topilgani ishlatiladi.
BROWSER_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]


def find_browser():
    """Chrome yoki Edge'ni topadi. PATH'dan ham qidiradi (Linux/Mac uchun)."""
    for path in BROWSER_CANDIDATES:
        if os.path.exists(path):
            return path
    for name in ("chrome", "google-chrome", "chromium", "msedge"):
        found = shutil.which(name)
        if found:
            return found
    return None


class Command(BaseCommand):
    help = "Saytdagi ma'lumotdan CV (PDF) yasaydi va profilga biriktiradi"

    def add_arguments(self, parser):
        parser.add_argument(
            "--lang",
            default="uz",
            choices=["uz", "en"],
            help="CV tili (standart: uz)",
        )
        parser.add_argument(
            "--html-only",
            action="store_true",
            help="Faqat HTML yasaydi, PDF'ga aylantirmaydi va profilga biriktirmaydi",
        )
        parser.add_argument(
            "--output",
            default="",
            help="PDF'ni shu yo'lga ham saqlaydi (profilga biriktirishdan tashqari)",
        )

    def handle(self, *args, **options):
        lang = options["lang"]

        profile = Profile.objects.get_active()
        if profile is None:
            raise CommandError(
                "Profil topilmadi. Avval `python manage.py seed_portfolio` ishlating "
                "yoki admin paneldan profil yarating."
            )

        html = self._render(profile, lang)

        if options["html_only"]:
            path = Path(f"cv-{lang}.html")
            path.write_text(html, encoding="utf-8")
            self.stdout.write(
                self.style.SUCCESS(f"HTML tayyor: {path.resolve()}\n")
                + "Uni brauzerda oching va Ctrl+P → 'Save as PDF' qiling."
            )
            return

        pdf_bytes = self._to_pdf(html)

        filename = f"{slugify(profile.full_name) or 'cv'}-cv-{lang}.pdf"

        # Eski faylni qoldirmaymiz — media papkada keraksiz nusxa yig'ilmasin
        if profile.resume:
            profile.resume.delete(save=False)

        profile.resume.save(filename, ContentFile(pdf_bytes), save=True)

        if options["output"]:
            out = Path(options["output"])
            out.write_bytes(pdf_bytes)
            self.stdout.write(f"Nusxa saqlandi: {out.resolve()}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nCV tayyor: {profile.resume.name} "
                f"({len(pdf_bytes) / 1024:.0f} KB)\n"
                "Saytdagi 'CV yuklab olish' tugmasi endi shu faylni beradi."
            )
        )

    # ------------------------------------------------------------- ichkarisi

    def _render(self, profile, lang):
        """
        Shablonni tanlangan tilda chizadi.

        `translation.override` joriy tilni vaqtincha almashtiradi — shu tufayli
        `{{ obj|tr:"title" }}` filtri kerakli (`*_uz` yoki `*_en`) maydonni oladi.
        Kontekst protsessorlari bu yerda ishlamaydi (so'rov yo'q), shuning uchun
        `t` lug'atini o'zimiz uzatamiz.
        """
        with translation.override(lang):
            context = {
                "lang": lang,
                "t": ui_table(lang),
                "profile": profile,
                "skill_categories": SkillCategory.objects.prefetch_related("skills"),
                "experiences": Experience.objects.all(),
                "educations": Education.objects.all(),
                "projects": Project.objects.with_tech(),
            }
            return render_to_string("core/resume.html", context)

    def _to_pdf(self, html):
        browser = find_browser()
        if browser is None:
            raise CommandError(
                "Chrome yoki Edge topilmadi.\n"
                "Yechim: `python manage.py make_resume --html-only` ishlating, "
                "so'ng hosil bo'lgan HTML faylni brauzerda ochib "
                "Ctrl+P → 'Save as PDF' qiling."
            )

        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source = tmp / "cv.html"
            target = tmp / "cv.pdf"
            source.write_text(html, encoding="utf-8")

            result = subprocess.run(
                [
                    browser,
                    "--headless=new",
                    "--disable-gpu",
                    "--no-sandbox",
                    # Brauzer sahifa chetiga URL va sanani yozib qo'ymasin
                    "--no-pdf-header-footer",
                    # Shrift va uslublar to'liq qo'llanguncha kutadi
                    "--run-all-compositor-stages-before-draw",
                    "--virtual-time-budget=4000",
                    f"--user-data-dir={tmp / 'profile'}",
                    f"--print-to-pdf={target}",
                    source.as_uri(),
                ],
                capture_output=True,
                timeout=90,
            )

            if not target.exists():
                stderr = result.stderr.decode(errors="replace")[-500:]
                raise CommandError(f"PDF yasalmadi. Brauzer javobi:\n{stderr}")

            return target.read_bytes()
