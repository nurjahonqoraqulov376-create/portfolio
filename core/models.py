"""Portfolio egasi haqidagi asosiy modellar."""

from django.db import models

from .i18n import TranslatedMixin


class ProfileManager(models.Manager):
    """Profil bitta bo'lishi kerak — uni olishning qulay usuli."""

    def get_active(self):
        return self.first()


class Profile(TranslatedMixin):
    """Sayt egasi haqidagi ma'lumot. Bazada faqat bitta yozuv bo'ladi."""

    full_name = models.CharField("To'liq ism", max_length=120)

    headline_uz = models.CharField("Kasb (uz)", max_length=160)
    headline_en = models.CharField("Kasb (en)", max_length=160, blank=True)

    bio_uz = models.TextField("Men haqimda (uz)")
    bio_en = models.TextField("Men haqimda (en)", blank=True)

    location_uz = models.CharField("Manzil (uz)", max_length=120, blank=True)
    location_en = models.CharField("Manzil (en)", max_length=120, blank=True)

    photo = models.ImageField("Rasm", upload_to="profile/", blank=True)
    resume = models.FileField("CV fayli", upload_to="resume/", blank=True)

    email = models.EmailField("Email")
    phone = models.CharField("Telefon", max_length=32, blank=True)

    telegram = models.URLField("Telegram", blank=True)
    github = models.URLField("GitHub", blank=True)
    linkedin = models.URLField("LinkedIn", blank=True)
    website = models.URLField("Shaxsiy sayt", blank=True)

    is_available = models.BooleanField("Ish takliflariga ochiq", default=True)
    updated_at = models.DateTimeField("Yangilangan", auto_now=True)

    objects = ProfileManager()

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profil"

    def __str__(self):
        return self.full_name

    @property
    def socials(self):
        """Footer va kontakt bo'limi uchun to'ldirilgan havolalar ro'yxati."""
        links = [
            ("GitHub", self.github),
            ("LinkedIn", self.linkedin),
            ("Telegram", self.telegram),
            ("Website", self.website),
        ]
        return [(name, url) for name, url in links if url]


class SkillCategory(TranslatedMixin):
    """Ko'nikmalar guruhi: Backend, Ma'lumotlar bazasi, Vositalar ..."""

    name_uz = models.CharField("Nomi (uz)", max_length=80)
    name_en = models.CharField("Nomi (en)", max_length=80, blank=True)
    icon = models.CharField("Belgi (emoji)", max_length=8, blank=True)
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        verbose_name = "Ko'nikma turkumi"
        verbose_name_plural = "Ko'nikma turkumlari"
        ordering = ["order", "id"]

    def __str__(self):
        return self.name_uz


class Skill(models.Model):
    """Bitta texnologiya va uni bilish darajasi."""

    class Level(models.IntegerChoices):
        BEGINNER = 1, "Boshlang'ich"
        BASIC = 2, "Asosiy"
        CONFIDENT = 3, "Ishonchli"
        STRONG = 4, "Kuchli"
        EXPERT = 5, "Ekspert"

    category = models.ForeignKey(
        SkillCategory,
        on_delete=models.CASCADE,
        related_name="skills",
        verbose_name="Turkum",
    )
    name = models.CharField("Nomi", max_length=60)
    level = models.PositiveSmallIntegerField(
        "Daraja", choices=Level.choices, default=Level.CONFIDENT
    )
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        verbose_name = "Ko'nikma"
        verbose_name_plural = "Ko'nikmalar"
        ordering = ["order", "-level", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"

    @property
    def percent(self):
        return self.level * 20


class Experience(TranslatedMixin):
    """Ish yoki amaliyot tajribasi."""

    role_uz = models.CharField("Lavozim (uz)", max_length=120)
    role_en = models.CharField("Lavozim (en)", max_length=120, blank=True)
    company = models.CharField("Tashkilot", max_length=120)
    company_url = models.URLField("Tashkilot sayti", blank=True)

    description_uz = models.TextField("Tavsif (uz)", blank=True)
    description_en = models.TextField("Tavsif (en)", blank=True)

    start_date = models.DateField("Boshlangan")
    end_date = models.DateField("Tugagan", null=True, blank=True, help_text="Bo'sh = hozirgacha")
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        verbose_name = "Tajriba"
        verbose_name_plural = "Tajriba"
        ordering = ["order", "-start_date"]

    def __str__(self):
        return f"{self.role_uz} — {self.company}"

    @property
    def is_current(self):
        return self.end_date is None


class Education(TranslatedMixin):
    """Ta'lim yoki kurs."""

    degree_uz = models.CharField("Yo'nalish (uz)", max_length=140)
    degree_en = models.CharField("Yo'nalish (en)", max_length=140, blank=True)
    institution_uz = models.CharField("O'quv muassasasi (uz)", max_length=140)
    institution_en = models.CharField("O'quv muassasasi (en)", max_length=140, blank=True)

    description_uz = models.TextField("Tavsif (uz)", blank=True)
    description_en = models.TextField("Tavsif (en)", blank=True)

    start_date = models.DateField("Boshlangan")
    end_date = models.DateField("Tugagan", null=True, blank=True, help_text="Bo'sh = hozirgacha")
    certificate_url = models.URLField("Sertifikat havolasi", blank=True)
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        verbose_name = "Ta'lim"
        verbose_name_plural = "Ta'lim"
        ordering = ["order", "-start_date"]

    def __str__(self):
        return f"{self.degree_uz} — {self.institution_uz}"

    @property
    def is_current(self):
        return self.end_date is None


class ContactMessage(models.Model):
    """Saytdagi kontakt formasi orqali kelgan xabar."""

    name = models.CharField("Ism", max_length=120)
    email = models.EmailField("Email")
    subject = models.CharField("Mavzu", max_length=160)
    message = models.TextField("Xabar")
    created_at = models.DateTimeField("Kelgan vaqti", auto_now_add=True)
    is_read = models.BooleanField("O'qilgan", default=False)

    class Meta:
        verbose_name = "Xabar"
        verbose_name_plural = "Xabarlar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name}: {self.subject}"
