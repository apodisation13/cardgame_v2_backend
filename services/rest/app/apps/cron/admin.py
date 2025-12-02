from django.contrib import admin
from django.http import HttpRequest

from apps.cron.models import CronTask


@admin.register(CronTask)
class CronTaskAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "schedule",
        "is_active",
    )
    fields = (
        "name",
        "schedule",
        "is_active",
    )
    readonly_fields = ("id",)
    list_filter = ("is_active",)
    ordering = ("name",)

    def has_add_permission(
        self,
        request: HttpRequest,
    ) -> bool:
        return True

    def has_change_permission(
        self,
        request: HttpRequest,
        obj: CronTask = None,
    ) -> bool:
        return True

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: CronTask = None,
    ) -> bool:
        return True
