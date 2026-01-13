import asyncpg

from lib.utils.db.pool import Database
from services.api.app.apps.cards.schemas import Card
from services.api.app.apps.progress.logic import process_enemies, process_cards
from services.api.app.apps.progress.schemas import (
    UserDatabase,
    UserProgressResponse,
    UserResources, CreateDeckRequest, ListDecksResponse,
)
from services.api.app.config import Config


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
            user_resources = await self._get_user_resources(
                connection=connection,
                user_id=user_id,
            )

            game_constants = await self._get_game_constants(
                connection=connection,
            )

            enemies, enemy_leaders, seasons = await process_enemies(
                connection=connection,
                user_id=user_id,
                base_url=base_url,
            )

            user_cards, user_leaders, user_decks = await process_cards(
                connection=connection,
                user_id=user_id,
                base_url=base_url,
            )

        return UserProgressResponse(
            user_database=UserDatabase(
                cards=user_cards,
                leaders=user_leaders,
                decks=user_decks,
            ),
            resources=user_resources,
            seasons=seasons,
            game_const=game_constants,
            enemies=enemies,
            enemy_leaders=enemy_leaders,
        )

    async def _get_user_resources(
        self,
        user_id: int,
        connection: asyncpg.Connection,
    ) -> UserResources:
        user_resources = await connection.fetchrow(
            """
                SELECT scraps, kegs, big_kegs, chests, wood, keys
                FROM user_resources
                WHERE id = $1
            """,
            user_id,
        )
        return UserResources(
            scraps=user_resources["scraps"],
            kegs=user_resources["kegs"],
            big_kegs=user_resources["big_kegs"],
            chests=user_resources["chests"],
            wood=user_resources["wood"],
            keys=user_resources["keys"],
        )

    async def _get_game_constants(
        self,
        connection: asyncpg.Connection,
    ) -> dict:
        game_constants = await connection.fetchval("""SELECT data::jsonb FROM game_constants""")
        print(type(game_constants), game_constants)
        return game_constants

    async def create_user_deck(
        self,
        user_id: int,
        deck: CreateDeckRequest,
        base_url: str,
    ) -> ListDecksResponse:
        async with self.db_pool.transaction() as connection:
            deck_id = await connection.fetchval(
                """
                    INSERT INTO decks
                    (name, leader_id)
                    VALUES ($1, $2)
                    RETURNING id
                """,
                deck.deck_name,
                deck.leader_id,
            )
            print("STR110", deck_id)

            card_decks: list[tuple[deck_id, Card.id]] = [(deck_id, card_id) for card_id in deck.cards]
            print("STR111", card_decks)

            await connection.executemany(
                """
                INSERT INTO card_decks
                (deck_id, card_id)
                VALUES ($1, $2)
                """,
                card_decks,
            )

            await connection.execute(
                """
                INSERT INTO user_decks
                (user_id, deck_id)
                VALUES ($1, $2)
                """,
                user_id,
                deck_id,
            )

            _, _, user_decks = await process_cards(
                connection=connection,
                user_id=user_id,
                base_url=base_url,
            )
            print("STR121", len(user_decks))

        return ListDecksResponse(
            decks=user_decks,
        )

    async def delete_user_deck(
        self,
        user_id: int,
        deck_id: int,
        base_url: str,
    ) -> ListDecksResponse:
        async with self.db_pool.transaction() as connection:
            await connection.execute(
                """
                DELETE FROM user_decks
                WHERE 
                    user_decks.user_id = $1
                    AND user_decks.deck_id = $2
                """,
                user_id,
                deck_id,
            )
            await connection.execute(
                """
                DELETE FROM card_decks
                WHERE 
                    card_decks.deck_id = $1
                """,
                deck_id,
            )
            await connection.execute(
                """
                DELETE FROM decks
                WHERE 
                    decks.id = $1
                """,
                deck_id,
            )
            _, _, user_decks = await process_cards(
                connection=connection,
                user_id=user_id,
                base_url=base_url,
            )
            print("STR183", len(user_decks))

        return ListDecksResponse(
            decks=user_decks,
        )

    async def patch_user_deck(
        self,
        user_id: int,
        deck_id: int,
        deck: CreateDeckRequest,
        base_url: str,
    ) -> ListDecksResponse:
        async with self.db_pool.transaction() as connection:
            await connection.fetchrow(
                """
                    UPDATE decks
                    SET 
                        name = $2, 
                        leader_id = $3
                    WHERE
                        decks.id = $1
                """,
                deck_id,
                deck.deck_name,
                deck.leader_id,
            )

            await connection.execute(
                """
                    DELETE FROM card_decks
                    WHERE card_decks.deck_id = $1
                """,
                deck_id,
            )

            card_decks: list[tuple[deck_id, Card.id]] = [(deck_id, card_id) for card_id in deck.cards]
            print("STR220", card_decks)
            await connection.executemany(
                """
                INSERT INTO card_decks
                (deck_id, card_id)
                VALUES ($1, $2)
                """,
                card_decks,
            )

            _, _, user_decks = await process_cards(
                connection=connection,
                user_id=user_id,
                base_url=base_url,
            )
            print("STR235", len(user_decks))

        return ListDecksResponse(
            decks=user_decks,
        )
