from django.contrib import admin

from apps.seasons.models import LevelEnemy, LevelRelatedLevels, Level, Season


admin.site.register(Season)


class LevelEnemyInLine(admin.TabularInline):
    model = LevelEnemy
    extra = 0
    verbose_name_plural = 'level enemies'
    autocomplete_fields = (
        'enemy',
    )


class LevelInline(admin.TabularInline):
    model = LevelRelatedLevels
    fk_name = "level"
    fields = (
        "line",
        "related_level",
    )
    extra = 0
    verbose_name_plural = 'level related levels'
    autocomplete_fields = (
        'related_level',
    )


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    inlines = (
        LevelEnemyInLine,
        LevelInline,
    )
    list_filter = (
        "difficulty",
        "enemy_leader_id",
        "season",
    )
    list_display = (
        "id",
        "name",
        "starting_enemies_number",
        "difficulty",
        "enemy_leader_admin",
        "number_of_enemies_admin",
        "get_related_levels",
        "x",
        "y",
        "season",
    )
    list_display_links = (
        "id",
        "name",
    )
    search_fields = (
        'name',
    )

    @admin.display(description="enemy_leader")
    def enemy_leader_admin(self, obj):
        return f"{obj.enemy_leader.name} - {obj.enemy_leader.ability}"

    @admin.display(description="en_№")
    def number_of_enemies_admin(self, obj):
        return obj.number_of_enemies()
