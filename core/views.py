"""Bosh sahifa, kontakt formasi va kichik JSON API."""

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView

from blog.models import Post
from projects.models import Project, Technology

from .forms import ContactForm
from .i18n import translated
from .models import Education, Experience, SkillCategory
from .translations import ui


def home_context(form=None):
    """
    Bosh sahifa uchun barcha ma'lumot.

    Alohida funksiya, chunki uni ikki joy ishlatadi: `HomeView` va kontakt
    formasi xato bilan qaytganda `contact_view`.
    """
    return {
        # prefetch_related — har turkum uchun alohida so'rov bo'lmasin
        "skill_categories": SkillCategory.objects.prefetch_related("skills"),
        "experiences": Experience.objects.all(),
        "educations": Education.objects.all(),
        "featured_projects": Project.objects.featured().with_tech()[:6],
        "latest_posts": Post.published.prefetch_related("tags")[:3],
        "stats": {
            "projects": Project.objects.count(),
            "technologies": Technology.objects.count(),
            "posts": Post.published.count(),
        },
        "form": form or ContactForm(),
    }


class HomeView(TemplateView):
    """Bir sahifali portfolio: hero, about, skills, tajriba, loyihalar, kontakt."""

    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(home_context())
        return context


def contact_view(request):
    """
    Kontakt formasi (POST).

    Post/Redirect/Get amaliyoti: muvaffaqiyatli yuborishdan keyin redirect
    qilinadi, shunda sahifani yangilash xabarni takrorlab yubormaydi.
    """
    if request.method != "POST":
        return redirect("core:home")

    form = ContactForm(request.POST)
    if form.is_valid():
        message = form.save()
        _notify_owner(message)
        messages.success(request, ui("form_success"))
        return redirect(reverse("core:home") + "#contact")

    messages.error(request, ui("form_error"))
    # Xatolarni ko'rsatish uchun bosh sahifani o'sha forma bilan qayta chizamiz
    return render(request, "core/home.html", home_context(form=form))


def _notify_owner(message):
    """Yangi xabar haqida egasiga email (sozlanmagan bo'lsa — o'tkazib yuboriladi)."""
    recipient = getattr(settings, "CONTACT_NOTIFY_EMAIL", "")
    if not recipient:
        return
    send_mail(
        subject=f"[Portfolio] {message.subject}",
        message=f"{message.name} <{message.email}>\n\n{message.message}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        fail_silently=True,
    )


def projects_api(request):
    """
    Oddiy JSON endpoint — `/api/projects/`.

    DRF ishlatmasdan, faqat Django vositalari bilan. Til `?lang=en` orqali
    ham, URL prefiksi orqali ham aniqlanadi.
    """
    queryset = Project.objects.with_tech()

    tech = request.GET.get("tech")
    if tech:
        queryset = queryset.filter(technologies__slug=tech)

    if request.GET.get("featured") == "1":
        queryset = queryset.filter(is_featured=True)

    data = [
        {
            "title": translated(project, "title"),
            "slug": project.slug,
            "summary": translated(project, "summary"),
            "status": project.status,
            "url": request.build_absolute_uri(project.get_absolute_url()),
            "github": project.github_url,
            "live": project.live_url,
            "technologies": [tech.name for tech in project.technologies.all()],
        }
        for project in queryset
    ]
    return JsonResponse({"count": len(data), "results": data})


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def page_not_found(request, exception):
    """404 sahifasi (config/urls.py dagi handler404)."""
    return render(request, "404.html", status=404)


def server_error(request):
    """
    500 sahifasi.

    Ataylab `render()` emas: xatolik bazadan kelib chiqqan bo'lsa,
    context processor'lar yana so'rov yuborib qayta yiqilmasin.
    """
    from django.template import loader

    html = loader.render_to_string("500.html")
    return HttpResponse(html, status=500)
