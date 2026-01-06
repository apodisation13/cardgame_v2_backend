from django.contrib import admin

from apps.enemies.models import Move, EnemyLeaderAbility, EnemyPassiveAbility, Deathwish


admin.site.register(Move)
admin.site.register(EnemyLeaderAbility)
admin.site.register(EnemyPassiveAbility)
admin.site.register(Deathwish)
