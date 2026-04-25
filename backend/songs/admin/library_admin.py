from django.contrib import admin

from ..models import Library


@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ("user", "total_count")
    search_fields = ("user__display_name",)
    readonly_fields = ("total_count",)
    filter_horizontal = ("songs",)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.sync_total_count()
