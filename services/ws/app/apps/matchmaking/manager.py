from dataclasses import dataclass
import logging
import uuid

from fastapi import WebSocket


logger = logging.getLogger(__name__)


@dataclass
class Player:
    user_id: int
    ws: WebSocket


@dataclass
class Room:
    room_id: str
    host: Player
    guest: Player

    def get_opponent(self, user_id: int) -> Player:
        return self.guest if self.host.user_id == user_id else self.host


class MatchmakingManager:
    def __init__(self):
        self._waiting: Player | None = None
        self._rooms: dict[str, Room] = {}
        self._player_rooms: dict[int, str] = {}  # user_id -> room_id

    def try_match(self, player: Player) -> Room | None:
        """
        Если уже кто-то ждёт — создаём комнату и возвращаем её.
        Если очередь пустая — добавляем игрока в ожидание и возвращаем None.
        """
        if self._waiting is None:
            self._waiting = player
            return None

        host = self._waiting
        self._waiting = None

        room_id = uuid.uuid4().hex[:8]
        room = Room(room_id=room_id, host=host, guest=player)
        self._rooms[room_id] = room
        self._player_rooms[host.user_id] = room_id
        self._player_rooms[player.user_id] = room_id

        logger.info("Room %s created: player %s (host) vs player %s (guest)", room_id, host.user_id, player.user_id)
        return room

    def get_room_for_player(self, user_id: int) -> Room | None:
        room_id = self._player_rooms.get(user_id)
        return self._rooms.get(room_id) if room_id else None

    def remove_room(self, room_id: str) -> None:
        room = self._rooms.pop(room_id, None)
        if room:
            self._player_rooms.pop(room.host.user_id, None)
            self._player_rooms.pop(room.guest.user_id, None)
            logger.info("Room %s removed", room_id)

    def remove_waiting(self, user_id: int) -> None:
        if self._waiting and self._waiting.user_id == user_id:
            self._waiting = None
            logger.info("Player %s removed from waiting queue", user_id)


manager = MatchmakingManager()
