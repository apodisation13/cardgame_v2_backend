import logging

from lib.utils.db.pool import Database
from lib.utils.schemas.game import UserStatsRecordType
from services.api.app.apps.stats.schemas import (
    CardsStats,
    GameStats,
    GetStatsResponse,
    LeadersStats,
    LevelsStats,
    SeasonsStats, GetLeaderboardResponse, PostLeaderboardRequest,
)
from services.api.app.config import Config
from services.api.app.exceptions import UserNotFoundError
from services.api.app.exceptions.exceptions import PostStatsError


logger = logging.getLogger(__name__)


class StatsService:
    def __init__(
        self,
        db_pool: Database,
        config: Config,
    ):
        self.db_pool = db_pool
        self.config = config

    async def get_user_stats(
        self,
        user_id: int,
        for_user: int | None,
    ) -> GetStatsResponse:
        if for_user is not None:
            async with self.db_pool.connection() as connection:
                user_id: int | None = await connection.fetchval(
                    """
                    SELECT
                        id
                    FROM
                        users
                    WHERE
                        id = $1
                    """,
                    for_user,
                )

            if not user_id:
                raise UserNotFoundError()

        logger.info("Getting database for user %s", user_id)
        async with self.db_pool.connection() as connection:
            stats: dict[str, GameStats] = await connection.fetchval(
                """
                SELECT
                    jsonb_object_agg(
                        faction_name,
                        jsonb_build_object(
                            'play', play,
                            'win', win,
                            'winrate', winrate
                        )
                    ) AS stats
                FROM (
                    SELECT
                        factions.name as faction_name,
                        COALESCE(play_stats.play_count, 0) AS play,
                        COALESCE(win_stats.win_count, 0) AS win,
                        CASE
                            WHEN COALESCE(play_stats.play_count, 0) > 0
                            THEN ROUND(
                                (COALESCE(win_stats.win_count, 0)::numeric / play_stats.play_count::numeric * 100),
                                 1
                                )
                            ELSE 0
                        END AS winrate
                    FROM factions
                    LEFT JOIN (
                        SELECT faction_id, count as play_count
                        FROM user_stats
                        WHERE user_id = $1 AND type = $3
                    ) play_stats ON factions.id = play_stats.faction_id
                    LEFT JOIN (
                        SELECT faction_id, count as win_count
                        FROM user_stats
                        WHERE user_id = $1 AND type = $4
                    ) win_stats ON factions.id = win_stats.faction_id
                    WHERE factions.id IN (
                        SELECT DISTINCT id
                        FROM factions
                        WHERE factions.name != $2
                    )
                ) subquery;
                """,
                user_id,
                "Neutral",
                UserStatsRecordType.PLAY,
                UserStatsRecordType.WIN,
            )

            cards_stats: CardsStats = await connection.fetchval(
                """
                SELECT
                    jsonb_build_object(
                        'total', total.count,
                        'open', COALESCE(open.count, 0)
                    ) AS result
                FROM
                    (SELECT COUNT(*) AS count FROM cards) total
                CROSS JOIN
                    (SELECT COUNT(*) AS count FROM user_cards WHERE user_id = $1) open;
                """,
                user_id,
            )

            leaders_stats: LeadersStats = await connection.fetchval(
                """
                SELECT
                    jsonb_build_object(
                        'total', total.count,
                        'open', COALESCE(open.count, 0)
                    ) AS result
                FROM
                    (SELECT COUNT(*) AS count FROM leaders) total
                CROSS JOIN
                    (SELECT COUNT(*) AS count FROM user_leaders WHERE user_id = $1) open;
                """,
                user_id,
            )

            seasons_stats: SeasonsStats = await connection.fetchval(
                """
                SELECT
                    jsonb_build_object(
                        'total', total.count,
                        'finished', COALESCE(finished.count, 0)
                    ) AS result
                FROM
                    (SELECT COUNT(*) AS count FROM seasons) total
                CROSS JOIN
                    (
                        SELECT COUNT(*) AS count
                        FROM user_seasons
                        WHERE user_id = $1
                        AND finished IS TRUE
                    ) finished;
                """,
                user_id,
            )

            levels_stats: LevelsStats = await connection.fetchval(
                """
                SELECT
                    jsonb_build_object(
                        'total', total.count,
                        'finished', COALESCE(finished.count, 0)
                    ) AS result
                FROM
                    (SELECT COUNT(*) AS count FROM levels) total
                CROSS JOIN
                    (
                        SELECT COUNT(*) AS count
                        FROM user_levels
                        WHERE user_id = $1
                        AND finished IS TRUE
                    ) finished;
                """,
                user_id,
            )

        return GetStatsResponse(
            stats=stats,
            cards=cards_stats,
            leaders=leaders_stats,
            seasons=seasons_stats,
            levels=levels_stats,
        )

    async def post_user_stats(
        self,
        user_id: int,
        user_deck_id: int,
        game_type: UserStatsRecordType,
    ) -> dict:
        async with self.db_pool.connection() as connection:
            leader_faction_id: int | None = await connection.fetchval(
                """
                SELECT
                    leaders.faction_id
                FROM
                    user_decks
                JOIN decks ON decks.id = user_decks.deck_id
                JOIN leaders ON decks.leader_id = leaders.id
                WHERE
                    user_decks.id = $1
                    AND user_decks.user_id = $2;
                """,
                user_deck_id,
                user_id,
            )

            if not leader_faction_id:
                msg = "Can not find such user_deck (%s) for user %s"
                logger.warning(msg, user_deck_id, user_id)
                raise PostStatsError(msg % (user_deck_id, user_id))

            await connection.fetchrow(
                """
                    INSERT INTO user_stats
                    (user_id, faction_id, count, type)
                    VALUES ($1, $2, 1, $3)
                    ON CONFLICT (user_id, faction_id, type)
                    DO UPDATE
                    SET
                        count = user_stats.count + 1,
                        updated_at = NOW()
                """,
                user_id,
                leader_faction_id,
                game_type,
            )

        return {"200": "OK"}

    async def get_user_leaderboard(
        self,
        user_id: int,
    ) -> list[GetLeaderboardResponse]:
        async with self.db_pool.connection() as connection:
            leaderboards: list[dict] = await connection.fetch(
                """
                SELECT
                    users.username,
                    user_preferences.data ->> 'avatar' AS user_avatar,
                    leaders.id AS leader_id,
                    factions.name AS faction_name,
                    leaderboard.max_kills AS max_kills,
                    leaderboard.mode AS mode
                FROM
                    users
                JOIN leaderboard ON users.id = leaderboard.user_id
                JOIN leaders ON leaderboard.leader_id = leaders.id
                JOIN factions ON leaders.faction_id = factions.id
                LEFT JOIN user_preferences ON users.id = user_preferences.id
                WHERE 
                    users.id = $1
                ORDER BY 
                    leaderboard.max_kills DESC, 
                    leaderboard.updated_at DESC
                """,
                user_id,
            )

        if not leaderboards:
            return []

        leaderboards_response = []
        for row in leaderboards:
            leaderboards_response.append(
                GetLeaderboardResponse(
                    username=row["username"],
                    user_avatar=row["user_avatar"],
                    leader_id=row["leader_id"],
                    faction_name=row["faction_name"],
                    max_kills=row["max_kills"],
                    mode=row["mode"],
                )
            )

        return leaderboards_response

    async def post_user_leaderboard(
        self,
        user_id: int,
        post_leaderboard_request: PostLeaderboardRequest,
    ) -> dict:
        user_deck_id = post_leaderboard_request.user_deck_id
        mode = post_leaderboard_request.mode
        max_kills = post_leaderboard_request.max_kills

        async with self.db_pool.connection() as connection:
            leader_id: int | None = await connection.fetchval(
                """
                SELECT
                    leaders.id
                FROM
                    user_decks
                JOIN decks ON decks.id = user_decks.deck_id
                JOIN leaders ON decks.leader_id = leaders.id
                WHERE
                    user_decks.id = $1
                    AND user_decks.user_id = $2;
                """,
                user_deck_id,
                user_id,
            )

            if not leader_id:
                msg = "Can not find such user_deck (%s) for user %s"
                logger.warning(msg, user_deck_id, user_id)
                raise PostStatsError(msg % (user_deck_id, user_id))

            await connection.fetchrow(
                """
                    INSERT INTO leaderboard
                    (user_id, leader_id, max_kills, mode)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (user_id, leader_id, mode)
                    DO UPDATE
                    SET
                        max_kills = EXCLUDED.max_kills,
                        updated_at = NOW()
                    WHERE 
                        leaderboard.max_kills < EXCLUDED.max_kills
                """,
                user_id,
                leader_id,
                max_kills,
                mode,
            )

        return {"200": "OK"}
