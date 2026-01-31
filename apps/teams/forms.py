"""Team forms."""
from django import forms

from apps.opportunities.models import Opportunity


class TeamCreateForm(forms.Form):
    """Form for creating a team."""
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={"class": "input-field", "placeholder": "Team name"}))
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "input-field", "rows": 4, "placeholder": "Description"}),
    )
    opportunity = forms.ModelChoiceField(
        Opportunity.objects.filter(is_active=True),
        required=False,
        empty_label="— No opportunity —",
        widget=forms.Select(attrs={"class": "input-field"}),
    )


class TeamInviteForm(forms.Form):
    """Form for inviting a user to join a team."""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "input-field", "placeholder": "User email"}),
        label="Invite by email",
    )
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "input-field", "rows": 3, "placeholder": "Optional invite message"}),
    )

    def clean_email(self):
        from django.contrib.auth import get_user_model
        email = self.cleaned_data.get("email", "").strip().lower()
        User = get_user_model()
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise forms.ValidationError("User not found with this email.")
        self._invitee = user
        return email

    @property
    def invitee(self):
        return getattr(self, "_invitee", None)
