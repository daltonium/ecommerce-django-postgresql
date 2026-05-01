from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # WHY inherit from UserAdmin and not ModelAdmin?
    # UserAdmin already knows how to handle password hashing in the admin panel.
    # It shows a proper password change form instead of exposing the hash.

    list_display = ['email', 'username', 'is_seller', 'is_staff']
    # Columns shown in the admin user list

    # Add our custom fields to the admin form
    fieldsets = UserAdmin.fieldsets + (
        ('BlueCart Info', {'fields': ('is_seller',)}),
    )