import os
import sys
import asyncio

from pyexcel_odsr import get_data


# Добавляем корневую директорию проекта в Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from lib.utils.config.env_types import load_env
from lib.utils.config.base import get_config
from lib.utils.db.pool import Database


load_env()
config = get_config()
db = Database(config)


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
            data_to_insert,
        )


async def update_images_in_place(cards_list, img_idx):
    for card in cards_list:

        old_path = card[img_idx]
        # Получаем директорию и имя файла
        dir_part, file_part = old_path.rsplit('/', 1)
        prefix = f"{dir_part}/"

        # Имя без расширения
        name_no_ext = os.path.splitext(file_part)[0]

        # Заменяем одно поле тремя
        card[img_idx:img_idx + 1] = [
            f"{prefix}{name_no_ext}_original.webp",
            f"{prefix}{name_no_ext}_tablet.webp",
            f"{prefix}{name_no_ext}_phone.webp"
        ]

    return cards_list


async def upload_leaders(file, db_pool):
    print("Inserting leaders")

    data = file["Cards.Leader"]
    print(len(data), data)

    # а здесь берем все столбцы, кроме первого (id) + так же пропускаем первую строку, там названия столбцов
    # вместо пустой строки ставим None для инзерта в бд
    needed_data = [row[1:len(row) - 1] for row in data[1:] if row]
    for element in needed_data:
        if element[9] == "":
            element[9] = None

    # добавляем туда измененные картинк
    data_to_insert = await update_images_in_place(needed_data, img_idx=7)
    print(len(data_to_insert), data_to_insert)

    async with db_pool.acquire() as connection:
        existing_row_count = await connection.fetchval("""select count(*) from leaders""")
        print(existing_row_count, len(data_to_insert))

        if existing_row_count == len(data_to_insert):
            print("Nothing to insert in table leaders")
            return

        await connection.executemany("""
            INSERT INTO leaders
            (
                name,
                unlocked,
                faction_id,
                ability_id,
                damage,
                charges,
                heal,
                image_original,
                image_tablet,
                image_phone,
                has_passive,
                passive_ability_id,
                value,
                timer,
                default_timer,
                reset_timer
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
            """,
            data_to_insert[existing_row_count:],
        )


