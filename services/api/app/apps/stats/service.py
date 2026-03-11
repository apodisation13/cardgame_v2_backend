import logging

from lib.utils.db.pool import Database
from lib.utils.schemas.game import UserStatsRecordType
from services.api.app.apps.stats.schemas import GetStatsResponse, GameStats, CardsStats, LeadersStats, SeasonsStats, \
    LevelsStats
from services.api.app.config import Config
from services.api.app.exceptions import UserNotFoundError

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
                            THEN ROUND((COALESCE(win_stats.win_count, 0)::numeric / play_stats.play_count::numeric * 100), 1)
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

            print("STR72", stats)

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

            print(cards_stats, leaders_stats)

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

            print(seasons_stats, levels_stats)

        return GetStatsResponse(
            stats=stats,
            cards=cards_stats,
            leaders=leaders_stats,
            seasons=seasons_stats,
            levels=levels_stats,
        )
