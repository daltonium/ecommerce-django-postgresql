from django.db import models

class TimeStampedModel(models.Model):
    """
    WHY: Every table in BlueCart needs created_at and updated_at.
    Instead of repeating these fields in every model, we inherit from this.
    This is called DRY — Don't Repeat Yourself.
    """
    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True