import asyncio
import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from services.ws.app.apps.matchmaking.events import WSEvent
from services.ws.app.apps.matchmaking.manager import Player, manager
from services.ws.app.auth import get_user_id_from_token


router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/matchmaking")
async def matchmaking_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
):
    """
    Эндпоинт для мэтчмейкинга.

    Фронт подключается: ws://server/ws/matchmaking?token=<jwt_token>

    Возможные события от сервера к клиенту:
      - AUTH_ERROR: токен невалидный, соединение закрывается
      - WAITING_FOR_OPPONENT: игрок добавлен в очередь, ждём второго
      - GAME_STARTED: нашли пару, игра начинается
          { event, room_id, role ("host"/"guest"), opponent_id }
      - OPPONENT_DISCONNECTED: противник вышел из игры

    После GAME_STARTED оба соединения работают как relay:
    любое сообщение от одного игрока автоматически пересылается другому.
    """
    config = websocket.app.state.config
    db = websocket.app.state.db

    await websocket.accept()

    user_id = await get_user_id_from_token(token, config, db)
    if user_id is None:
        await websocket.send_json({"event": WSEvent.AUTH_ERROR, "detail": "Invalid or expired token"})
        await websocket.close(code=4001)
        return

    logger.info("Player %s connected to matchmaking", user_id)

    player = Player(user_id=user_id, ws=websocket)
    room = manager.try_match(player)

    if room is None:
        # Первый игрок — ждём второго
        await websocket.send_json({"event": WSEvent.WAITING_FOR_OPPONENT})
    else:
        # Нашли пару — уведомляем обоих
        await room.host.ws.send_json({
            "event": WSEvent.GAME_STARTED,
            "room_id": room.room_id,
            "role": "host",
            "opponent_id": room.guest.user_id,
        })
        await websocket.send_json({
            "event": WSEvent.GAME_STARTED,
            "room_id": room.room_id,
            "role": "guest",
            "opponent_id": room.host.user_id,
        })

    # Основной цикл: получаем сообщения и пересылаем противнику.
    # Пока игрок в ожидании (нет комнаты) — сообщения игнорируются.
    # Как только создалась комната — сообщения начинают форвардиться.
    try:
        while True:
            data = await websocket.receive_text()
            current_room = manager.get_room_for_player(user_id)
            if current_room:
                opponent = current_room.get_opponent(user_id)
                try:
                    await opponent.ws.send_text(data)
                except Exception:
                    logger.warning("Failed to send message to player %s", opponent.user_id)
    except WebSocketDisconnect:
        logger.info("Player %s disconnected", user_id)
    finally:
        # Уведомляем противника и чистим комнату
        current_room = manager.get_room_for_player(user_id)
        if current_room:
            opponent = current_room.get_opponent(user_id)
            manager.remove_room(current_room.room_id)
            try:
                await opponent.ws.send_json({"event": WSEvent.OPPONENT_DISCONNECTED})
                await asyncio.sleep(10)
                await opponent.ws.close(code=1000)
            except Exception:
                pass
        else:
            manager.remove_waiting(user_id)
