from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    """User role for permissions and UI."""

    STUDENT = "student", "Student"
    SHANYRAQ_LEADER = "shanyraq_leader", "Shanyraq Leader"
    STUDENT_COUNCIL = "student_council", "Student Council"
    TEACHER = "teacher", "Teacher"
    ADMIN = "admin", "Admin"


class User(AbstractUser):
    """Custom user with email as identifier and role."""

    email = models.EmailField("email address", unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.email

    # Role checks for code/templates
    @property
    def is_student(self):
        return self.role == Role.STUDENT

    @property
    def is_shanyraq_leader(self):
        return self.role == Role.SHANYRAQ_LEADER

    @property
    def is_student_council(self):
        return self.role == Role.STUDENT_COUNCIL

    @property
    def is_teacher(self):
        return self.role == Role.TEACHER

    @property
    def is_admin_role(self):
        return self.role == Role.ADMIN

    @property
    def is_moderator(self):
        return self.role in (Role.ADMIN, Role.TEACHER)

    def get_profile(self):
        """Return UserProfile, creating one if missing."""
        profile, _ = UserProfile.objects.get_or_create(user=self)
        return profile


class ThemePreference(models.TextChoices):
    LIGHT = "light", "Light"
    DARK = "dark", "Dark"
    SYSTEM = "system", "System"


class UserProfile(models.Model):
    """Extended profile: avatar, class, shanyraq, points, rank, onboarding, theme."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True)
    class_name = models.CharField(max_length=64, blank=True, help_text="e.g. 10A, 11B")
    shanyraq = models.ForeignKey(
        "shanyraq.Shanyraq",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members",
    )
    NIS_points = models.PositiveIntegerField(default=0)
    shanyraq_points = models.PositiveIntegerField(default=0)
    rank = models.CharField(max_length=64, blank=True, help_text="e.g. Bronze, Silver, Gold")
    interests = models.TextField(blank=True, help_text="Comma-separated interests")
    activity_score = models.PositiveIntegerField(default=0, help_text="Cached activity metric")
    last_activity = models.DateTimeField(null=True, blank=True)
    onboarding_completed = models.BooleanField(default=False)
    theme = models.CharField(
        max_length=10,
        choices=ThemePreference.choices,
        default=ThemePreference.SYSTEM,
    )

    class Meta:
        verbose_name = "user profile"
        verbose_name_plural = "user profiles"

    def __str__(self):
        return f"Profile: {self.user.email}"

    def display_name(self):
        return self.full_name.strip() or self.user.email
