from django import forms
from django.contrib import admin

from apps.cards.models import Ability, Card, CardDeck, Deck, Leader, PassiveAbility, Type
from django_json_widget.widgets import JSONEditorWidget


admin.site.register(Type)
admin.site.register(Ability)
admin.site.register(PassiveAbility)


class LeaderForm(forms.ModelForm):
    class Meta:
        model = Leader

        fields = (
            "id",
            "name",
            "unlocked",
            "image_original",
            "faction",
            "ability",
            "passive_ability",
            "data",
        )
        widgets = {"data": JSONEditorWidget}


class CardForm(forms.ModelForm):
    class Meta:
        model = Card

        fields = (
            "id",
            "name",
            "unlocked",
            "image_original",
            "type",
            "color",
            "faction",
            "ability",
            "passive_ability",
            "newly_added",
            "data",
        )
        widgets = {"data": JSONEditorWidget}


@admin.register(Leader)
class LeaderAdmin(admin.ModelAdmin):
    form = LeaderForm
    list_filter = (
        "faction_id",
        "ability_id",
        "passive_ability_id",
    )
    list_display = [
        "id",
        "name",
        "get_damage",
        "get_charges",
        "get_hp",
    ]
    list_display_links = [
        "id",
        "name",
        "get_damage",
        "get_charges",
        "get_hp",
    ]
    search_fields = ("name",)

    @admin.display(description="Урон")
    def get_damage(self, obj: Leader) -> int:
        return obj.data.get("damage")

    @admin.display(description="Заряды")
    def get_charges(self, obj: Leader) -> int:
        return obj.data.get("charges")

    @admin.display(description="ХП")
    def get_hp(self, obj: Leader) -> int:
        return obj.data.get("hp")


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    form = CardForm
    list_filter = (
        "faction_id",
        "color_id",
        "type_id",
        "ability_id",
        "passive_ability_id",
    )
    list_display = [
        "id",
        "name",
        "get_color_name",
        "get_type_name",
        "get_damage",
        "get_charges",
        "get_hp",
    ]
    list_display_links = [
        "id",
        "name",
        "get_color_name",
        "get_type_name",
        "get_damage",
        "get_charges",
        "get_hp",
    ]
    search_fields = ("name",)

    @admin.display(description="Цвет", ordering="color__name")
    def get_color_name(self, obj: Card) -> str:
        return obj.color.name

    @admin.display(description="Тип", ordering="type__name")
    def get_type_name(self, obj: Card) -> str:
        return obj.type.name

    @admin.display(description="Урон")
    def get_damage(self, obj: Card) -> int:
        return obj.data.get("damage")

    @admin.display(description="Заряды")
    def get_charges(self, obj: Card) -> int:
        return obj.data.get("charges")

    @admin.display(description="ХП")
    def get_hp(self, obj: Card) -> int:
        return obj.data.get("hp")


class CardDeckInLine(admin.TabularInline):
    model = CardDeck
    extra = 0
    autocomplete_fields = ["card"]


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    inlines = (CardDeckInLine,)
    list_filter = ("leader_id",)
    list_display = [field.name for field in Deck._meta.fields]
    list_display_links = [field.name for field in Deck._meta.fields]
    search_fields = ("name",)
