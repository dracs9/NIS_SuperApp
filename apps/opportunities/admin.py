from django.contrib import admin

from .models import Opportunity, OpportunityTag


@admin.register(OpportunityTag)
class OpportunityTagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ("title", "opportunity_type", "subject", "deadline", "organization", "is_active", "created_at")
    list_filter = ("opportunity_type", "subject", "is_active")
    search_fields = ("title", "description", "subject", "organization")
    raw_id_fields = ("created_by",)
    filter_horizontal = ("tags",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "deadline"
