from django.contrib import admin

from apps.enemies.models import Deathwish, Enemy, EnemyLeader, EnemyLeaderAbility, EnemyPassiveAbility, Move


admin.site.register(Move)
admin.site.register(EnemyLeaderAbility)
admin.site.register(EnemyPassiveAbility)
admin.site.register(Deathwish)


@admin.register(EnemyLeader)
class EnemyLeaderAdmin(admin.ModelAdmin):
    list_filter = (
        "faction_id",
        "ability_id",
        "has_passive",
        "passive_ability_id",
    )
    list_display = [field.name for field in EnemyLeader._meta.fields]
    list_display_links = [field.name for field in EnemyLeader._meta.fields]


@admin.register(Enemy)
class EnemyAdmin(admin.ModelAdmin):
    list_filter = (
        "faction_id",
        "color_id",
        "move_id",
        "has_passive",
        "passive_ability_id",
        "has_deathwish",
        "deathwish",
    )
    list_display = [field.name for field in Enemy._meta.fields]
    list_display_links = [field.name for field in Enemy._meta.fields]
    search_fields = ["name"]
