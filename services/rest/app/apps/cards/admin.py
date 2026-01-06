from django.contrib import admin

from apps.cards.models import Type, Ability, PassiveAbility, Leader, Card

admin.site.register(Type)
admin.site.register(Ability)
admin.site.register(PassiveAbility)



@admin.register(Leader)
class LeaderAdmin(admin.ModelAdmin):
    list_filter = (
        "faction_id",
        "ability_id",
        "has_passive",
        "passive_ability_id",
    )
    list_display = [field.name for field in Leader._meta.fields]
    list_display_links = [field.name for field in Leader._meta.fields]
    search_fields = (
        'name',
    )


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_filter = (
        "faction_id",
        "color_id",
        "type_id",
        "ability_id",
        "has_passive",
        "passive_ability_id",
    )
    list_display = [field.name for field in Card._meta.fields]
    list_display_links = [field.name for field in Card._meta.fields]
    search_fields = (
        'name',
    )
