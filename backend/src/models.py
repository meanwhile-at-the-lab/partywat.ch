import random
from fastapi import WebSocket
import json
from utils import send_data

class User:
    def __init__(self, socket: WebSocket = None, alias: str = None, host_credential: str = None):
        self.socket = socket
        self.alias = alias or f"User_{random.randint(0, 99999999)}"
        self.host_credential = host_credential

    async def send_message(self, event: str, message: str):
        await send_data(self.socket, event, message)

    def __str__(self) -> str:
        return f"User(alias={self.alias}, HasSocket={self.socket is not None})"

    def __repr__(self) -> str:
        return self.__str__()

class VideoData:
    def __init__(self, id: str, timestamp: float, is_paused: bool = False):
        self.id = id
        self.timestamp = timestamp
        self.is_paused = is_paused

    def get_data(self) -> str:
        return f"VideoData(id={self.id}, timestamp={self.timestamp}, is_paused={self.is_paused})"

    def get_data_json(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "is_paused": self.is_paused
        }

    def __str__(self) -> str:
        return self.get_data()

    def __repr__(self) -> str:
        return self.get_data()

class Room:
    def __init__(self, host: User = None, id: int = None, video_data: VideoData = None, video_queue: list[str] = []):
        self.host = host
        self.users: set[User] = set()
        self.id = id
        self.video_data = video_data if video_data else VideoData(id="", timestamp=0, is_paused=True)
        self.video_queue: list[str] = video_queue

    def set_video(self, video_data: VideoData):
        self.video_data = video_data

    def next_in_queue(self):
        if len(self.video_queue) > 0:
            self.video_data = VideoData(self.video_queue.pop(0), 0, True)
            return True
        return False

    async def broadcast_message(self, event: str, message: str):
        for user in self.users:
            await user.send_message(event, message)

    async def broadcast_video_data(self):
        for user in self.users:
            await user.send_message("video-data", self.video_data.get_data_json())

    def get_data(self) -> str:
        return f"Room(users={self.users}, host={self.host if self.host else 'None'}{(', id='+str(self.id)) if self.id is not None else ''})"
    
    def get_unique_alias(self, alias: str) -> str:
        a = set([u.alias for u in self.users])
        a_alias = alias
        i = 0
        while a_alias in a:
            i += 1
            a_alias = alias + str(i)
        return a_alias

    def get_data_json(self) -> dict:
        return {
            "id": self.id,
            "host": self.host.alias,
            "users": [u.alias for u in self.users],
            "video_data": self.video_data.get_data_json(),
            "video_queue": self.video_queue,
        }
    
    def get_user(self, alias: str = None, socket: WebSocket = None):
        for u in self.users:
            if alias and u.alias == alias:
                return u
            if socket and u.socket == socket or (socket is u.socket):
                return u
        return None
 
    def alias_exists(self, alias: str) -> bool:
        return any(u.alias == alias for u in self.users)

    def __str__(self) -> str:
        return self.get_data()

    def __repr__(self) -> str:
        return self.get_data()

rooms: dict[int, Room] = {}