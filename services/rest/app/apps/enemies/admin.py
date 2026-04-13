from django import forms
from django.contrib import admin

from apps.enemies.models import Deathwish, Enemy, EnemyLeader, EnemyLeaderAbility, EnemyPassiveAbility, Move
from django_json_widget.widgets import JSONEditorWidget


admin.site.register(Move)
admin.site.register(EnemyLeaderAbility)
admin.site.register(EnemyPassiveAbility)
admin.site.register(Deathwish)


class EnemyLeaderForm(forms.ModelForm):
    class Meta:
        model = EnemyLeader

        fields = (
            "id",
            "name",
            "image_original",
            "faction",
            "ability",
            "passive_ability",
            "data",
        )
        widgets = {"data": JSONEditorWidget}


class EnemyForm(forms.ModelForm):
    class Meta:
        model = Enemy

        fields = (
            "id",
            "name",
            "image_original",
            "move",
            "color",
            "faction",
            "passive_ability",
            "data",
        )
        widgets = {"data": JSONEditorWidget}


@admin.register(EnemyLeader)
class EnemyLeaderAdmin(admin.ModelAdmin):
    form = EnemyLeaderForm
    list_filter = (
        "faction_id",
        "ability_id",
        "passive_ability_id",
    )
    list_display = [
        "id",
        "name",
        "get_hp",
    ]
    list_display_links = [
        "id",
        "name",
        "get_hp",
    ]
    search_fields = ("name",)

    @admin.display(description="ХП")
    def get_hp(self, obj: EnemyLeader) -> int:
        return obj.data.get("hp")


@admin.register(Enemy)
class EnemyAdmin(admin.ModelAdmin):
    form = EnemyForm
    list_filter = (
        "faction_id",
        "color_id",
        "move_id",
        "passive_ability_id",
        "deathwish",
    )
    list_display = [
        "id",
        "name",
        "get_damage",
        "get_hp",
    ]
    list_display_links = [
        "id",
        "name",
        "get_damage",
        "get_hp",
    ]
    search_fields = ("name",)

    @admin.display(description="Урон")
    def get_damage(self, obj: Enemy) -> int:
        return obj.data.get("damage")

    @admin.display(description="ХП")
    def get_hp(self, obj: Enemy) -> int:
        return obj.data.get("hp")
