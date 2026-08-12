"""Kontakt formasi."""

from django import forms

from .i18n import current_lang
from .models import ContactMessage
from .translations import ui


class ContactForm(forms.ModelForm):
    """
    ModelForm — yuborilgan xabar to'g'ridan-to'g'ri bazaga yoziladi.

    `honeypot` maydoni botlarga qarshi: u ekranda ko'rinmaydi, odam uni
    to'ldirmaydi. To'ldirilgan bo'lsa — spam deb hisoblanadi.
    """

    honeypot = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "subject": forms.TextInput(),
            "message": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "name": ui("form_name"),
            "email": ui("form_email"),
            "subject": ui("form_subject"),
            "message": ui("form_message"),
        }
        for name, field in self.fields.items():
            if name == "honeypot":
                continue
            field.label = placeholders.get(name, field.label)
            field.widget.attrs.setdefault("placeholder", placeholders.get(name, ""))
            field.widget.attrs["class"] = "form-control"

    def clean_honeypot(self):
        if self.cleaned_data.get("honeypot"):
            raise forms.ValidationError("Spam aniqlandi.")
        return ""

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if len(message) < 10:
            errors = {
                "uz": "Xabar juda qisqa — kamida 10 ta belgi yozing.",
                "en": "Message is too short — please write at least 10 characters.",
            }
            raise forms.ValidationError(errors.get(current_lang(), errors["uz"]))
        return message