async def upload_cards(file, db_pool):
    print("Inserting cards")

    data = file["Cards.Card"]
    print(len(data), data)

    # а здесь берем все столбцы, кроме первого (id) + так же пропускаем первую строку, там названия столбцов
    # вместо пустой строки в passive_ability_id ставим None для инзерта в бд
    needed_data = [row[1:22] for row in data[1:] if row]
    for element in needed_data:
        if element[15] == "":
            element[15] = None

    # добавляем туда измененные картинк
    data_to_insert = await update_images_in_place(needed_data, img_idx=10)
    print(len(data_to_insert), data_to_insert)

    async with db_pool.acquire() as connection:
        existing_row_count = await connection.fetchval("""select count(*) from cards""")
        print(existing_row_count, len(data_to_insert))

        if existing_row_count == len(data_to_insert):
            print("Nothing to insert in table cards")
            return

        for element in data_to_insert:
            print(len(element))

        await connection.executemany("""
            INSERT INTO cards
            (
                name,
                unlocked,
                faction_id,
                color_id,
                type_id,
                ability_id,
                damage,
                charges,
                hp,
                heal,
                image_original,
                image_tablet,
                image_phone,
                has_passive,
                has_passive_in_hand,
                has_passive_in_deck,
                has_passive_in_grave,
                passive_ability_id,
                value,
                timer,
                default_timer,
                reset_timer,
                each_tick
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23)
            """,
            data_to_insert[existing_row_count:],
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

    data = file["Enemies.EnemyLeader"]
    print(len(data), data)

    # а здесь берем все столбцы, кроме первого (id) + так же пропускаем первую строку, там названия столбцов
    # вместо пустой строки ставим None для инзерта в бд
    needed_data = [row[1:14] for row in data[1:] if row]
    for element in needed_data:
        if element[2] == "":
            element[2] = None
        if element[6] == "":
            element[6] = None

    # добавляем туда измененные картинк
    data_to_insert = await update_images_in_place(needed_data, img_idx=7)
    print(len(data_to_insert), data_to_insert)

    async with db_pool.acquire() as connection:
        existing_row_count = await connection.fetchval("""select count(*) from enemy_leaders""")
        print(existing_row_count, len(data_to_insert))

        if existing_row_count == len(data_to_insert):
            print("Nothing to insert in table leaders")
            return

        await connection.executemany("""
            INSERT INTO enemy_leaders
            (
                name,
                faction_id,
                ability_id,
                hp,
                base_hp,
                has_passive,
                passive_ability_id,
                image_original,
                image_tablet,
                image_phone,
                value,
                timer,
                default_timer,
                reset_timer,
                each_tick
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
            """,
            data_to_insert[existing_row_count:],
        )


async def upload_enemies(file, db_pool):
    print("Inserting enemies")

    data = file["Enemies.Enemy"]
    print(len(data), data)

    # а здесь берем все столбцы, кроме первого (id) + так же пропускаем первую строку, там названия столбцов
    # вместо пустой строки ставим None для инзерта в бд
    needed_data = [row[1:23] for row in data[1:] if row]
    for element in needed_data:
        if element[13] == "":
            element[13] = None
        if element[20] == "":
            element[20] = None

    # добавляем туда измененные картинк
    data_to_insert = await update_images_in_place(needed_data, img_idx=8)
    print(len(data_to_insert), data_to_insert)

    async with db_pool.acquire() as connection:
        existing_row_count = await connection.fetchval("""select count(*) from enemies""")
        print(existing_row_count, len(data_to_insert))

        if existing_row_count == len(data_to_insert):
            print("Nothing to insert in table leaders")
            return

        await connection.executemany("""
            INSERT INTO enemies
            (
                name,
                faction_id,
                color_id,
                move_id,
                damage,
                hp,
                base_hp,
                shield,
                image_original,
                image_tablet,
                image_phone,
                has_passive,
                has_passive_in_field,
                has_passive_in_deck,
                has_passive_in_grave,
                passive_ability_id,
                value,
                timer,
                default_timer,
                reset_timer,
                each_tick,
                has_deathwish,
                deathwish_id,
                deathwish_value
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24)
            """,
            data_to_insert[existing_row_count:],
        )


async def upload_seasons(file, db_pool):
    print("Inserting seasons")

    data = file["Enemies.Season"]

    # берем name, unlocked, description (столбцы 2,3,4) + так же пропускаем первую строку, там названия столбцов
    data_to_insert = [row[1:4] for row in data[1:] if row]

    async with db_pool.acquire() as connection:
        existing_row_count = await connection.fetchval("""select count(*) from seasons""")

        if existing_row_count == len(data_to_insert):
            print("Nothing to insert in table seasons")
            return

        await connection.executemany(
            """INSERT INTO seasons (name, unlocked, description) VALUES ($1, $2, $3)""",
            data_to_insert,
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
                data_to_insert,
            )


async def upload_from_excel():
    data = get_data("database.ods")

    db_pool = await db.connect()

    await upload_with_only_names(data, db_pool, page_name="Faction", table_name="factions")
    await upload_with_only_names(data, db_pool, page_name="Color", table_name="colors")
    await upload_with_only_names(data, db_pool, page_name="Type", table_name="types")

    await upload_with_names_and_descriptions(data, db_pool, page_name="Ability", table_name="abilities")
    await upload_with_names_and_descriptions(data, db_pool, page_name="CardPassiveAbility", table_name="passive_abilities")
    await upload_with_names_and_descriptions(data, db_pool, page_name="Move", table_name="moves")
    await upload_with_names_and_descriptions(data, db_pool, page_name="EnemyPassiveAbility", table_name="enemy_passive_abilities")
    await upload_with_names_and_descriptions(data, db_pool, page_name="EnemyLeaderAbility", table_name="enemy_leader_abilities")
    await upload_with_names_and_descriptions(data, db_pool, page_name="Deathwish", table_name="deathwishes")

    await upload_leaders(data, db_pool)
    await upload_cards(data, db_pool)
    await upload_base_deck(data, db_pool)
    await upload_enemy_leaders(data, db_pool)
    await upload_enemies(data, db_pool)
    await upload_seasons(data, db_pool)
    await upload_levels_enemies(data, db_pool)


if __name__ == "__main__":
    asyncio.run(upload_from_excel())
