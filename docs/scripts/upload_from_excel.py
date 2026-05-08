import json
import os
import sys
import asyncio

from pyexcel_odsr import get_data


# Добавляем корневую директорию проекта в Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from lib.utils.config.env_types import load_env
from lib.utils.config.base import get_config
from lib.utils.db.pool import Database


async def upload_with_only_names(file, db_pool, page_name, table_name):
    print(f"Inserting {table_name}")

    data: list[list] = file[page_name]  # [[1, damage, hp, etc], ]

    # пропускаем первую строчку, там названия столбцов (срез) + не берем id
    data_to_insert = [row[1] for row in data[1:] if row]

    async with db_pool.acquire() as connection:
        # ищем сколько сейчас строк в бд, чтобы инзертить только все следующие
        existing_row_count = await connection.fetchval(f"""select count(*) from {table_name}""")

        if existing_row_count == len(data_to_insert):
            # ну а тут если данных столько же, сразу выходим, ничего не пытаемся инзертить
            print(f"Nothing to insert in table {table_name}")
            return

        # инзертим только начиная с последнего существующего
        await connection.executemany(
            f"""INSERT INTO {table_name} (name) VALUES ($1)""",
            [(row, ) for row in data_to_insert[existing_row_count:]],
        )


async def upload_with_names_and_descriptions(file, db_pool, page_name, table_name):
    print(f"Inserting {table_name}")

    data = file[page_name]

    # а здесь берем name, description, столбцы 2 и 3 + так же пропускаем первую строку, там названия столбцов
    data_to_insert = [row[1:3] for row in data[1:] if row]

    async with db_pool.acquire() as connection:
        existing_row_count = await connection.fetchval(f"""select count(*) from {table_name}""")

        if existing_row_count == len(data_to_insert):
            print(f"Nothing to insert in table {table_name}")
            return

        await connection.executemany(
            f"""INSERT INTO {table_name} (name, description) VALUES ($1, $2)""",
            data_to_insert[existing_row_count:],
        )


