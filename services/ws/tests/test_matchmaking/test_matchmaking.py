import time
from unittest.mock import patch

import pytest
from starlette.testclient import TestClient

from services.ws.app.apps.matchmaking.events import WSEvent

PLAYER_1_ID = 1
PLAYER_2_ID = 2

AUTH_PATCH = "services.ws.app.apps.matchmaking.routes.get_user_id_from_token"
SLEEP_PATCH = "services.ws.app.apps.matchmaking.routes.asyncio.sleep"


async def auth_by_token(token, config, db):
    """Заглушка авторизации: token1 -> player 1, token2 -> player 2, иначе None."""
    return {
        "token1": PLAYER_1_ID,
        "token2": PLAYER_2_ID,
    }.get(token)


class TestMatchmakingAuth:
    def test_invalid_token_sends_auth_error(self, client: TestClient):
        async def _invalid_auth(token, config, db):
            return None

        with patch(AUTH_PATCH, new=_invalid_auth):
            with client.websocket_connect("/ws/matchmaking?token=bad") as ws:
                msg = ws.receive_json()
                assert msg["event"] == WSEvent.AUTH_ERROR

    def test_missing_token_rejected(self, client: TestClient):
        # WebSocket-роут без обязательного token должен разорвать соединение
        with pytest.raises(Exception):
            with client.websocket_connect("/ws/matchmaking") as ws:
                ws.receive_json()


class TestMatchmakingFlow:
    def test_first_player_waits(self, client: TestClient):
        with patch(AUTH_PATCH, new=auth_by_token):
            with client.websocket_connect("/ws/matchmaking?token=token1") as ws:
                msg = ws.receive_json()
                assert msg["event"] == WSEvent.WAITING_FOR_OPPONENT

    def test_two_players_get_matched(self, client: TestClient):
        with patch(AUTH_PATCH, new=auth_by_token):
            with client.websocket_connect("/ws/matchmaking?token=token1") as ws1:
                msg = ws1.receive_json()
                assert msg["event"] == WSEvent.WAITING_FOR_OPPONENT

                with client.websocket_connect("/ws/matchmaking?token=token2") as ws2:
                    # Игрок 2 (гость) получает GAME_STARTED
                    msg2 = ws2.receive_json()
                    assert msg2["event"] == WSEvent.GAME_STARTED
                    assert msg2["role"] == "guest"
                    assert msg2["opponent_id"] == PLAYER_1_ID

                    # Игрок 1 (хост) тоже получает GAME_STARTED
                    msg1 = ws1.receive_json()
                    assert msg1["event"] == WSEvent.GAME_STARTED
                    assert msg1["role"] == "host"
                    assert msg1["opponent_id"] == PLAYER_2_ID

                    # У обоих одинаковый room_id
                    assert msg1["room_id"] == msg2["room_id"]

    def test_messages_relayed_between_players(self, client: TestClient):
        with patch(AUTH_PATCH, new=auth_by_token):
            with client.websocket_connect("/ws/matchmaking?token=token1") as ws1:
                ws1.receive_json()  # WAITING

                with client.websocket_connect("/ws/matchmaking?token=token2") as ws2:
                    ws2.receive_json()  # GAME_STARTED
                    ws1.receive_json()  # GAME_STARTED

                    # Игрок 1 шлёт сообщение — оно должно прийти игроку 2
                    ws1.send_text('{"action":"state_update","hp":90}')
                    received = ws2.receive_text()
                    assert received == '{"action":"state_update","hp":90}'

                    # И наоборот
                    ws2.send_text('{"action":"end_turn"}')
                    received = ws1.receive_text()
                    assert received == '{"action":"end_turn"}'


class TestMatchmakingDisconnect:
    def test_disconnect_notifies_opponent(self, client: TestClient):
        with patch(AUTH_PATCH, new=auth_by_token), patch(SLEEP_PATCH):
            with client.websocket_connect("/ws/matchmaking?token=token1") as ws1:
                ws1.receive_json()  # WAITING

                with client.websocket_connect("/ws/matchmaking?token=token2") as ws2:
                    ws2.receive_json()  # GAME_STARTED
                    ws1.receive_json()  # GAME_STARTED

                    # Игрок 2 выходит
                # ws2 закрылся

                # Игрок 1 должен получить OPPONENT_DISCONNECTED
                msg = ws1.receive_json()
                assert msg["event"] == WSEvent.OPPONENT_DISCONNECTED

    def test_waiting_player_disconnect_cleans_queue(self, client: TestClient):
        from services.ws.app.apps.matchmaking.manager import manager

        with patch(AUTH_PATCH, new=auth_by_token):
            with client.websocket_connect("/ws/matchmaking?token=token1") as ws:
                ws.receive_json()  # WAITING
                assert manager._waiting is not None

            # Даём серверу время обработать дисконнект (finally-блок асинхронный)
            time.sleep(0.1)
            assert manager._waiting is None
