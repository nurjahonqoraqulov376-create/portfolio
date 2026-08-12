"""
Loyiha URL'lari.

`i18n_patterns` tillar uchun prefiks qo'shadi:
    /            -> o'zbekcha (prefix_default_language=False)
    /en/         -> inglizcha
Admin, API va sitemap prefikssiz qoladi.
"""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from core.sitemaps import SITEMAPS
from core.views import projects_api, robots_txt

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/projects/", projects_api, name="projects-api"),
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS}, name="sitemap"),
    path("robots.txt", robots_txt, name="robots"),
    # `set_language` view — til almashtirish formasi uchun
    path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += i18n_patterns(
    path("", include("core.urls")),
    path("projects/", include("projects.urls")),
    path("blog/", include("blog.urls")),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "core.views.page_not_found"
handler500 = "core.views.server_error"
