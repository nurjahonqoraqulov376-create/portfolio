"""core ilovasi testlari."""

from django.test import TestCase
from django.urls import reverse
from django.utils.translation import override

from core.i18n import translated
from core.models import ContactMessage, Profile, Skill, SkillCategory
from core.translations import ui


class TranslationHelperTests(TestCase):
    """`translated()` joriy tilga qarab to'g'ri maydonni tanlashi kerak."""

    @classmethod
    def setUpTestData(cls):
        cls.category = SkillCategory.objects.create(
            name_uz="Backend", name_en="Backend server"
        )
        cls.only_uz = SkillCategory.objects.create(name_uz="Faqat o'zbekcha", name_en="")

    def test_returns_uzbek_by_default(self):
        with override("uz"):
            self.assertEqual(translated(self.category, "name"), "Backend")

    def test_returns_english_when_active(self):
        with override("en"):
            self.assertEqual(translated(self.category, "name"), "Backend server")

    def test_falls_back_to_uzbek_when_translation_missing(self):
        with override("en"):
            self.assertEqual(translated(self.only_uz, "name"), "Faqat o'zbekcha")

    def test_ui_labels_exist_in_both_languages(self):
        with override("uz"):
            self.assertEqual(ui("nav_projects"), "Loyihalar")
        with override("en"):
            self.assertEqual(ui("nav_projects"), "Projects")


class ModelTests(TestCase):
    def test_skill_percent(self):
        category = SkillCategory.objects.create(name_uz="Backend")
        skill = Skill.objects.create(category=category, name="Django", level=4)
        self.assertEqual(skill.percent, 80)
        self.assertIn("Django", str(skill))

    def test_profile_socials_skips_empty_links(self):
        profile = Profile.objects.create(
            full_name="Test User",
            headline_uz="Backend",
            bio_uz="Bio",
            email="test@example.com",
            github="https://github.com/test",
        )
        self.assertEqual(profile.socials, [("GitHub", "https://github.com/test")])


class HomePageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Profile.objects.create(
            full_name="Test User",
            headline_uz="Django dasturchi",
            headline_en="Django developer",
            bio_uz="O'zbekcha bio",
            bio_en="English bio",
            email="test@example.com",
        )

    def test_home_page_uses_uzbek(self):
        # Manzilni to'g'ridan-to'g'ri yozamiz: `reverse()` joriy faol tilga
        # qarab prefiks qo'shadi, test tartibiga bog'liq bo'lib qolmasin.
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django dasturchi")
        self.assertContains(response, "Loyihalar")

    def test_home_page_english_prefix(self):
        response = self.client.get("/en/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django developer")
        self.assertContains(response, "Projects")

    def test_uzbek_has_no_url_prefix(self):
        # prefix_default_language=False -> "/uz/" mavjud emas
        self.assertEqual(self.client.get("/uz/").status_code, 404)


class ContactFormTests(TestCase):
    def test_valid_message_is_saved(self):
        response = self.client.post(
            reverse("core:contact"),
            {
                "name": "Ali",
                "email": "ali@example.com",
                "subject": "Salom",
                "message": "Bu yetarlicha uzun xabar matni.",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertEqual(ContactMessage.objects.first().name, "Ali")

    def test_invalid_email_is_rejected(self):
        Profile.objects.create(
            full_name="Test", headline_uz="Backend", bio_uz="Bio", email="a@b.uz"
        )
        response = self.client.post(
            reverse("core:contact"),
            {
                "name": "Ali",
                "email": "notanemail",
                "subject": "Salom",
                "message": "Bu yetarlicha uzun xabar matni.",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_short_message_is_rejected(self):
        response = self.client.post(
            reverse("core:contact"),
            {
                "name": "Ali",
                "email": "ali@example.com",
                "subject": "Salom",
                "message": "qisqa",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_honeypot_blocks_bots(self):
        self.client.post(
            reverse("core:contact"),
            {
                "name": "Bot",
                "email": "bot@example.com",
                "subject": "Spam",
                "message": "Bu yetarlicha uzun spam matni.",
                "honeypot": "men botman",
            },
        )
        self.assertEqual(ContactMessage.objects.count(), 0)


class SeedCommandTests(TestCase):
    def test_seed_command_is_idempotent(self):
        from django.core.management import call_command
        from io import StringIO

        out = StringIO()
        call_command("seed_portfolio", stdout=out)
        first_count = Profile.objects.count()

        call_command("seed_portfolio", stdout=out)
        self.assertEqual(Profile.objects.count(), first_count)
        self.assertEqual(first_count, 1)