async def upload_leaders(file, db_pool):
    print("Inserting leaders")

    data = file["Cards.Leader_2"]

    header = data[0]
    data_idx = header.index('data')

    needed_data = []
    for row in data[1:]:
        if not row:
            continue
        element = [None if v == "" else v for v in row[1:len(row) - 1]]
        element[data_idx - 1] = json.loads(element[data_idx - 1].replace("“", '"').replace("”", '"'))
        needed_data.append(element)

    print(needed_data)

    async with db_pool.acquire() as connection:
        existing_row_count = await connection.fetchval("""select count(*) from leaders""")
        print(existing_row_count, len(needed_data))

        if existing_row_count == len(needed_data):
            print("Nothing to insert in table leaders")
            return

        await connection.executemany("""
            INSERT INTO leaders
            (
                name,
                unlocked,
                faction_id,
                ability_id,
                passive_ability_id,
                data,
                image_original
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            needed_data[existing_row_count:],
        )


async def upload_cards(file, db_pool):
    print("Inserting cards")

    data = file["Cards.Card_2"]

    header = data[0]
    data_idx = header.index('data')

    needed_data = []
    for row in data[1:]:
        if not row:
            continue
        element = [None if v == "" else v for v in row[1:10]]
        element[data_idx - 1] = json.loads(element[data_idx - 1].replace("“", '"').replace("”", '"'))
        needed_data.append(element)

    async with db_pool.acquire() as connection:
        existing_row_count = await connection.fetchval("""select count(*) from cards""")
        print(existing_row_count, len(needed_data))

        if existing_row_count == len(needed_data):
            print("Nothing to insert in table cards")
            return

        await connection.executemany("""
            INSERT INTO cards
            (
                name,
                unlocked,
                faction_id,
                color_id,
                type_id,
                ability_id,
                passive_ability_id,
                data,
                image_original
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """,
            needed_data[existing_row_count:],
        )


async def upload_base_deck(file, db_pool):
    print("Inserting base deck")

    async with db_pool.acquire() as connection:
        base_deck_exists = await connection.fetchval("""select name from decks where name = 'base-deck'""")
        print(base_deck_exists)

        if base_deck_exists:
            return

        await connection.execute(
            """
                INSERT INTO decks
                (name, leader_id)
                VALUES ($1, $2)
            """,
            'base-deck',
            1,
        )

        data = file["Cards.CardDeck"]
        print(len(data), data)

        # берем из таблицы только 2 столбца - deck_id, card_id
        data_to_insert = [row[1:3] for row in data[1:] if row]
        print(len(data_to_insert), data_to_insert)

        await connection.executemany(
            """
                INSERT INTO card_decks
                (deck_id, card_id)
                VALUES ($1, $2)
            """,
            data_to_insert,
        )


async def upload_enemy_leaders(file, db_pool):
    print("Inserting enemy leaders")

    data = file["Enemies.EnemyLeader_2"]

    header = data[0]
    data_idx = header.index('data')

    needed_data = []
    for row in data[1:]:
        if not row:
            continue
        element = [None if v == "" else v for v in row[1:7]]
        element[data_idx - 1] = json.loads(element[data_idx - 1].replace("“", '"').replace("”", '"'))
        needed_data.append(element)

    async with db_pool.acquire() as connection:
        existing_row_count = await connection.fetchval("""select count(*) from enemy_leaders""")
        print(existing_row_count, len(needed_data))

        if existing_row_count == len(needed_data):
            print("Nothing to insert in table leaders")
            return

        await connection.executemany("""
            INSERT INTO enemy_leaders
            (
                name,
                faction_id,
                ability_id,
                passive_ability_id,
                data,
                image_original
            )
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            needed_data[existing_row_count:],
        )


async def upload_enemies(file, db_pool):
    print("Inserting enemies")

    data = file["Enemies.Enemy_2"]

    header = data[0]
    data_idx = header.index('data')

    needed_data = []
    for row in data[1:]:
        if not row:
            continue
        element = [None if v == "" else v for v in row[1:9]]
        element[data_idx - 1] = json.loads(element[data_idx - 1].replace("“", '"').replace("”", '"'))
        needed_data.append(element)

    async with db_pool.acquire() as connection:
        existing_row_count = await connection.fetchval("""select count(*) from enemies""")
        print(existing_row_count, len(needed_data))

        if existing_row_count == len(needed_data):
            print("Nothing to insert in table leaders")
            return

        await connection.executemany("""
            INSERT INTO enemies
            (
                name,
                faction_id,
                color_id,
                move_id,
                passive_ability_id,
                deathwish_id,
                data,
                image_original 
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
            needed_data[existing_row_count:],
        )


async def upload_seasons(file, db_pool):
    print("Inserting seasons")

    data = file["Enemies.Season"]

    # берем name, unlocked, description, x, y (столбцы 2,3,4) + так же пропускаем первую строку, там названия столбцов
    data_to_insert = [row[1:6] for row in data[1:] if row]

    async with db_pool.acquire() as connection:
        existing_row_count = await connection.fetchval("""select count(*) from seasons""")

        if existing_row_count == len(data_to_insert):
            print("Nothing to insert in table seasons")
            return

        await connection.executemany(
            """INSERT INTO seasons (name, unlocked, description, x, y) VALUES ($1, $2, $3, $4, $5)""",
            data_to_insert[existing_row_count:],
        )

    data = file["Seasons.SeasonRelatedSeason"]

    data_to_insert = [row[1:4] for row in data[1:] if row]
    print(len(data_to_insert), data_to_insert)

    for element in data_to_insert:
        if element[2] == "NONE":
            element[2] = None
        element.append(f"{element[0]}-{element[1]}")

    print(len(data_to_insert), data_to_insert)
    async with db_pool.acquire() as connection:
        existing_row_count = await connection.fetchval("""select count(*) from season_related_seasons""")
        print(existing_row_count, len(data_to_insert))

        if existing_row_count != len(data_to_insert):
            await connection.executemany(
                """
                    INSERT INTO season_related_seasons
                     (season_id, related_season_id, line, connection)
                     VALUES ($1, $2, $3, $4)
                """,
                data_to_insert[existing_row_count:],
            )


async def upload_levels_enemies(file, db_pool):
    print("Inserting levels")

    data = file["Enemies.Level"]

    data_to_insert = [row[1:9] for row in data[1:] if row]
    print(len(data_to_insert), data_to_insert)

    async with db_pool.acquire() as connection:
        existing_row_count = await connection.fetchval("""select count(*) from levels""")
        print(existing_row_count, len(data_to_insert))

        if existing_row_count != len(data_to_insert):
            await connection.executemany(
                """
                    INSERT INTO levels
                     (
                        name, 
                        starting_enemies_number, 
                        difficulty,
                        enemy_leader_id,
                        unlocked,
                        season_id,
                        x,
                        y
                    )
                     VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                data_to_insert[existing_row_count:],
            )

    data = file["Enemies.LevelEnemy"]

    data_to_insert = [row[1:3] for row in data[1:] if row]
    print(len(data_to_insert), data_to_insert)

    async with db_pool.acquire() as connection:
        existing_row_count = await connection.fetchval("""select count(*) from level_enemies""")
        print(existing_row_count, len(data_to_insert))

        if existing_row_count != len(data_to_insert):
            await connection.executemany(
                """
                    INSERT INTO level_enemies
                     (level_id, enemy_id)
                     VALUES ($1, $2)
                """,
                data_to_insert[existing_row_count:],
            )

    data = file["Enemies.LevelRelatedLevel"]

    data_to_insert = [row[1:4] for row in data[1:] if row]
    print(len(data_to_insert), data_to_insert)

    for element in data_to_insert:
        if element[2] == "NONE":
            element[2] = None
        element.append(f"{element[0]}-{element[1]}")

    print(len(data_to_insert), data_to_insert)
    async with db_pool.acquire() as connection:
        existing_row_count = await connection.fetchval("""select count(*) from level_related_levels""")
        print(existing_row_count, len(data_to_insert))

        if existing_row_count != len(data_to_insert):
            await connection.executemany(
                """
                    INSERT INTO level_related_levels
                     (level_id, related_level_id, line, connection)
                     VALUES ($1, $2, $3, $4)
                """,
                data_to_insert[existing_row_count:],
            )


async def update_leaders(file, db_pool):
    print("Updating leaders")

    data = file["Cards.Leader_2"]

    header = data[0]
    data_idx = header.index('data')

    needed_data = []
    for row in data[1:]:
        if not row:
            continue
        element = [None if v == "" else v for v in row[0:len(row) - 1]]
        element[data_idx] = json.loads(element[data_idx].replace("“", '"').replace("”", '"'))
        needed_data.append(element)

    print(needed_data)

    # массовый апдейт по leaders.id
    async with db_pool.acquire() as connection:
        await connection.executemany("""
            UPDATE leaders
            SET
                name = $2,
                unlocked = $3,
                faction_id = $4,
                ability_id = $5,
                passive_ability_id = $6,
                data = $7,
                image_original = $8
            WHERE
                leaders.id = $1
            """,
            needed_data,
        )


async def update_cards(file, db_pool):
    print("Updating cards")

    data = file["Cards.Card_2"]

    header = data[0]
    data_idx = header.index('data')

    needed_data = []
    for row in data[1:]:
        if not row:
            continue
        element = [None if v == "" else v for v in row[:10]]
        element[data_idx] = json.loads(element[data_idx].replace("“", '"').replace("”", '"'))
        needed_data.append(element)

    # массовый апдейт по cards.id
    async with db_pool.acquire() as connection:
        await connection.executemany("""
            UPDATE cards
            SET
                name = $2,
                unlocked = $3,
                faction_id = $4,
                color_id = $5,
                type_id = $6,
                ability_id = $7,
                passive_ability_id = $8,
                data = $9,
                image_original = $10
            WHERE
                cards.id = $1
            """,
            needed_data,
        )


async def update_enemy_leaders(file, db_pool):
    print("Updating enemy leaders")

    data = file["Enemies.EnemyLeader_2"]

    header = data[0]
    data_idx = header.index('data')

    needed_data = []
    for row in data[1:]:
        if not row:
            continue
        element = [None if v == "" else v for v in row[:7]]
        element[data_idx] = json.loads(element[data_idx].replace("“", '"').replace("”", '"'))
        needed_data.append(element)

    # массовый апдейт по enemy_leaders.id
    async with db_pool.acquire() as connection:
        await connection.executemany("""
            UPDATE enemy_leaders
            SET
                name = $2,
                faction_id = $3,
                ability_id = $4,
                passive_ability_id = $5,
                data = $6,
                image_original = $7
            WHERE
                enemy_leaders.id = $1
            """,
            needed_data,
        )


async def update_enemies(file, db_pool):
    print("Updating enemies")

    data = file["Enemies.Enemy_2"]

    header = data[0]
    data_idx = header.index('data')

    needed_data = []
    for row in data[1:]:
        if not row:
            continue
        element = [None if v == "" else v for v in row[:9]]
        element[data_idx] = json.loads(element[data_idx].replace("“", '"').replace("”", '"'))
        needed_data.append(element)

    # массовый апдейт по enemies.id
    async with db_pool.acquire() as connection:
        await connection.executemany("""
            UPDATE enemies
            SET
                name = $2,
                faction_id = $3,
                color_id = $4,
                move_id = $5,
                passive_ability_id = $6,
                deathwish_id = $7,
                data = $8,
                image_original = $9
            WHERE
                enemies.id = $1
            """,
            needed_data,
        )


async def create(data, db_pool):
    # await upload_with_only_names(data, db_pool, page_name="Faction", table_name="factions")
    # await upload_with_only_names(data, db_pool, page_name="Color", table_name="colors")
    # await upload_with_only_names(data, db_pool, page_name="Type", table_name="types")
    # await upload_with_names_and_descriptions(data, db_pool, page_name="Ability", table_name="abilities")
    # await upload_with_names_and_descriptions(data, db_pool, page_name="CardPassiveAbility", table_name="passive_abilities")
    # await upload_with_names_and_descriptions(data, db_pool, page_name="Move", table_name="moves")
    # await upload_with_names_and_descriptions(data, db_pool, page_name="EnemyPassiveAbility", table_name="enemy_passive_abilities")
    # await upload_with_names_and_descriptions(data, db_pool, page_name="EnemyLeaderAbility", table_name="enemy_leader_abilities")
    # await upload_with_names_and_descriptions(data, db_pool, page_name="Deathwish", table_name="deathwishes")
    #
    # await upload_leaders(data, db_pool)
    # await upload_cards(data, db_pool)
    # await upload_base_deck(data, db_pool)
    # await upload_enemy_leaders(data, db_pool)
    # await upload_enemies(data, db_pool)
    # await upload_seasons(data, db_pool)
    await upload_levels_enemies(data, db_pool)


async def update(data, db_pool):
    await update_leaders(data, db_pool)
    await update_cards(data, db_pool)
    await update_enemy_leaders(data, db_pool)
    await update_enemies(data, db_pool)


async def upload_from_excel():
    load_env()
    config = get_config()
    # config.DB_URL = "postgresql://postgres:strongPass123123@46.243.210.49:5434/gridways_testing"
    config.DB_URL = "postgresql://postgres:iknowYou1932844)@localhost:5432/my_local_test_db"
    db = Database(config)

    data = get_data("database.ods")

    db_pool = await db.connect()

    async with db_pool.acquire() as connection:
        a = await connection.fetch("SELECT * FROM users")
    print(len(a), a)

    await create(data, db_pool)
    # await update(data, db_pool)


if __name__ == "__main__":
    asyncio.run(upload_from_excel())
