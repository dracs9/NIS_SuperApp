from django.db import models


class Shanyraq(models.Model):
    """Shanyraq group (e.g. class/house)."""
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=64, unique=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Shanyraq'
        verbose_name_plural = 'Shanyraqs'

    def __str__(self):
        return self.name
