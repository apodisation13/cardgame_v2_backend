import asyncpg


async def get_game_constants(
    connection: asyncpg.Connection,
) -> dict | None:
    return await connection.fetchval("""SELECT data::jsonb FROM game_constants""")
