from django.contrib import admin
from django.http import HttpRequest

from apps.accounts.models import DjangoAuthUser, User


@admin.register(DjangoAuthUser)
class DjangoAuthUserAdmin(admin.ModelAdmin): ...


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "is_active",
    )
    fields = (
        "username",
        "email",
        "is_active",
    )
    readonly_fields = (
        "id",
        "username",
        "email",
        "password",
    )
    list_filter = ("is_active",)
    search_fields = (
        "username",
        "email",
    )

    def has_add_permission(
        self,
        request: HttpRequest,
    ) -> bool:
        return False

    def has_change_permission(
        self,
        request: HttpRequest,
        obj: User = None,
    ) -> bool:
        return True

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: User = None,
    ) -> bool:
        return True
