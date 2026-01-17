import pytest


@pytest.mark.asyncio
async def test_create_user(db_connection, db_pool):
    print(type(db_connection), type(db_pool))

    await db_connection.execute(
        """
            insert into users
            (username, password, email)
            values ('1', '1', '1')
        """,
    )
    await db_connection.execute(
        """
            insert into users
            (username, password, email)
            values ('2', '2', '2')
        """,
    )

    result = await db_connection.fetchrow("SELECT * FROM users")
    print(11, result)
#
#
# @pytest.mark.asyncio
# async def test_create_user_2(db_connection, db_pool):
#     print(type(db_connection), type(db_pool))
#     result = await db_connection.fetchrow("SELECT * FROM users")
#     print(32, result)
