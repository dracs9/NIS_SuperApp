from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.events.models import Event, EventStatus
from apps.shanyraq.models import Shanyraq
from apps.spaces.models import BookingStatus, Space, SpaceBooking

User = get_user_model()


class Command(BaseCommand):
    help = "Create test data for moderation dashboard"

    def handle(self, *args, **options):
        # Create test user if not exists
        user, created = User.objects.get_or_create(
            email="test@student.nis.kz",
            defaults={
                "username": "teststudent",
                "role": "student",
                "first_name": "Test",
                "last_name": "Student",
            },
        )
        if created:
            user.set_password("password123")
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created test user: {user.email}"))

        # Create test teacher/moderator
        moderator, created = User.objects.get_or_create(
            email="moderator@nis.kz",
            defaults={
                "username": "moderator",
                "role": "teacher",
                "first_name": "Test",
                "last_name": "Moderator",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            moderator.set_password("password123")
            moderator.save()
            self.stdout.write(self.style.SUCCESS(f"Created moderator: {moderator.email}"))

        # Create test shanyraq
        shanyraq, created = Shanyraq.objects.get_or_create(
            name="Test Shanyraq", defaults={"slug": "test-shanyraq"}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created shanyraq: {shanyraq.name}"))

        # Create test space
        space, created = Space.objects.get_or_create(
            name="Test Classroom",
            defaults={
                "space_type": "classroom",
                "capacity": 30,
                "location": "Building A, Room 101",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created space: {space.name}"))

        # Create pending event
        tomorrow = timezone.now() + timezone.timedelta(days=1)
        event, created = Event.objects.get_or_create(
            title="Test School Event",
            defaults={
                "description": "A test event for moderation testing",
                "start_at": tomorrow.replace(hour=14, minute=0),
                "end_at": tomorrow.replace(hour=16, minute=0),
                "location": "Main Hall",
                "status": EventStatus.PENDING,
                "created_by": user,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created pending event: {event.title}"))

        # Create pending booking
        booking, created = SpaceBooking.objects.get_or_create(
            space=space,
            booked_by=user,
            start_time=tomorrow.replace(hour=10, minute=0),
            end_time=tomorrow.replace(hour=11, minute=0),
            defaults={
                "purpose": "Test class session",
                "attendees_count": 25,
                "status": BookingStatus.PENDING,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created pending booking: {booking}"))

        self.stdout.write(self.style.SUCCESS("Test data creation completed!"))
        self.stdout.write(
            "You can now access the moderation dashboard at: http://127.0.0.1:8000/moderation/dashboard/"
        )
        self.stdout.write("Login with: moderator@nis.kz / password123")
