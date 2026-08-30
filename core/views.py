"""Bosh sahifa, kontakt formasi va kichik JSON API."""

import logging

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView

from projects.models import Project, Technology

from . import notifications
from .forms import ContactForm
from .i18n import translated
from .models import (
    Education,
    Experience,
    Notification,
    Profile,
    Skill,
    SkillCategory,
)
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
        notifications.notify(
            Notification.KIND_SPAM,
            "Kontakt formasi limitga urildi",
            "Bitta IP juda ko'p xabar yubormoqchi bo'ldi.",
            request=request,
        )
        messages.error(request, ui("form_too_many"))
        return redirect(reverse("core:home") + "#contact")

    form = ContactForm(request.POST)
    if form.is_valid():
        message = form.save()
        _notify_owner(message, request)
        messages.success(request, ui("form_success"))
        return redirect(reverse("core:home") + "#contact")

    if "honeypot" in form.errors:
        # Odam ko'rmaydigan maydon to'ldirilgan — deyarli aniq bot
        notifications.notify(
            Notification.KIND_SPAM,
            "Bot aniqlandi (honeypot)",
            "Yashirin maydon to'ldirilgan — xabar saqlanmadi.",
            request=request,
        )

    messages.error(request, ui("form_error"))
    # Xatolarni ko'rsatish uchun bosh sahifani o'sha forma bilan qayta chizamiz
    return render(request, "core/home.html", home_context(form=form))


def _notify_owner(message, request=None):
    """
    Yangi xabar haqida egasini xabardor qilish: admin panel, Telegram, email.

    Telegram va email ixtiyoriy — sozlanmagani o'tkazib yuboriladi. Yuborish
    muvaffaqiyatsiz bo'lsa ham forma ishlayveradi: xabar baribir bazada
    saqlangan va admin panelda ko'rinadi. Shuning uchun xatolik yutiladi,
    lekin logga yoziladi — aks holda "nega kelmadi?" degan savolga javob
    topib bo'lmaydi.
    """
    notifications.notify(
        Notification.KIND_MESSAGE,
        f"{message.name} — {message.subject}",
        f"✉️ {message.email}\n\n{message.message}",
        link=reverse("admin:core_contactmessage_change", args=[message.pk]),
        request=request,
    )
    _notify_owner_email(message)


def _notify_owner_email(message):
    """Egasiga email ogohlantirish (CONTACT_NOTIFY_EMAIL bo'sh bo'lsa — yo'q)."""
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


def resume_download(request):
    """
    CV faylini beradi va yuklab olinganini qayd etadi.

    Nega to'g'ridan-to'g'ri `profile.resume.url` emas: media faylga havola
    bosilganini Django umuman ko'rmaydi. CV yuklab olgan odam — kontakt
    formasidan yozmasa ham — eng kuchli signal: ish beruvchi sizni tekshiryapti.
    Shuning uchun havola shu view orqali o'tadi, u faqat hisobga oladi va
    faylning haqiqiy manziliga yo'naltiradi.
    """
    profile = Profile.objects.get_active()
    if not profile or not profile.resume:
        raise Http404("CV fayli yuklanmagan.")

    # Bitta odam sahifani bir necha marta yangilasa, har safar bildirishnoma
    # kelmasin — bir soatlik oyna ichida IP bo'yicha bir marta.
    key = f"resume-seen:{_client_ip(request)}"
    if not cache.get(key):
        cache.set(key, 1, timeout=3600)
        notifications.notify(
            Notification.KIND_RESUME,
            "CV yuklab olindi",
            f"Kimdir «{profile.full_name}» CV faylini yuklab oldi.",
            request=request,
        )

    return redirect(profile.resume.url)


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

    _report_server_error(request)

    html = loader.render_to_string("500.html")
    return HttpResponse(html, status=500)


def _report_server_error(request):
    """
    Sayt yiqilganini Telegram'ga va admin panelga bildiradi.

    Nega kerak: Railway'dagi sayt buzilsa, buni faqat mehmon ko'radi va
    hech kimga aytmaydi. Bu yerda esa xato darhol telefonga tushadi.

    Nega o'z ichida `try`: bu funksiya xato ishlov berish paytida chaqiriladi.
    Agar u ham yiqilsa, mehmon 500 sahifasi o'rniga bo'sh ekran ko'radi.
    Ayniqsa baza yiqilgan bo'lsa — bildirishnomani yozib bo'lmaydi.
    """
    try:
        notifications.notify(
            Notification.KIND_ERROR,
            "Saytda xatolik (500)",
            f"Sahifa: {request.get_full_path()}",
            request=request,
        )
    except Exception:
        logger.exception("Xatolik haqida bildirishnoma yuborib bo'lmadi")
