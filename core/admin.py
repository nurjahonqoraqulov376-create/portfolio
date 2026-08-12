from django.contrib import admin, messages

from .models import (
    ContactMessage,
    Education,
    Experience,
    Profile,
    Skill,
    SkillCategory,
)

admin.site.site_header = "Portfolio boshqaruvi"
admin.site.site_title = "Portfolio admin"
admin.site.index_title = "Sayt kontenti"


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
