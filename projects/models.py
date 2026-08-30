"""Portfolio loyihalari."""

from django.db import models
from django.urls import reverse

from core.i18n import TranslatedMixin
from core.models import validate_upload_size
from core.translations import choice_label


class Technology(models.Model):
    """Loyihalarda ishlatilgan texnologiya (Django, PostgreSQL, Docker ...)."""

    name = models.CharField("Nomi", max_length=50, unique=True)
    slug = models.SlugField("Slug", max_length=60, unique=True)
    color = models.CharField(
        "Rang", max_length=7, default="#6366f1", help_text="HEX, masalan #0c4b33"
    )

    class Meta:
        verbose_name = "Texnologiya"
        verbose_name_plural = "Texnologiyalar"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProjectQuerySet(models.QuerySet):
    """
    Maxsus QuerySet — metodlarni zanjir qilib chaqirish mumkin:
    `Project.objects.featured().with_tech()`.
    """

    def featured(self):
        return self.filter(is_featured=True)

    def with_tech(self):
        return self.prefetch_related("technologies")


class Project(TranslatedMixin):
    """Bitta portfolio loyihasi."""

    STATUS_LABELS = {
        "planned": {"uz": "Rejada", "en": "Planned"},
        "in_progress": {"uz": "Jarayonda", "en": "In progress"},
        "done": {"uz": "Tugallangan", "en": "Completed"},
    }

    class Status(models.TextChoices):
        PLANNED = "planned", "Rejada"
        IN_PROGRESS = "in_progress", "Jarayonda"
        DONE = "done", "Tugallangan"

    title_uz = models.CharField("Sarlavha (uz)", max_length=140)
    title_en = models.CharField("Sarlavha (en)", max_length=140, blank=True)
    slug = models.SlugField("Slug", max_length=160, unique=True)

    summary_uz = models.CharField("Qisqa tavsif (uz)", max_length=220)
    summary_en = models.CharField("Qisqa tavsif (en)", max_length=220, blank=True)

    description_uz = models.TextField("To'liq tavsif (uz)")
    description_en = models.TextField("To'liq tavsif (en)", blank=True)

    cover = models.ImageField(
        "Rasm", upload_to="projects/", blank=True, validators=[validate_upload_size]
    )
    icon = models.CharField(
        "Belgi (emoji)",
        max_length=8,
        blank=True,
        help_text="Rasm yuklanmagan bo'lsa, muqovada shu emoji chiqadi. Masalan: 🤖",
    )
    technologies = models.ManyToManyField(
        Technology, related_name="projects", verbose_name="Texnologiyalar", blank=True
    )

    github_url = models.URLField("GitHub havolasi", blank=True)
    live_url = models.URLField("Ishlayotgan sayt", blank=True)

    status = models.CharField(
        "Holati", max_length=20, choices=Status.choices, default=Status.DONE
    )
    is_featured = models.BooleanField("Tanlangan (bosh sahifada)", default=False)
    started_at = models.DateField("Boshlangan sana", null=True, blank=True)
    order = models.PositiveIntegerField("Tartib", default=0)
    created_at = models.DateTimeField("Qo'shilgan", auto_now_add=True)

    objects = ProjectQuerySet.as_manager()

    class Meta:
        verbose_name = "Loyiha"
        verbose_name_plural = "Loyihalar"
        ordering = ["order", "-created_at"]
        indexes = [models.Index(fields=["is_featured", "order"])]

    def __str__(self):
        return self.title_uz

    def get_absolute_url(self):
        return reverse("projects:detail", kwargs={"slug": self.slug})

    @property
    def status_label(self):
        """Holat nomi joriy tilda."""
        return choice_label(self.STATUS_LABELS, self.status)
