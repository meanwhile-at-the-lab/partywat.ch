from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
from fastapi import Request
import uvicorn
import os
from dotenv import load_dotenv
import random

load_dotenv()

app = FastAPI()

print(os.getenv('FRONTEND_PORT'))

app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://localhost:{os.getenv('FRONTEND_PORT')}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class User:
    def __init__(self, socket: WebSocket = None, alias: str = None):
        self.socket = socket
        self.alias = alias or f"User_{random.randint(0, 99999999)}"

    async def send_message(self, event: str, message: str):
        await send_data(self.socket, event, message)

    def __str__(self) -> str:
        return f"User(alias={self.alias})"
    def __repr__(self) -> str:
        return self.__str__()
    
class Room:
    def __init__(self, host: User = None, id: int = None):
        self.host = host
        self.users: set[User] = set()
        self.id = id

    async def broadcast_message(self, event: str, message: str):
        for user in self.users:
            await user.send_message(event, message)

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
            "users": [u.alias for u in self.users]
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

async def send_data(socket: WebSocket, event: str, message: str):
    await socket.send_text(json.dumps({"event": event, "message": message}))

def get_new_room_id() -> int:
    id = random.randint(0, 100000)
    while id in rooms:
        id = random.randint(0, 100000)
    return id

async def handle_message(socket: WebSocket, data: dict):
    event = data.get("event")
    message = data.get("message")
    print("Received", event, message)
    if event == "message":
        await socket.send_text(message)
    elif event == "disconnect":
        # HACK: Quick and dirty way to log disconnections w/ aliases
        print("Disconnecting", socket)
        for room_id in rooms:
            print(f"Checking room {room_id}")
            room = rooms[room_id]
            user = room.get_user(socket=socket)
            if user:
                print(f"User: {user.alias} disconnected")
    elif event == "get-room":
        room_id = int(message)
        if room_id not in rooms:
            await send_data(socket, "room-not-found", "Room not found")
        else:
            await send_data(socket, "room-data", json.dumps(rooms[room_id].get_data_json()))
    elif event == "join-room":
        message = json.loads(message)
        print(message)
        room_id = int(message["id"])
        alias = message["alias"]
        if room_id not in rooms:
            await send_data(socket, "room-not-found", "Room not found")
        else:
            room = rooms[room_id]
            if message["type"] == "host":
                if room.host.alias != alias or len(room.users) != 0:
                    await send_data(socket, "not-host", "You are not the host")
                    return
                else:
                    u = User(alias=alias, socket=socket)
                    room.host = u
                    room.users.add(u)
            elif message["type"] == "guest":
                alias = room.get_unique_alias(alias)
            user = room.get_user(alias=alias)
            if user:
                user.socket = socket
            else:
                user = User(alias=alias, socket=socket)
                room.users.add(user)
            await send_data(socket, "room-joined", json.dumps({"alias": alias, "room": room.get_data_json(), "isHost": room.host.alias == alias}))
            await room.broadcast_message("user-joined", alias)
    elif event == "leave-room":
        message = json.loads(message)
        room_id = int(message["id"])
        print("leave-room", room_id)
        if room_id not in rooms:
            await send_data(socket, "room-not-found", "Room not found")
        else:
            user = rooms[room_id].get_user(socket=socket)
            if not user:
                await send_data(socket, "not-in-room", "Not in room")
            else:
                rooms[room_id].users.remove(user)
                await rooms[room_id].broadcast_message("user-left", user.alias)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            await handle_message(websocket, data)
    except WebSocketDisconnect:
        await handle_message(websocket, {"event": "disconnect", "message": ""})
        pass

@app.post("/api/create-room")
async def create_room(request: Request):
    data = await request.json()
    alias = data.get("alias")
    if not alias:
        raise HTTPException(status_code=400, detail="Alias is required")
    user = User(alias=alias)
    id = get_new_room_id()
    room = Room(host=user, id=id)
    rooms[id] = room
    return {"message": json.dumps(room.get_data_json())}


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    print(f"Running server at {host}:{port}")
    uvicorn.run(app, host=host, port=port)
