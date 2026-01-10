from django.contrib import admin

from apps.news.models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "is_active",
        "priority",
    )
    fields = (
        "id",
        "title",
        "text",
        "is_active",
        "priority",
        "created_at",
        "updated_at",
    )
    list_display_links = (
        "id",
        "title",
    )
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_active",)
    search_fields = (
        "title",
        "text",
    )
