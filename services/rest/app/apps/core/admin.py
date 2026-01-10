from django import forms
from django.contrib import admin
from django.http import HttpRequest

from apps.core.models import Color, Faction, GameConstants
from django_json_widget.widgets import JSONEditorWidget


class GameConstantsForm(forms.ModelForm):
    class Meta:
        model = GameConstants

        fields = ("data",)
        widgets = {"data": JSONEditorWidget}


@admin.register(GameConstants)
class GameConstantsAdmin(admin.ModelAdmin):
    form = GameConstantsForm
    list_display = ("id",)
    list_display_links = ("id",)
    fields = (
        "id",
        "data",
    )
    readonly_fields = ("id",)

    def has_add_permission(
        self,
        request: HttpRequest,
        obj: GameConstants = None,
    ) -> bool:
        """В этой таблице может быть в принципе только 1 строка"""
        first_data = GameConstants.objects.exists()
        return not first_data

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: GameConstants = None,
    ) -> bool:
        return False


admin.site.register(Faction)
admin.site.register(Color)
