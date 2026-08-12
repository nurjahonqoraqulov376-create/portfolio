from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title_uz", "is_published", "published_at", "views"]
    list_editable = ["is_published"]
    list_filter = ["is_published", "published_at", "tags"]
    search_fields = ["title_uz", "title_en", "body_uz", "body_en"]
    prepopulated_fields = {"slug": ("title_uz",)}
    filter_horizontal = ["tags"]
    date_hierarchy = "published_at"
    readonly_fields = ["views"]
    fieldsets = [
        ("Sarlavha", {"fields": ["title_uz", "title_en", "slug"]}),
        ("Qisqa mazmun", {"fields": ["excerpt_uz", "excerpt_en"]}),
        ("Matn", {"fields": ["body_uz", "body_en"]}),
        ("Qo'shimcha", {"fields": ["cover", "tags"]}),
        ("Chop etish", {"fields": ["is_published", "published_at", "views"]}),
    ]
