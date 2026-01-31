"""
Event creation wizard forms and approval forms.
"""
from django import forms

from .models import EventPolicy, EventStatus


class EventWizardStep1Form(forms.Form):
    """Step 1: Title and description."""
    title = forms.CharField(max_length=255, widget=forms.TextInput(attrs={"class": "input-field", "placeholder": "Event title"}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "input-field", "rows": 4, "placeholder": "Description"}))


class EventWizardStep2Form(forms.Form):
    """Step 2: Dates and location."""
    start_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"class": "input-field", "type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d"],
    )
    end_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"class": "input-field", "type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d"],
    )
    location = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={"class": "input-field", "placeholder": "Venue or room"}))

    def clean(self):
        data = super().clean()
        start = data.get("start_at")
        end = data.get("end_at")
        if start and end and end <= start:
            self.add_error("end_at", "End must be after start.")
        return data


class EventWizardStep3Form(forms.Form):
    """Step 3: Policy (optional) and confirm."""
    policy = forms.ModelChoiceField(
        queryset=EventPolicy.objects.none(),
        required=False,
        empty_label="— No policy —",
        widget=forms.Select(attrs={"class": "input-field"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["policy"].queryset = EventPolicy.objects.filter(is_active=True)


class EventApproveRejectForm(forms.Form):
    """Admin/Teacher approval or rejection with comment."""
    action = forms.ChoiceField(choices=[("approve", "Approve"), ("reject", "Reject")], widget=forms.HiddenInput())
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "input-field", "rows": 3, "placeholder": "Comment (required for rejection)"}))

    def clean(self):
        data = super().clean()
        if data.get("action") == "reject" and not (data.get("comment") or "").strip():
            self.add_error("comment", "Please provide a reason for rejection.")
        return data
