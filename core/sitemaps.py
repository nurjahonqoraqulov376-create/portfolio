"""Qidiruv tizimlari uchun sitemap.xml."""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from projects.models import Project


class StaticSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1.0

    def items(self):
        # Blog hozircha yashirilgan — maqola paydo bo'lganda "blog:list" qo'shiladi
        return ["core:home", "projects:list"]

    def location(self, item):
        return reverse(item)


class ProjectSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Project.objects.all()

    def lastmod(self, obj):
        return obj.created_at


SITEMAPS = {
    "static": StaticSitemap,
    "projects": ProjectSitemap,
}
