from django.contrib import admin
from .models import CustomUser, OtpTable
# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    # Remove username field completely
    model = CustomUser

    # Display columns in admin list
    list_display = (
        "id",
        "email",
        "full_name",
        "phone",
        "status",
        "is_email_verified",
        "is_phone_verified",
        "is_staff",
        "is_superuser",
        "last_activity",
        "created_at",
    )

    # Advanced search
    search_fields = (
        "email",
        "full_name",
        "phone",
    )

    # Filters on right sidebar
    list_filter = (
        "status",
        "is_email_verified",
        "is_phone_verified",
        "is_staff",
        "is_superuser",
        "created_at",
        "last_activity",
    )

    # Default ordering
    ordering = ("-created_at",)

    # Fields shown in detail page
    fieldsets = (
        ("Basic Info", {
            "fields": ("email", "password", "full_name", "phone", "image")
        }),
        ("Permissions", {
            "fields": (
                "status",
                "is_email_verified",
                "is_phone_verified",
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
        }),
        ("Location Info", {
            "fields": ("latitude", "longitude", "last_activity"),
        }),
        ("Important Dates", {
            "fields": ("last_login", "created_at", "updated_at"),
        }),
    )

    # Fields for add user form
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "full_name"),
        }),
    )

    # Read-only fields
    readonly_fields = ("created_at", "updated_at", "last_login")

    # Prevent showing username anywhere
    exclude = ("username",)

from django.contrib import admin

admin.site.site_header = "Sweet Tune Admin"
admin.site.site_title = "Sweet Tune Portal"
admin.site.index_title = "Welcome to Sweet Tune Dashboard"