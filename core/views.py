"""Bosh sahifa, kontakt formasi va kichik JSON API."""

import logging

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView

from projects.models import Project, Technology

from .forms import ContactForm
from .i18n import translated
from .models import Education, Experience, Skill, SkillCategory
from .translations import ui

logger = logging.getLogger(__name__)


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
        "stats": {
            "projects": Project.objects.count(),
            "technologies": Technology.objects.count(),
            "skills": Skill.objects.count(),
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


def _client_ip(request):
    """
    Mijozning IP manzili.

    `X-Forwarded-For` sarlavhasiga faqat sayt proxy ortida turgani aniq
    bo'lgandagina ishonamiz (`TRUST_PROXY_IP`). Aks holda uni istalgan odam
    o'zi yozib yuborib, har so'rovda yangi IP ko'rsatib rate limit'ni
    chetlab o'tishi mumkin edi.
    """
    if getattr(settings, "TRUST_PROXY_IP", False):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "") or "noma'lum"


def _contact_rate_exceeded(request):
    """
    Bitta IP belgilangan vaqt oynasida nechta xabar yuborganini sanaydi.

    Nega kerak: har bir xabar Gmail'ga xat yuboradi. Cheklovsiz qoldirilsa
    bitta skript bir necha daqiqada pochtani ko'mib tashlaydi, Gmail'ning
    kunlik limitini yeb qo'yadi va bazani keraksiz yozuvlar bilan to'ldiradi.
    """
    limit = getattr(settings, "CONTACT_RATE_LIMIT", 5)
    window = getattr(settings, "CONTACT_RATE_WINDOW", 3600)
    if limit <= 0:
        return False

    key = f"contact-rate:{_client_ip(request)}"
    hits = cache.get(key, 0)
    if hits >= limit:
        return True

    # `window` faqat birinchi urinishda o'rnatiladi, shunda oyna suzib ketmaydi
    if hits == 0:
        cache.set(key, 1, timeout=window)
    else:
        try:
            cache.incr(key)
        except ValueError:
            # Oyna hisob o'qilgandan keyin tugab qolgan bo'lsa
            cache.set(key, 1, timeout=window)
    return False


@require_http_methods(["GET", "POST"])
def contact_view(request):
    """
    Kontakt formasi (POST).

    Post/Redirect/Get amaliyoti: muvaffaqiyatli yuborishdan keyin redirect
    qilinadi, shunda sahifani yangilash xabarni takrorlab yubormaydi.
    """
    if request.method != "POST":
        return redirect("core:home")

    if _contact_rate_exceeded(request):
        logger.warning("Kontakt formasi rate limit: %s", _client_ip(request))
        messages.error(request, ui("form_too_many"))
        return redirect(reverse("core:home") + "#contact")

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
    """
    Yangi xabar haqida egasiga email (sozlanmagan bo'lsa — o'tkazib yuboriladi).

    Xat ketmasa ham forma ishlayveradi: xabar baribir bazada saqlangan va
    admin panelda ko'rinadi. Shuning uchun xatolik yutiladi, lekin logga yoziladi —
    aks holda "nega xat kelmadi?" degan savolga javob topib bo'lmaydi.
    """
    recipient = getattr(settings, "CONTACT_NOTIFY_EMAIL", "")
    if not recipient:
        logger.info("CONTACT_NOTIFY_EMAIL bo'sh — ogohlantirish xati yuborilmadi")
        return

    # Sarlavhadagi yangi qator email sarlavhalarini buzishi mumkin (header
    # injection). Django buni o'zi ham to'xtatadi, lekin ishonchli bo'lgani
    # yaxshi: qator ajratgichlarni bo'shliqqa aylantiramiz va uzunlikni kesamiz.
    subject = " ".join(str(message.subject).splitlines())[:120]

    try:
        send_mail(
            subject=f"[Portfolio] {subject}",
            message=f"{message.name} <{message.email}>\n\n{message.message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
    except Exception:
        logger.exception("Kontakt xabari haqida email yuborib bo'lmadi")


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
