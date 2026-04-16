from django.contrib import admin
from .models import String, SetupStorage


@admin.register(String)
class StringAdmin(admin.ModelAdmin):
    list_display = ("string_name", "type", "gauge", "tension")
    search_fields = ("string_name",)
    list_filter = ("type", "gauge")
    ordering = ("string_name",)


@admin.register(SetupStorage)
class SetupStorageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "instrument_type",
        "total_strings",
        "scale_sength",
        "is_multi_scale",
        "string_type",
        "selected_tuning",
        "total_tension",
        "is_public"
    )

    search_fields = (
        "user__email",
        "instrument_type",
        "string_type",
        "selected_tuning",
    )

    list_filter = (
        "instrument_type",
        "is_multi_scale",
        "is_public",
        "string_type",
    )


    filter_horizontal = ("strings",)


    ordering = ("-id",)

    list_per_page = 20