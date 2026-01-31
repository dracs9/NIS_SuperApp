"""
Custom auth forms: school email validation, password strength UI support.
"""
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from allauth.account.forms import LoginForm, SignupForm


def get_allowed_email_domains():
    """Allowed school email domains (e.g. @nis.edu.kz)."""
    return getattr(settings, "ACCOUNT_ALLOWED_EMAIL_DOMAINS", ["nis.edu.kz"])


def validate_school_email(value):
    """Require email to end with an allowed domain."""
    domains = get_allowed_email_domains()
    value = (value or "").strip().lower()
    if not value:
        return
    for domain in domains:
        if value.endswith("@" + domain):
            return
    raise ValidationError(
        "Please use your school email address (e.g. name@nis.edu.kz)."
    )


class CustomLoginForm(LoginForm):
    """Login form with remember me and consistent styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["login"].widget.attrs.update({
            "class": "input-field",
            "placeholder": "School email",
            "autocomplete": "email",
        })
        self.fields["password"].widget.attrs.update({
            "class": "input-field",
            "placeholder": "Password",
            "autocomplete": "current-password",
        })
        if "remember" in self.fields:
            self.fields["remember"].widget.attrs["class"] = "rounded border-zinc-300 text-emerald-600 focus:ring-emerald-500 dark:border-zinc-600 dark:bg-zinc-700"


class CustomSignupForm(SignupForm):
    """Signup form with school email validation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update({
            "class": "input-field",
            "placeholder": "School email (e.g. you@nis.edu.kz)",
            "autocomplete": "email",
        })
        self.fields["password1"].widget.attrs.update({
            "class": "input-field",
            "placeholder": "Password",
            "autocomplete": "new-password",
        })
        if "password2" in self.fields:
            self.fields["password2"].widget.attrs.update({
                "class": "input-field",
                "placeholder": "Confirm password",
                "autocomplete": "new-password",
            })

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        validate_school_email(email)
        return email
