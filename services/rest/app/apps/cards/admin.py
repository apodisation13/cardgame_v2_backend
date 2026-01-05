from django.contrib import admin

from apps.cards.models import Type, Ability, PassiveAbility


admin.site.register(Type)
admin.site.register(Ability)
admin.site.register(PassiveAbility)
