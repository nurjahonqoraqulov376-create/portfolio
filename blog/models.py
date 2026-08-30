"""Blog — o'rganilgan mavzular bo'yicha qisqa yozuvlar."""

from django.db import models
from django.urls import reverse
from django.utils import timezone

from core.i18n import TranslatedMixin, translated
from core.models import validate_upload_size


class PublishedManager(models.Manager):
    """Faqat chop etilgan maqolalar (custom manager namunasi)."""

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(is_published=True, published_at__lte=timezone.now())
        )


class Post(TranslatedMixin):
    title_uz = models.CharField("Sarlavha (uz)", max_length=160)
    title_en = models.CharField("Sarlavha (en)", max_length=160, blank=True)
    slug = models.SlugField("Slug", max_length=180, unique=True)

    excerpt_uz = models.CharField("Qisqa mazmun (uz)", max_length=250)
    excerpt_en = models.CharField("Qisqa mazmun (en)", max_length=250, blank=True)

    body_uz = models.TextField("Matn (uz)")
    body_en = models.TextField("Matn (en)", blank=True)

    cover = models.ImageField(
        "Rasm", upload_to="blog/", blank=True, validators=[validate_upload_size]
    )
    tags = models.ManyToManyField(
        "projects.Technology", related_name="posts", verbose_name="Teglar", blank=True
    )

    is_published = models.BooleanField("Chop etilgan", default=True)
    published_at = models.DateTimeField("Chop etilgan vaqti", default=timezone.now)
    views = models.PositiveIntegerField("Ko'rishlar", default=0, editable=False)

    objects = models.Manager()       # admin uchun — hammasi
    published = PublishedManager()   # sayt uchun — faqat chop etilganlari

    class Meta:
        verbose_name = "Maqola"
        verbose_name_plural = "Maqolalar"
        ordering = ["-published_at"]
        indexes = [models.Index(fields=["-published_at"])]

    def __str__(self):
        return self.title_uz

    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"slug": self.slug})

    @property
    def reading_time(self):
        """Taxminiy o'qish vaqti (daqiqa) — 180 so'z/daqiqa."""
        words = len(translated(self, "body").split())
        return max(1, round(words / 180))
