from django.contrib import admin

from apps.accounts.models import DjangoAuthUser, User


@admin.register(DjangoAuthUser)
class DjangoAuthUserAdmin(admin.ModelAdmin):
    ...


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'is_active',
    )
    readonly_fields = (
        "username",
        "email",
        "password",
    )
    list_filter = (
        'is_active',
    )
    search_fields = (
        'username',
        'email',
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True
