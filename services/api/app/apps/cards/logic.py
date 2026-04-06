import asyncpg

from services.api.app.apps.cards.schemas import Card, Enemy, EnemyLeader, Leader


async def get_enemies(
    connection: asyncpg.Connection,
    base_url: str,
) -> dict[int, Enemy]:
    enemies = await connection.fetch(
        """
            SELECT
                enemies.id,
                enemies.name,

                factions.name AS faction_name,
                colors.name AS color_name,

                moves.name AS move_name,
                moves.description AS move_description,

                enemy_passive_abilities.name AS passive_ability_name,
                enemy_passive_abilities.description AS passive_ability_description,

                deathwishes.name AS deathwish_name,
                deathwishes.description AS deathwish_description,

                enemies.data,
                enemies.image_original AS image
            FROM
                enemies
            JOIN
                factions ON enemies.faction_id = factions.id
            JOIN
                colors ON enemies.color_id = colors.id
            JOIN
                moves ON enemies.move_id = moves.id
            LEFT JOIN
                deathwishes ON enemies.deathwish_id = deathwishes.id
            LEFT JOIN
                enemy_passive_abilities ON enemies.passive_ability_id = enemy_passive_abilities.id
            ORDER BY
                enemies.faction_id,
                enemies.data ->> 'hp' DESC,
                enemies.data ->> 'damage' DESC
        """,
    )

    return {row["id"]: Enemy.get_one(row, base_url) for row in enemies}


async def get_enemy_leaders(
    connection: asyncpg.Connection,
    base_url: str,
) -> dict[int, EnemyLeader]:
    enemy_leaders = await connection.fetch(
        """
            SELECT
                enemy_leaders.id,
                enemy_leaders.name,

                factions.name AS faction_name,

                enemy_leader_abilities.name AS ability_name,
                enemy_leader_abilities.description AS ability_description,

                enemy_passive_abilities.name AS passive_ability_name,
                enemy_passive_abilities.description AS passive_ability_description,

                enemy_leaders.data,
                enemy_leaders.image_original AS image
            FROM
                enemy_leaders
            JOIN
                factions ON enemy_leaders.faction_id = factions.id
            LEFT JOIN
                enemy_leader_abilities ON enemy_leaders.ability_id = enemy_leader_abilities.id
            LEFT JOIN
                enemy_passive_abilities ON enemy_leaders.passive_ability_id = enemy_passive_abilities.id
        """,
    )

    return {row["id"]: EnemyLeader.get_one(row, base_url) for row in enemy_leaders}


async def get_leaders(
    connection: asyncpg.Connection,
    base_url: str,
) -> list[Leader]:
    leaders: list[dict] = await connection.fetch(
        """
            SELECT
                leaders.id,
                leaders.name,
                leaders.unlocked,

                factions.name AS faction_name,

                abilities.name AS ability_name,
                abilities.description AS ability_description,

                passive_abilities.name AS passive_ability_name,
                passive_abilities.description AS passive_ability_description,

                leaders.data,
                leaders.image_original AS image,
                leaders.newly_added
            FROM
                leaders
            JOIN
                factions ON leaders.faction_id = factions.id
            JOIN
                abilities ON leaders.ability_id = abilities.id
            LEFT JOIN
                passive_abilities ON leaders.passive_ability_id = passive_abilities.id
            ORDER BY
                leaders.faction_id,
                (leaders.data ->> 'hp')::int DESC,
                (leaders.data ->> 'charges')::int DESC
        """,
    )

    return [Leader.get_one(row, base_url) for row in leaders]


async def get_cards(
    connection: asyncpg.Connection,
    base_url: str,
) -> list[Card]:
    cards: list[dict] = await connection.fetch(
        """
            SELECT
                cards.id,
                cards.name,
                cards.unlocked,

                factions.name AS faction_name,
                colors.name AS color_name,
                types.name AS type_name,

                abilities.name AS ability_name,
                abilities.description AS ability_description,

                passive_abilities.name AS passive_ability_name,
                passive_abilities.description AS passive_ability_description,

                cards.data,
                cards.image_original AS image,
                cards.newly_added
            FROM
                cards
            JOIN
                factions ON cards.faction_id = factions.id
            JOIN
                colors ON cards.color_id = colors.id
            JOIN
                types ON cards.type_id = types.id
            JOIN
                abilities ON cards.ability_id = abilities.id
            LEFT JOIN
                passive_abilities ON cards.passive_ability_id = passive_abilities.id
            ORDER BY
                cards.color_id DESC,
                (cards.data ->> 'damage')::int DESC,
                (cards.data ->> 'hp')::int DESC,
                (cards.data ->> 'charges')::int DESC
        """,
    )

    return [Card.get_one(row, base_url) for row in cards]
