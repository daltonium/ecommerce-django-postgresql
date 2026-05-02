from django.contrib import admin
from .models import Review, ReviewReply


class ReviewReplyInline(admin.StackedInline):
    model = ReviewReply
    extra = 0


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['user__email', 'product__name']
    inlines = [ReviewReplyInline]