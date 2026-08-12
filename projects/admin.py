from django.contrib import admin
from django.utils.html import format_html

from .models import Project, Technology


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "color_box", "project_count"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("projects")

    @admin.display(description="Rang")
    def color_box(self, obj):
        return format_html(
            '<span style="display:inline-block;width:60px;height:16px;'
            'border-radius:4px;background:{}"></span> {}',
            obj.color,
            obj.color,
        )

    @admin.display(description="Loyihalar")
    def project_count(self, obj):
        return obj.projects.count()


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["title_uz", "status", "is_featured", "order", "created_at"]
    list_editable = ["is_featured", "order"]
    list_filter = ["status", "is_featured", "technologies"]
    search_fields = ["title_uz", "title_en", "summary_uz", "description_uz"]
    prepopulated_fields = {"slug": ("title_uz",)}
    filter_horizontal = ["technologies"]
    date_hierarchy = "created_at"
    fieldsets = [
        ("Sarlavha", {"fields": ["title_uz", "title_en", "slug"]}),
        ("Qisqa tavsif", {"fields": ["summary_uz", "summary_en"]}),
        ("To'liq tavsif", {"fields": ["description_uz", "description_en"]}),
        ("Media va texnologiyalar", {"fields": ["cover", "technologies"]}),
        ("Havolalar", {"fields": ["github_url", "live_url"]}),
        ("Sozlamalar", {"fields": ["status", "is_featured", "started_at", "order"]}),
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("technologies")
