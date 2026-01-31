from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    """User role for permissions (e.g. admin, moderator, member)."""
    name = models.CharField(max_length=64, unique=True)
    code = models.SlugField(max_length=64, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class User(AbstractUser):
    """Custom user with email as identifier and optional role."""
    email = models.EmailField('email address', unique=True)
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
    )
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    @property
    def is_moderator(self):
        return self.role and self.role.code in ('admin', 'moderator')

    @property
    def is_admin(self):
        return self.role and self.role.code == 'admin'
