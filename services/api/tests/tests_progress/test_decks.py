# class TestDecksAPI:
#     @pytest.mark.asyncio
#     async def test_create_user_deck(
#         self,
#         client: AsyncClient,
#         db_connection,
#         user_factory,
#     ) -> None:
#         user = await user_factory(
#             # email="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
#         )
#         print("STR35", type(user), user.id)
#
#         response = await client.post(
#             "/users/register-user",
#             json={
#                 "email": "email",
#                 "password": "password",
#                 "username": "username",
#             }
#         )
#
#         a = await db_connection.fetch("SELECT * FROM users")
#         print("STR40", a)
#         print(2)
#
#         response_json = response.json()
#         print("STR38", response_json)
#         assert response.status_code == 200
#
#         response = await client.post(
#             "/users/login-user",
#             json={
#                 "email": "email",
#                 "password": "password",
#             }
#         )
#
#         response_json = response.json()
#         print("STR38", response_json)
#         assert response.status_code == 200
#
#         token = response_json["token"]["access_token"]
#         print(58, token)
#
#         response = await client.get(
#             "/user-progress/1",
#             headers={"Authorization": f"Bearer {token}"},
#         )
#         response_json = response.json()
#         print("STR38", response_json)
