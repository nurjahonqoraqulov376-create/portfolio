from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from blog.models import Post


class PostModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.published = Post.objects.create(
            title_uz="Chop etilgan",
            slug="chop-etilgan",
            excerpt_uz="Qisqa",
            body_uz=" ".join(["so'z"] * 360),
        )
        cls.draft = Post.objects.create(
            title_uz="Qoralama",
            slug="qoralama",
            excerpt_uz="Qisqa",
            body_uz="Matn",
            is_published=False,
        )
        cls.future = Post.objects.create(
            title_uz="Kelajakda",
            slug="kelajakda",
            excerpt_uz="Qisqa",
            body_uz="Matn",
            published_at=timezone.now() + timedelta(days=3),
        )

    def test_published_manager_hides_drafts_and_future(self):
        slugs = list(Post.published.values_list("slug", flat=True))
        self.assertEqual(slugs, ["chop-etilgan"])
        self.assertEqual(Post.objects.count(), 3)

    def test_reading_time(self):
        # 360 so'z / 180 = 2 daqiqa
        self.assertEqual(self.published.reading_time, 2)

    def test_absolute_url(self):
        self.assertEqual(self.published.get_absolute_url(), "/blog/chop-etilgan/")


class PostViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.post = Post.objects.create(
            title_uz="Django ORM",
            title_en="Django ORM in English",
            slug="django-orm",
            excerpt_uz="Qisqa mazmun",
            excerpt_en="Short excerpt",
            body_uz="O'zbekcha matn",
            body_en="English body",
        )

    def test_list_page(self):
        response = self.client.get(reverse("blog:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django ORM")

    def test_detail_page_increments_views(self):
        self.assertEqual(self.post.views, 0)
        response = self.client.get(self.post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.views, 1)

    def test_detail_page_in_english(self):
        response = self.client.get("/en/blog/django-orm/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "English body")

    def test_draft_is_not_reachable(self):
        Post.objects.create(
            title_uz="Yashirin",
            slug="yashirin",
            excerpt_uz="Q",
            body_uz="M",
            is_published=False,
        )
        self.assertEqual(self.client.get("/blog/yashirin/").status_code, 404)
