from django.contrib import admin

from ..models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "display_name")
    search_fields = ("username", "display_name")
    readonly_fields = ("user_id",)
