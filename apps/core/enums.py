"""
Shared status and choice enums for the app.
"""
from django.db import models


class Status(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    PENDING = 'pending', 'Pending'
    ACTIVE = 'active', 'Active'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    ARCHIVED = 'archived', 'Archived'
    CANCELLED = 'cancelled', 'Cancelled'


class ModerationStatus(models.TextChoices):
    PENDING = 'pending', 'Pending Review'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    CHANGES_REQUESTED = 'changes_requested', 'Changes Requested'


class PublishStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    PUBLISHED = 'published', 'Published'
    UNPUBLISHED = 'unpublished', 'Unpublished'
