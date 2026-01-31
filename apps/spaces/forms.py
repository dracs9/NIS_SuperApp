"""
Space booking forms.
"""
from datetime import datetime

from django import forms

from .models import Space, SpaceBooking


class BookingRequestForm(forms.Form):
    """Form for creating a new booking request."""
    space = forms.ModelChoiceField(
        queryset=Space.objects.none(),
        widget=forms.Select(attrs={"class": "input-field"}),
    )
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"class": "input-field", "type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"],
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"class": "input-field", "type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"],
    )
    purpose = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "input-field", "rows": 3, "placeholder": "Purpose of booking"}),
    )
    attendees_count = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={"class": "input-field", "placeholder": "Number of attendees"}),
    )

    def __init__(self, *args, **kwargs):
        space_id = kwargs.pop("space_id", None)
        super().__init__(*args, **kwargs)
        self.fields["space"].queryset = Space.objects.filter(is_active=True).order_by("name")
        if space_id:
            self.fields["space"].initial = space_id

    def clean(self):
        data = super().clean()
        start = data.get("start_time")
        end = data.get("end_time")
        if start and end and end <= start:
            self.add_error("end_time", "End time must be after start time.")
        space = data.get("space")
        attendees = data.get("attendees_count")
        if space and attendees and attendees > space.capacity:
            self.add_error("attendees_count", f"Exceeds space capacity ({space.capacity}).")
        return data


class BookingApproveRejectForm(forms.Form):
    """Admin/Teacher approval or rejection with comment."""
    action = forms.ChoiceField(
        choices=[("approve", "Approve"), ("reject", "Reject")],
        widget=forms.HiddenInput(),
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "input-field", "rows": 3, "placeholder": "Comment (required for rejection)"}),
    )

    def clean(self):
        data = super().clean()
        if data.get("action") == "reject" and not (data.get("comment") or "").strip():
            self.add_error("comment", "Please provide a reason for rejection.")
        return data
