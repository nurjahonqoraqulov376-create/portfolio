"""
Maxsus admin sayt — bosh sahifasida statistika va bildirishnomalar.

Nega standart `admin.site` emas: Django'ning admin bosh sahifasi faqat
modellar ro'yxatini ko'rsatadi. Bizga esa "nima bo'ldi?" degan savolga
darhol javob beradigan panel kerak — o'qilmagan xabarlar, CV yuklashlar,
sayt xatolari.

Ulanishi `config/settings.py` dagi INSTALLED_APPS orqali:
`django.contrib.admin` o'rniga `core.apps.PortfolioAdminConfig` turadi.
"""

from datetime import timedelta

from django.contrib.admin import AdminSite
from django.db.models import Sum
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone


class PortfolioAdminSite(AdminSite):
    site_header = "Portfolio boshqaruvi"
    site_title = "Portfolio admin"
    index_title = "Boshqaruv paneli"

    def each_context(self, request):
        """
        Har bir admin sahifasiga qo'shiladigan ma'lumot.

        O'qilmagan bildirishnomalar soni sarlavhadagi qizil nishonda
        ko'rinadi — qaysi sahifada bo'lmang, yangilik borligini bilasiz.
        """
        context = super().each_context(request)
        context["unread_notifications"] = self._unread_count()
        return context

    def _unread_count(self):
        # Import shu yerda: modul yuklanayotganda ilovalar hali tayyor bo'lmaydi
        from .models import Notification

        try:
            return Notification.objects.unread().count()
        except Exception:
            # Migratsiya qilinmagan bazada admin baribir ochilaversin
            return 0

    def index(self, request, extra_context=None):
        extra_context = {**(extra_context or {}), **self._dashboard_context()}
        return super().index(request, extra_context)

    def _dashboard_context(self):
        from blog.models import Post
        from projects.models import Project

        from .models import ContactMessage, Notification

        week_ago = timezone.now() - timedelta(days=7)

        try:
            unread_messages = ContactMessage.objects.filter(is_read=False).count()
            resume_week = Notification.objects.filter(
                kind=Notification.KIND_RESUME, created_at__gte=week_ago
            ).count()
            errors_week = Notification.objects.filter(
                kind=Notification.KIND_ERROR, created_at__gte=week_ago
            ).count()
            blog_views = Post.objects.aggregate(total=Sum("views"))["total"] or 0
            recent = list(Notification.objects.all()[:8])
        except Exception:
            # Baza hali tayyor emas (birinchi migratsiyagacha) — panel bo'sh chiqsin
            return {"dashboard_cards": [], "recent_notifications": []}

        # Har karta: (belgi, sarlavha, qiymat, izoh, rang, havola)
        cards = [
            {
                "icon": "💬",
                "label": "O'qilmagan xabar",
                "value": unread_messages,
                "hint": "Kontakt formasidan",
                "tone": "accent" if unread_messages else "muted",
                "url": reverse("admin:core_contactmessage_changelist")
                + "?is_read__exact=0",
            },
            {
                "icon": "📄",
                "label": "CV yuklashlar",
                "value": resume_week,
                "hint": "Oxirgi 7 kun",
                "tone": "success" if resume_week else "muted",
                "url": reverse("admin:core_notification_changelist")
                + f"?kind__exact={Notification.KIND_RESUME}",
            },
            {
                "icon": "🔴",
                "label": "Sayt xatolari",
                "value": errors_week,
                "hint": "Oxirgi 7 kun",
                "tone": "danger" if errors_week else "muted",
                "url": reverse("admin:core_notification_changelist")
                + f"?kind__exact={Notification.KIND_ERROR}",
            },
            {
                "icon": "🚀",
                "label": "Loyihalar",
                "value": Project.objects.count(),
                "hint": f"{Project.objects.filter(is_featured=True).count()} tasi tanlangan",
                "tone": "muted",
                "url": reverse("admin:projects_project_changelist"),
            },
            {
                "icon": "👁",
                "label": "Blog ko'rishlari",
                "value": blog_views,
                "hint": f"{Post.objects.count()} ta post",
                "tone": "muted",
                "url": reverse("admin:blog_post_changelist"),
            },
        ]

        return {
            "dashboard_cards": cards,
            "recent_notifications": recent,
            "notifications_url": reverse("admin:core_notification_changelist"),
        }
