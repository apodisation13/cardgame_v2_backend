
from lib.utils.schemas import Base
from services.api.app.utils.images import build_image_url


class Ability(Base):
    name: str
    description: str


class PassiveAbility(Base):
    name: str | None
    description: str | None


class Card(Base):
    id: int
    name: str
    unlocked: bool
    image: str
    faction: str
    color: str
    type: str
    ability: Ability
    damage: int
    charges: int
    hp: int
    heal: int
    has_passive: bool
    has_passive_in_hand: bool
    has_passive_in_deck: bool
    has_passive_in_grave: bool
    passive_ability: PassiveAbility
    value: int
    timer: int
    default_timer: int
    reset_timer: bool
    each_tick: bool

    @staticmethod
    def get_one(
        row: dict,
        base_url: str,
    ) -> "Card":
        return Card(
            id=row["id"],
            name=row["name"],
            unlocked=row["unlocked"],
            image=build_image_url(base_url, row["image"]),
            faction=row["faction_name"],
            color=row["color_name"],
            type=row["type_name"],
            ability=Ability(
                name=row["ability_name"],
                description=row["ability_description"],
            ),
            damage=row["damage"],
            charges=row["charges"],
            hp=row["hp"],
            heal=row["heal"],
            has_passive=row["has_passive"],
            has_passive_in_hand=row["has_passive_in_hand"],
            has_passive_in_deck=row["has_passive_in_deck"],
            has_passive_in_grave=row["has_passive_in_grave"],
            passive_ability=PassiveAbility(
                name=row["passive_ability_name"],
                description=row["passive_ability_description"],
            ),
            value=row["value"],
            timer=row["timer"],
            default_timer=row["default_timer"],
            reset_timer=row["reset_timer"],
            each_tick=row["each_tick"],
        )


class Leader(Base):
    id: int
    name: str
    image: str
    unlocked: bool
    faction: str
    ability: Ability
    damage: int
    charges: int
    heal: int
    has_passive: bool
    passive_ability: PassiveAbility
    value: int
    timer: int
    default_timer: int
    reset_timer: bool

    @staticmethod
    def get_one(
        row: dict,
        base_url: str,
    ) -> "Leader":
        return Leader(
            id=row["id"],
            name=row["name"],
            unlocked=row["unlocked"],
            image=build_image_url(base_url, row["image"]),
            faction=row["faction_name"],
            ability=Ability(
                name=row["ability_name"],
                description=row["ability_description"],
            ),
            damage=row["damage"],
            charges=row["charges"],
            heal=row["heal"],
            has_passive=row["has_passive"],
            passive_ability=PassiveAbility(
                name=row["passive_ability_name"],
                description=row["passive_ability_description"],
            ),
            value=row["value"],
            timer=row["timer"],
            default_timer=row["default_timer"],
            reset_timer=row["reset_timer"],
        )


class CardForDeck(Base):
    card: Card
    count: int = 1


class Deck(Base):
    id: int
    name: str
    leader: Leader
    cards: list[CardForDeck]
    health: int


class EnemyLeaderAbility(Base):
    name: str | None
    description: str | None


class EnemyPassiveAbility(Base):
    name: str | None
    description: str | None


class EnemyLeader(Base):
    id: int
    name: str
    image: str
    faction: str
    hp: int
    base_hp: int
    ability: EnemyLeaderAbility
    has_passive: bool
    passive_ability: EnemyPassiveAbility
    value: int
    timer: int
    default_timer: int
    reset_timer: bool
    each_tick: bool

    @staticmethod
    def get_one(
        row: dict,
        base_url: str,
    ) -> "EnemyLeader":
        return EnemyLeader(
            id=row["id"],
            name=row["name"],
            image=build_image_url(base_url, row["image"]),
            faction=row["faction_name"],
            hp=row["hp"],
            base_hp=row["base_hp"],
            ability=EnemyLeaderAbility(
                name=row["ability_name"],
                description=row["ability_description"],
            ),
            has_passive=row["has_passive"],
            passive_ability=EnemyPassiveAbility(
                name=row["passive_ability_name"],
                description=row["passive_ability_description"],
            ),
            value=row["value"],
            timer=row["timer"],
            default_timer=row["default_timer"],
            reset_timer=row["reset_timer"],
            each_tick=row["each_tick"],
        )


class Move(Base):
    name: str
    description: str


class Deathwish(Base):
    name: str | None
    description: str | None


class Enemy(Base):
    id: int
    name: str
    image: str
    faction: str
    color: str
    move: Move
    damage: int
    hp: int
    base_hp: int
    shield: bool
    has_passive: bool
    has_passive_in_field: bool
    has_passive_in_grave: bool
    has_passive_in_deck: bool
    passive_ability: EnemyPassiveAbility
    value: int
    timer: int
    default_timer: int
    reset_timer: bool
    each_tick: bool
    has_deathwish: bool
    deathwish: Deathwish
    deathwish_value: int

    @staticmethod
    def get_one(
        row: dict,
        base_url: str,
    ) -> "Enemy":
        return Enemy(
            id=row["id"],
            name=row["name"],
            image=build_image_url(base_url, row["image"]),
            faction=row["faction_name"],
            color=row["color_name"],
            move=Move(
                name=row["move_name"],
                description=row["move_description"],
            ),
            damage=row["damage"],
            hp=row["hp"],
            base_hp=row["base_hp"],
            shield=row["shield"],
            has_passive=row["has_passive"],
            has_passive_in_field=row["has_passive_in_field"],
            has_passive_in_grave=row["has_passive_in_grave"],
            has_passive_in_deck=row["has_passive_in_deck"],
            passive_ability=EnemyPassiveAbility(
                name=row["passive_ability_name"],
                description=row["passive_ability_description"],
            ),
            value=row["value"],
            timer=row["timer"],
            default_timer=row["default_timer"],
            reset_timer=row["reset_timer"],
            each_tick=row["each_tick"],
            has_deathwish=row["has_deathwish"],
            deathwish=Deathwish(
                name=row["deathwish_name"],
                description=row["deathwish_description"],
            ),
            deathwish_value=row["deathwish_value"],
        )
