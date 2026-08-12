from django.test import TestCase
from django.urls import reverse
from django.utils.translation import override

from projects.models import Project, Technology


class ProjectModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.django = Technology.objects.create(name="Django", slug="django")
        cls.project = Project.objects.create(
            title_uz="Blog API",
            title_en="Blog API",
            slug="blog-api",
            summary_uz="Qisqa tavsif",
            summary_en="Short summary",
            description_uz="To'liq tavsif",
            status=Project.Status.DONE,
        )
        cls.project.technologies.add(cls.django)

    def test_absolute_url(self):
        self.assertEqual(self.project.get_absolute_url(), "/projects/blog-api/")

    def test_status_label_is_translated(self):
        with override("uz"):
            self.assertEqual(self.project.status_label, "Tugallangan")
        with override("en"):
            self.assertEqual(self.project.status_label, "Completed")


class ProjectViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.django = Technology.objects.create(name="Django", slug="django")
        cls.react = Technology.objects.create(name="React", slug="react")

        cls.first = Project.objects.create(
            title_uz="Birinchi", slug="birinchi", summary_uz="A", description_uz="A"
        )
        cls.first.technologies.add(cls.django)

        cls.second = Project.objects.create(
            title_uz="Ikkinchi", slug="ikkinchi", summary_uz="B", description_uz="B"
        )
        cls.second.technologies.add(cls.react)

    def test_list_shows_all_projects(self):
        response = self.client.get(reverse("projects:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Birinchi")
        self.assertContains(response, "Ikkinchi")

    def test_list_filters_by_technology(self):
        response = self.client.get(reverse("projects:list"), {"tech": "django"})
        self.assertContains(response, "Birinchi")
        self.assertNotContains(response, "Ikkinchi")

    def test_detail_page(self):
        response = self.client.get(self.first.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Birinchi")

    def test_missing_project_returns_404(self):
        self.assertEqual(self.client.get("/projects/yoq/").status_code, 404)

    def test_json_api(self):
        response = self.client.get(reverse("projects-api"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 2)
        by_slug = {item["slug"]: item for item in data["results"]}
        self.assertEqual(by_slug["birinchi"]["technologies"], ["Django"])
        self.assertEqual(by_slug["ikkinchi"]["technologies"], ["React"])

    def test_json_api_filters_by_tech(self):
        response = self.client.get(reverse("projects-api"), {"tech": "react"})
        self.assertEqual(response.json()["count"], 1)
