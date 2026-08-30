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


class NotificationSafetyTests(TestCase):
    """
    Bildirishnoma tizimi hujum paytida ham xotirjam qolishi kerak.

    Bu testlar aynan quyidagi xavflarga qarshi yozilgan:
      * bot formaga urganda har urinishga alohida yozuv va Telegram xabari
        ketishi (o'zimizni o'zimiz DDoS qilish);
      * jadvalning cheksiz o'sib, diskni to'ldirib qo'yishi;
      * bildirishnoma yaratishdagi nosozlik mehmonning so'rovini yiqitishi.
    """

    def setUp(self):
        from core.models import Notification

        Notification.objects.all().delete()

    def test_repeated_spam_creates_single_row(self):
        from core.models import Notification
        from core.notifications import notify

        for _ in range(50):
            notify(Notification.KIND_SPAM, "Bot aniqlandi", "sinov")

        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(Notification.objects.first().repeat_count, 50)

    def test_repeated_errors_are_grouped(self):
        from core.models import Notification
        from core.notifications import notify

        for _ in range(20):
            notify(Notification.KIND_ERROR, "Saytda xatolik (500)", "/sinov/")

        self.assertEqual(Notification.objects.count(), 1)

    def test_contact_messages_are_never_grouped(self):
        """Har bir haqiqiy xabar qimmatli — ular birlashtirilmasligi kerak."""
        from core.models import Notification
        from core.notifications import notify

        for i in range(3):
            notify(Notification.KIND_MESSAGE, f"Mehmon {i}", "salom")

        self.assertEqual(Notification.objects.count(), 3)

    def test_table_is_pruned_at_limit(self):
        from core.models import Notification
        from core import notifications

        original = notifications.MAX_ROWS
        notifications.MAX_ROWS = 10
        try:
            for i in range(25):
                notifications.notify(Notification.KIND_MESSAGE, f"Xabar {i}")
            self.assertLessEqual(Notification.objects.count(), 10)
            # Eng yangilari qolishi kerak, eng eskilari o'chishi
            self.assertTrue(Notification.objects.filter(title="Xabar 24").exists())
            self.assertFalse(Notification.objects.filter(title="Xabar 0").exists())
        finally:
            notifications.MAX_ROWS = original

    def test_notify_never_raises(self):
        """
        Bildirishnoma yaratishdagi har qanday nosozlik yutilishi shart.

        Aks holda kontakt formasi yoki 500 sahifasi mehmonga bo'sh ekran
        ko'rsatib qo'yadi.
        """
        from unittest.mock import patch

        from core.models import Notification
        from core.notifications import notify

        with patch(
            "core.models.Notification.objects.create", side_effect=RuntimeError("baza yo'q")
        ):
            self.assertIsNone(notify(Notification.KIND_MESSAGE, "Sinov"))

    def test_describe_request_survives_bad_host(self):
        """Noto'g'ri `Host` sarlavhasi bildirishnomani yiqitmasligi kerak."""
        from django.core.exceptions import DisallowedHost
        from unittest.mock import Mock

        from core.notifications import describe_request

        request = Mock()
        request.META = {}
        request.get_host.side_effect = DisallowedHost("yomon host")
        self.assertIn("IP", describe_request(request))


class TelegramSafetyTests(TestCase):
    """Telegram moduli maxfiy ma'lumotni sizdirmasligi kerak."""

    def test_token_is_removed_from_log_text(self):
        from django.test import override_settings

        from core import telegram

        token = "1234567890:AAHsecret-token-value"
        with override_settings(TELEGRAM_BOT_TOKEN=token):
            scrubbed = telegram._scrub(f"xato: https://api.telegram.org/bot{token}/send")
        self.assertNotIn(token, scrubbed)
        self.assertIn("***TOKEN***", scrubbed)

    def test_html_is_escaped_in_message(self):
        """Mehmon yozgan matn Telegram formatlashini buzmasligi kerak."""
        from core import telegram
        from core.models import Notification

        text = telegram.format_notification(
            Notification.KIND_MESSAGE, "<b>qalbaki</b>", "<script>x</script>"
        )
        self.assertNotIn("<script>", text)
        self.assertIn("&lt;script&gt;", text)


class AdminLoginThrottleTests(TestCase):
    """Admin parolini cheksiz tanlab bo'lmasligi kerak."""

    def setUp(self):
        from django.core.cache import cache

        cache.clear()

    def test_repeated_failures_are_blocked(self):
        from core.admin_site import LOGIN_MAX_ATTEMPTS

        url = reverse("admin:login")
        for _ in range(LOGIN_MAX_ATTEMPTS):
            self.client.post(url, {"username": "admin", "password": "xato"})

        response = self.client.post(url, {"username": "admin", "password": "xato"})
        self.assertEqual(response.status_code, 429)

    def test_successful_login_resets_counter(self):
        from django.contrib.auth import get_user_model

        from core.admin_site import LOGIN_MAX_ATTEMPTS

        get_user_model().objects.create_superuser("egasi", "e@e.uz", "juda-kuchli-parol-1")
        url = reverse("admin:login")

        for _ in range(LOGIN_MAX_ATTEMPTS - 1):
            self.client.post(url, {"username": "egasi", "password": "xato"})

        self.client.post(url, {"username": "egasi", "password": "juda-kuchli-parol-1"})
        # Hisob nolga qaytgani uchun keyingi urinish bloklanmaydi
        response = self.client.post(url, {"username": "egasi", "password": "xato"})
        self.assertNotEqual(response.status_code, 429)


class ResumeDownloadTests(TestCase):
    """CV havolasi kuzatilishi, lekin spam bildirishnoma yasamasligi kerak."""

    def setUp(self):
        from django.core.cache import cache
        from django.core.files.uploadedfile import SimpleUploadedFile

        from core.models import Notification

        cache.clear()
        Notification.objects.all().delete()
        self.profile = Profile.objects.create(
            full_name="Sinov", headline_uz="Dasturchi", bio_uz="matn", email="a@b.uz"
        )
        self.profile.resume.save(
            "cv.pdf", SimpleUploadedFile("cv.pdf", b"%PDF-1.4 sinov"), save=True
        )

    def tearDown(self):
        self.profile.resume.delete(save=False)

    def test_download_is_recorded_once_per_window(self):
        from core.models import Notification

        for _ in range(5):
            response = self.client.get(reverse("core:resume_download"))
            self.assertEqual(response.status_code, 302)

        self.assertEqual(
            Notification.objects.filter(kind=Notification.KIND_RESUME).count(), 1
        )

    def test_missing_resume_returns_404(self):
        self.profile.resume.delete(save=True)
        self.assertEqual(self.client.get(reverse("core:resume_download")).status_code, 404)
