"""Qidiruv tizimlari uchun sitemap.xml."""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from blog.models import Post
from projects.models import Project


class StaticSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1.0

    def items(self):
        return ["core:home", "projects:list", "blog:list"]

    def location(self, item):
        return reverse(item)


class ProjectSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Project.objects.all()

    def lastmod(self, obj):
        return obj.created_at


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Post.published.all()

    def lastmod(self, obj):
        return obj.published_at


SITEMAPS = {
    "static": StaticSitemap,
    "projects": ProjectSitemap,
    "posts": PostSitemap,
}
