from django.contrib import admin
from .models import Shanyraq


@admin.register(Shanyraq)
class ShanyraqAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
