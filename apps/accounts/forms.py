"""
Custom auth forms: school email validation, password strength UI support.
"""

from allauth.account.forms import LoginForm, SignupForm
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from .models import UserProfile


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
    raise ValidationError("Please use your school email address (e.g. name@nis.edu.kz).")


class CustomLoginForm(LoginForm):
    """Login form with remember me and consistent styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["login"].widget.attrs.update(
            {
                "class": "input-field",
                "placeholder": "School email",
                "autocomplete": "email",
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": "input-field",
                "placeholder": "Password",
                "autocomplete": "current-password",
            }
        )
        if "remember" in self.fields:
            self.fields["remember"].widget.attrs[
                "class"
            ] = "rounded border-zinc-300 text-emerald-600 focus:ring-emerald-500 dark:border-zinc-600 dark:bg-zinc-700"


class CustomSignupForm(SignupForm):
    """Signup form with school email validation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update(
            {
                "class": "input-field",
                "placeholder": "School email (e.g. you@nis.edu.kz)",
                "autocomplete": "email",
            }
        )
        self.fields["password1"].widget.attrs.update(
            {
                "class": "input-field",
                "placeholder": "Password",
                "autocomplete": "new-password",
            }
        )
        if "password2" in self.fields:
            self.fields["password2"].widget.attrs.update(
                {
                    "class": "input-field",
                    "placeholder": "Confirm password",
                    "autocomplete": "new-password",
                }
            )

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        validate_school_email(email)
        return email


class ProfileEditForm(forms.ModelForm):
    """Form for editing user profile information."""

    class Meta:
        model = UserProfile
        fields = [
            "avatar",
            "full_name",
            "bio",
            "github_url",
            "instagram_url",
            "linkedin_url",
            "telegram_url",
        ]
        widgets = {
            "bio": forms.Textarea(
                attrs={
                    "rows": 3,
                    "maxlength": 250,
                    "placeholder": "Tell us about yourself...",
                    "class": "w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-md focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 dark:bg-zinc-700 dark:text-zinc-100",
                }
            ),
            "full_name": forms.TextInput(
                attrs={
                    "placeholder": "Your full name",
                    "class": "w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-md focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 dark:bg-zinc-700 dark:text-zinc-100",
                }
            ),
            "github_url": forms.URLInput(
                attrs={
                    "placeholder": "https://github.com/username",
                    "class": "w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-md focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 dark:bg-zinc-700 dark:text-zinc-100",
                }
            ),
            "instagram_url": forms.URLInput(
                attrs={
                    "placeholder": "https://instagram.com/username",
                    "class": "w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-md focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 dark:bg-zinc-700 dark:text-zinc-100",
                }
            ),
            "linkedin_url": forms.URLInput(
                attrs={
                    "placeholder": "https://linkedin.com/in/username",
                    "class": "w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-md focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 dark:bg-zinc-700 dark:text-zinc-100",
                }
            ),
            "telegram_url": forms.TextInput(
                attrs={
                    "placeholder": "@username or https://t.me/username",
                    "class": "w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-md focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 dark:bg-zinc-700 dark:text-zinc-100",
                }
            ),
        }

    def clean_bio(self):
        bio = self.cleaned_data.get("bio", "").strip()
        if len(bio) > 250:
            raise forms.ValidationError("Bio must be 250 characters or less.")
        return bio

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url", "").strip()
        if url and not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        return url

    def clean_instagram_url(self):
        url = self.cleaned_data.get("instagram_url", "").strip()
        if url and not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        return url

    def clean_linkedin_url(self):
        url = self.cleaned_data.get("linkedin_url", "").strip()
        if url and not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        return url
