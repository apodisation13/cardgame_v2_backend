from lib.utils.schemas import Base
from services.api.app.utils.images import build_image_url


class Ability(Base):
    name: str
    description: str


class PassiveAbility(Base):
    name: str | None
    description: str | None


class Deck(Base):
    id: int
    name: str
    leader_id: int
    cards: list[int]
    health: int


class EnemyLeaderAbility(Base):
    name: str | None
    description: str | None


class EnemyPassiveAbility(Base):
    name: str | None
    description: str | None


class Move(Base):
    name: str
    description: str


class Deathwish(Base):
    name: str | None
    description: str | None


class Leader(Base):
    id: int
    name: str
    unlocked: bool
    faction: str
    ability: Ability
    passive_ability: PassiveAbility
    data: dict
    image: str
    newly_added: bool

    @staticmethod
    def get_one(
        row: dict,
        base_url: str,
    ) -> "Leader":
        return Leader(
            id=row["id"],
            name=row["name"],
            unlocked=row["unlocked"],
            faction=row["faction_name"],
            ability=Ability(
                name=row["ability_name"],
                description=row["ability_description"],
            ),
            passive_ability=PassiveAbility(
                name=row["passive_ability_name"],
                description=row["passive_ability_description"],
            ),
            data=row["data"],
            image=build_image_url(base_url, row["image"]),
            newly_added=row["newly_added"],
        )


class Card(Base):
    id: int
    name: str
    unlocked: bool
    faction: str
    color: str
    type: str
    ability: Ability
    passive_ability: PassiveAbility
    data: dict
    image: str
    newly_added: bool

    @staticmethod
    def get_one(
        row: dict,
        base_url: str,
    ) -> "Card":
        return Card(
            id=row["id"],
            name=row["name"],
            unlocked=row["unlocked"],
            faction=row["faction_name"],
            color=row["color_name"],
            type=row["type_name"],
            ability=Ability(
                name=row["ability_name"],
                description=row["ability_description"],
            ),
            passive_ability=PassiveAbility(
                name=row["passive_ability_name"],
                description=row["passive_ability_description"],
            ),
            data=row["data"],
            image=build_image_url(base_url, row["image"]),
            newly_added=row["newly_added"],
        )


class EnemyLeader(Base):
    id: int
    name: str
    faction: str
    ability: EnemyLeaderAbility
    passive_ability: EnemyPassiveAbility
    data: dict
    image: str

    @staticmethod
    def get_one(
        row: dict,
        base_url: str,
    ) -> "EnemyLeader":
        return EnemyLeader(
            id=row["id"],
            name=row["name"],
            faction=row["faction_name"],
            ability=EnemyLeaderAbility(
                name=row["ability_name"],
                description=row["ability_description"],
            ),
            passive_ability=EnemyPassiveAbility(
                name=row["passive_ability_name"],
                description=row["passive_ability_description"],
            ),
            data=row["data"],
            image=build_image_url(base_url, row["image"]),
        )


class Enemy(Base):
    id: int
    name: str
    faction: str
    color: str
    move: Move
    passive_ability: EnemyPassiveAbility
    deathwish: Deathwish
    data: dict
    image: str

    @staticmethod
    def get_one(
        row: dict,
        base_url: str,
    ) -> "Enemy":
        return Enemy(
            id=row["id"],
            name=row["name"],
            faction=row["faction_name"],
            color=row["color_name"],
            move=Move(
                name=row["move_name"],
                description=row["move_description"],
            ),
            passive_ability=EnemyPassiveAbility(
                name=row["passive_ability_name"],
                description=row["passive_ability_description"],
            ),
            deathwish=Deathwish(
                name=row["deathwish_name"],
                description=row["deathwish_description"],
            ),
            data=row["data"],
            image=build_image_url(base_url, row["image"]),
        )


class CardsResponse(Base):
    cards: list[Card]
    leaders: list[Leader]
    enemy_leaders: dict[int, EnemyLeader]
    enemies: dict[int, Enemy]
