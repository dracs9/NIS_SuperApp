from django.db import models


class Skill(models.Model):
    """Skill that users can have."""

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(
        max_length=50,
        choices=[
            ("technical", "Technical"),
            ("creative", "Creative"),
            ("leadership", "Leadership"),
            ("academic", "Academic"),
            ("sports", "Sports"),
            ("other", "Other"),
        ],
        default="other",
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "skill"
        verbose_name_plural = "skills"
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.get_category_display()}: {self.name}"


class UserSkill(models.Model):
    """User's skill with proficiency level."""

    LEVEL_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
        ("expert", "Expert"),
    ]

    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="user_skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="user_skills")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="beginner")
    is_featured = models.BooleanField(default=False, help_text="Show on profile")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "user skill"
        verbose_name_plural = "user skills"
        unique_together = [["user", "skill"]]
        ordering = ["-is_featured", "skill__category", "skill__name"]

    def __str__(self):
        return f"{self.user.email} - {self.skill.name} ({self.get_level_display()})"
