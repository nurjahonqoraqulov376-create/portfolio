from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("contact/", views.contact_view, name="contact"),
    # CV havolasi shu view orqali o'tadi — yuklab olinganini bilish uchun
    path("cv/", views.resume_download, name="resume_download"),
]
