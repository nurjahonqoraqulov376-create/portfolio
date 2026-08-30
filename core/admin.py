from django.contrib import admin, messages
from django.utils.html import format_html

from .models import (
    ContactMessage,
    Education,
    Experience,
    Notification,
    Profile,
    Skill,
    SkillCategory,
)

# Sarlavhalar `core/admin_site.py` da (PortfolioAdminSite) belgilangan.


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["full_name", "headline_uz", "email", "is_available", "updated_at"]
    fieldsets = [
        ("Asosiy", {"fields": ["full_name", "photo", "is_available"]}),
        ("Kasb", {"fields": ["headline_uz", "headline_en"]}),
        ("Men haqimda", {"fields": ["bio_uz", "bio_en"]}),
        ("Manzil", {"fields": ["location_uz", "location_en"]}),
        ("Aloqa", {"fields": ["email", "phone"]}),
        ("Havolalar", {"fields": ["github", "linkedin", "telegram", "website"]}),
        ("Fayllar", {"fields": ["resume"]}),
    ]

    def has_add_permission(self, request):
        # Profil bitta bo'lishi kerak: yozuv bor bo'lsa yangisini qo'shib bo'lmaydi
        return not Profile.objects.exists()


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1
    fields = ["name", "level", "order"]


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ["name_uz", "name_en", "icon", "skill_count", "order"]
    list_editable = ["order"]
    inlines = [SkillInline]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("skills")

    @admin.display(description="Ko'nikmalar soni")
    def skill_count(self, obj):
        return obj.skills.count()


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "level", "order"]
    list_filter = ["category", "level"]
    list_editable = ["level", "order"]
    search_fields = ["name"]


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ["role_uz", "company", "start_date", "end_date", "order"]
    list_editable = ["order"]
    search_fields = ["role_uz", "role_en", "company"]
    fieldsets = [
        ("Lavozim", {"fields": ["role_uz", "role_en", "company", "company_url"]}),
        ("Sana", {"fields": ["start_date", "end_date", "order"]}),
        ("Tavsif", {"fields": ["description_uz", "description_en"]}),
    ]


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ["degree_uz", "institution_uz", "start_date", "end_date", "order"]
    list_editable = ["order"]
    search_fields = ["degree_uz", "institution_uz"]


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "subject", "created_at", "is_read"]
    list_filter = ["is_read", "created_at"]
    search_fields = ["name", "email", "subject", "message"]
    readonly_fields = ["name", "email", "subject", "message", "created_at"]
    actions = ["mark_as_read", "mark_as_unread"]

    def has_add_permission(self, request):
        # Xabarlar faqat sayt formasi orqali keladi
        return False

    @admin.action(description="O'qilgan deb belgilash")
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(
            request, f"{updated} ta xabar o'qilgan deb belgilandi.", messages.SUCCESS
        )

    @admin.action(description="O'qilmagan deb belgilash")
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f"{updated} ta xabar o'qilmagan deb belgilandi.")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Bildirishnomalar markazi.

    Bu yerga sayt hodisalari tushadi: yangi xabar, CV yuklab olindi, sayt
    xatosi, spam urinishi. Telegram'ga yuborilgani bilan bir xil ma'lumot,
    lekin bu yerda qidirsa, filtrlasa va arxiv sifatida saqlasa bo'ladi.
    """

    list_display = ["badge", "short_title", "preview", "created_at", "read_mark"]
    list_display_links = ["short_title"]
    list_filter = ["kind", "is_read", "created_at"]
    search_fields = ["title", "body"]
    readonly_fields = ["kind", "title", "body", "open_link", "created_at", "repeat_count"]
    fields = ["kind", "title", "body", "open_link", "repeat_count", "created_at", "is_read"]
    date_hierarchy = "created_at"
    actions = ["mark_as_read", "mark_as_unread"]
    list_per_page = 30

    def has_add_permission(self, request):
        # Bildirishnomalarni sayt o'zi yaratadi, qo'lda qo'shilmaydi
        return False

    @admin.display(description="Turi", ordering="kind")
    def badge(self, obj):
        return format_html(
            '<span class="pf-badge pf-badge--{}">{} {}</span>',
            obj.tone,
            obj.icon,
            obj.get_kind_display(),
        )

    @admin.display(description="Sarlavha", ordering="title")
    def short_title(self, obj):
        # O'qilmaganlari qalin — ro'yxatda darhol ko'zga tashlanadi
        css = "pf-unread" if not obj.is_read else ""
        if obj.repeat_count > 1:
            # Takrorlangan hodisa yangi qator ochmaydi, shuning uchun necha
            # marta bo'lgani shu yerda ko'rinishi kerak
            return format_html(
                '<span class="{}">{}</span> <span class="pf-badge pf-badge--warning">×{}</span>',
                css,
                obj.title,
                obj.repeat_count,
            )
        return format_html('<span class="{}">{}</span>', css, obj.title)

    @admin.display(description="Tafsilot")
    def preview(self, obj):
        text = " ".join(obj.body.split())
        return text[:90] + "…" if len(text) > 90 else text

    @admin.display(description="Holat", boolean=True, ordering="is_read")
    def read_mark(self, obj):
        return obj.is_read

    @admin.display(description="Bog'liq sahifa")
    def open_link(self, obj):
        if not obj.link:
            return "—"
        return format_html('<a class="pf-link" href="{}">Ochish →</a>', obj.link)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        # Ochilgan bildirishnoma avtomatik o'qilgan bo'ladi — qo'lda
        # belgilab yurish keraksiz ish
        Notification.objects.filter(pk=object_id, is_read=False).update(is_read=True)
        return super().change_view(request, object_id, form_url, extra_context)

    @admin.action(description="Ko'rilgan deb belgilash")
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} ta bildirishnoma ko'rildi.", messages.SUCCESS)

    @admin.action(description="Ko'rilmagan deb belgilash")
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f"{updated} ta bildirishnoma ko'rilmagan qilindi.")
