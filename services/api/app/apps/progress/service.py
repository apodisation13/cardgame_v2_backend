from urllib.parse import urljoin

from lib.utils.db.pool import Database
from services.api.app.apps.cards.schemas import Card, Leader, Deck, Enemy, EnemyLeader
from services.api.app.apps.progress.schemas import UserProgressResponse, UserDatabase, UserCard, UserLeader, UserDeck, \
    UserResources
from services.api.app.config import Config


# def build_image_url(
#     base_url: str,
#     image_path: str,
# ) -> str:
#     return urljoin(base_url, f"media/{image_path}")



class UserProgressService:
    def __init__(
        self,
        db_pool: Database,
        config: Config,
    ):
        self.db_pool = db_pool
        self.config = config

    async def get_user_progress(
        self,
        user_id: int,
        base_url: str,
    ) -> UserProgressResponse:
        async with self.db_pool.connection() as connection:
            user_resources = await connection.fetchrow(
                """
                    SELECT scraps, kegs, big_kegs, chests, wood, keys
                    FROM user_resources 
                    WHERE id = $1
                """,
                user_id,
            )
            user_resources = UserResources(
                scraps=user_resources["scraps"],
                kegs=user_resources["kegs"],
                big_kegs=user_resources["big_kegs"],
                chests=user_resources["chests"],
                wood=user_resources["wood"],
                keys=user_resources["keys"],
            )

            game_constants = await connection.fetchval("""SELECT data::jsonb FROM game_constants""")
            print(type(game_constants), game_constants)

            enemies = await connection.fetch(
                """
                    SELECT
                        enemies.id,
                        enemies.name,
                        enemies.image_phone AS image,
                        factions.name AS faction_name,
                        colors.name AS color_name,
                        moves.name AS move_name,
                        moves.description AS move_description,
                        enemies.damage,
                        enemies.hp,
                        enemies.base_hp,
                        enemies.shield,
                        enemies.has_passive,
                        enemies.has_passive_in_field,
                        enemies.has_passive_in_grave,
                        enemies.has_passive_in_deck,
                        enemy_passive_abilities.name AS passive_ability_name,
                        enemy_passive_abilities.description AS passive_ability_description,
                        enemies.value,
                        enemies.timer,
                        enemies.default_timer,
                        enemies.reset_timer,
                        enemies.each_tick,
                        enemies.has_deathwish,
                        deathwishes.name AS deathwish_name,
                        deathwishes.description AS deathwish_description,
                        enemies.deathwish_value
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
                """,
            )
            enemies_model = [Enemy.get_one(row, base_url) for row in enemies]

            enemies_dict = {}
            for enemy in enemies_model:
                enemies_dict[enemy.id] = enemy

            enemy_leaders = await connection.fetch(
                """
                    SELECT
                        enemy_leaders.id,
                        enemy_leaders.name,
                        enemy_leaders.image_phone AS image,
                        factions.name AS faction_name,
                        enemy_leaders.hp,
                        enemy_leaders.base_hp,
                        enemy_leader_abilities.name AS ability_name,
                        enemy_leader_abilities.description AS ability_description,
                        enemy_leaders.has_passive,
                        enemy_passive_abilities.name AS passive_ability_name,
                        enemy_passive_abilities.description AS passive_ability_description,
                        enemy_leaders.value,
                        enemy_leaders.timer,
                        enemy_leaders.default_timer,
                        enemy_leaders.reset_timer,
                        enemy_leaders.each_tick
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
            enemy_leader_model = [EnemyLeader.get_one(row, base_url) for row in enemy_leaders]

            enemy_leaders_dict = {}
            for enemy_leader in enemy_leader_model:
                enemy_leaders_dict[enemy_leader.id] = enemy_leader

            seasons = await connection.fetch(
                """
                    SELECT
                        seasons.id,
                        seasons.name,
                        seasons.description,
                        seasons.unlocked,
                         
                        enemies.id,
                        enemies.name,
                        enemies.image_phone AS image,
                        factions.name AS faction_name,
                        colors.name AS color_name,
                        moves.name AS move_name,
                        moves.description AS move_description,
                        enemies.damage,
                        enemies.hp,
                        enemies.base_hp,
                        enemies.shield,
                        enemies.has_passive,
                        enemies.has_passive_in_field,
                        enemies.has_passive_in_grave,
                        enemies.has_passive_in_deck,
                        enemy_passive_abilities.name AS passive_ability_name,
                        enemy_passive_abilities.description AS passive_ability_description,
                        enemies.value,
                        enemies.timer,
                        enemies.default_timer,
                        enemies.reset_timer,
                        enemies.each_tick,
                        enemies.has_deathwish,
                        deathwishes.name AS deathwish_name,
                        deathwishes.description AS deathwish_description,
                        enemies.deathwish_value
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
                """,
            )
            enemies_model = [Enemy.get_one(row, base_url) for row in enemies]

            enemies_dict = {}
            for enemy in enemies_model:
                enemies_dict[enemy.id] = enemy



            user_cards: list[dict] = await connection.fetch(
                """
                    SELECT
                        cards.id,
                        cards.name,
                        cards.image_phone AS image,
                        cards.unlocked,
                        factions.name AS faction_name,
                        colors.name AS color_name,
                        types.name AS type_name,
                        abilities.name AS ability_name,
                        abilities.description AS ability_description,
                        cards.damage,
                        cards.charges,
                        cards.hp,
                        cards.heal,
                        cards.has_passive,
                        cards.has_passive_in_hand,
                        cards.has_passive_in_deck,
                        cards.has_passive_in_grave,
                        passive_abilities.name AS passive_ability_name,
                        passive_abilities.description AS passive_ability_description,
                        cards.value,
                        cards.timer,
                        cards.default_timer,
                        cards.reset_timer,
                        cards.each_tick,
                        COALESCE(user_cards.count, 0) AS user_card_count,
                        user_cards.id AS user_card_id
                    FROM
                        cards
                    LEFT JOIN
                        user_cards ON cards.id = user_cards.card_id AND user_cards.user_id = $1
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
                        cards.damage DESC,
                        cards.hp DESC,
                        cards.charges DESC
                """,
                user_id,
            )

            user_cards_model = [
                UserCard(
                    id=user_card["user_card_id"],
                    count=user_card["user_card_count"],
                    card=Card.get_one(user_card, base_url),
                )
                for user_card in user_cards
            ]

            users_card_dict = {}
            for card in user_cards_model:
                users_card_dict[card.card.id] = card.card

            print(149, users_card_dict)

            user_leaders: list[dict] = await connection.fetch(
                """
                    SELECT
                        leaders.id,
                        leaders.name,
                        leaders.image_phone AS image,
                        leaders.unlocked,
                        factions.name AS faction_name,
                        abilities.name AS ability_name,
                        abilities.description AS ability_description,
                        leaders.damage,
                        leaders.charges,
                        leaders.heal,
                        leaders.has_passive,
                        passive_abilities.name AS passive_ability_name,
                        passive_abilities.description AS passive_ability_description,
                        leaders.value,
                        leaders.timer,
                        leaders.default_timer,
                        leaders.reset_timer,
                        COALESCE(user_leaders.count, 0) AS user_leader_count,
                        user_leaders.id AS user_leader_id
                    FROM
                        leaders
                    LEFT JOIN
                        user_leaders ON leaders.id = user_leaders.leader_id AND user_leaders.user_id = $1
                    JOIN
                        factions ON leaders.faction_id = factions.id
                    JOIN
                        abilities ON leaders.ability_id = abilities.id
                    LEFT JOIN
                        passive_abilities ON leaders.passive_ability_id = passive_abilities.id
                """,
                user_id,
            )
            user_leaders_model = [
                UserLeader(
                    id=user_leader["user_leader_id"],
                    count=user_leader["user_leader_count"],
                    card=Leader.get_one(user_leader, base_url),
                )
                for user_leader in user_leaders
            ]

            users_leaders_dict = {}
            for leader in user_leaders_model:
                users_leaders_dict[leader.card.id] = leader.card

            print(199, users_leaders_dict)

            user_decks: list[dict] = await connection.fetch(
                """
                    select 
                        user_decks.id AS user_deck_id,
                        decks.id AS deck_id,
                        decks.name AS deck_name,
                        decks.leader_id AS leader_id,
                        card_decks.card_id AS card_id
                    from user_decks
                    join decks on user_decks.deck_id = decks.id
                    join card_decks on decks.id = card_decks.deck_id
                    where user_decks.user_id = $1;
                """,
                user_id,
            )

        user_decs_dict = {}

        for row in user_decks:
            user_deck_id = row["user_deck_id"]

            card_id: int = row["card_id"]
            card: Card = users_card_dict[card_id]
            hp = card.hp

            if user_deck_id not in user_decs_dict:
                deck_id: int = row["deck_id"]
                deck_name: str = row["deck_name"]
                leader_id: int = row["leader_id"]
                leader: Leader = users_leaders_dict[leader_id]

                user_decs_dict[user_deck_id] = UserDeck(
                    id=user_deck_id,
                    deck=Deck(
                        id=deck_id,
                        name=deck_name,
                        leader=leader,
                        health=hp,
                        cards=[card],
                    )
                )
            else:
                user_deck: UserDeck = user_decs_dict[user_deck_id]
                user_deck.deck.cards.append(card)
                user_deck.deck.health += hp

        user_decks_model = []
        for user_deck_id, user_deck in user_decs_dict.items():
            user_decks_model.append(user_deck)

        return UserProgressResponse(
            user_database=UserDatabase(
                cards=user_cards_model,
                leaders=user_leaders_model,
                decks=user_decks_model,
            ),
            resources=user_resources,
            seasons=[],
            game_const=game_constants,
            enemies=enemies_model,
            enemy_leaders=enemy_leader_model,
        )
