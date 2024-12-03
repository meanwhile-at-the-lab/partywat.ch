from fastapi import WebSocket, WebSocketDisconnect, HTTPException, Request
import json
from models import User, Room, rooms
import random
from utils import send_data, send_error, log, generate_host_credential

async def handle_message_event(socket: WebSocket, message: str):
    await socket.send_json({"event": "message", "message":message})

async def handle_video_paused_event(socket: WebSocket, message: str):
    msg = json.loads(message)
    room_id = int(msg["id"])
    is_paused = msg["is_paused"]
    host_credential = msg.get("hostCredential")
    room = rooms[room_id]
    user = room.get_user(socket=socket)
    if room.host.alias != user.alias or room.host_credential != host_credential:
        await send_data(socket, "not-host", "You are not the host")
        return
    room.video_data.is_paused = is_paused
    await room.broadcast_video_data()

async def handle_video_seek_event(socket: WebSocket, message: str):
    msg = json.loads(message)
    room_id = int(msg["id"])
    timestamp = msg["timestamp"]
    host_credential = msg.get("hostCredential")
    room = rooms[room_id]
    user = room.get_user(socket=socket)
    if room.host.alias != user.alias or room.host_credential != host_credential:
        await send_data(socket, "not-host", "You are not the host")
        return
    room.video_data.timestamp = timestamp
    await room.broadcast_video_data()

async def handle_disconnect_event(socket: WebSocket, message: str):
    print("Disconnecting", socket)
    for room_id, room in rooms.items():
        print(f"Checking room {room_id}")
        user = room.get_user(socket=socket)
        if user:
            print(f"User: {user.alias} disconnected")
            room.users.remove(user)
            await room.broadcast_message("user-left", user.alias)

async def handle_get_room_event(socket: WebSocket, message: str):
    room_id = int(message)
    if room_id not in rooms:
        await send_data(socket, "room-not-found", "Room not found")
    else:
        room_data = rooms[room_id].get_data_json()
        await send_data(socket, "room-data", room_data)

async def handle_join_room_event(socket: WebSocket, message: str):
    message = json.loads(message)
    print(message)
    room_id = int(message["id"])
    alias = message["alias"]
    host_credential = message.get("hostCredential")
    if room_id not in rooms:
        await send_data(socket, "room-not-found", "Room not found")
        return
    room = rooms[room_id]
    user_type = message.get("type")
    log(f"Joining room {room_id} as {user_type} {alias}")
    if user_type == "host":
        if room.host and (room.host.alias != alias or room.host_credential != host_credential):
            await send_data(socket, "not-host", "Invalid host credentials")
            return
        user = User(alias=alias, socket=socket)
        room.host = user
        room.users.add(user)
    elif user_type == "guest":
        alias = room.get_unique_alias(alias)
        user = room.get_user(alias=alias)
        if user:
            user.socket = socket
        else:
            user = User(alias=alias, socket=socket)
            room.users.add(user)
    else:
        await send_data(socket, "invalid-type", "Invalid user type")
        return

    is_host = room.host.alias == alias
    response = {
        "alias": alias,
        "room": room.get_data_json(),
        "isHost": is_host
    }
    if is_host:
        response["hostCredential"] = room.host_credential
    await send_data(socket, "room-joined", response)
    await room.broadcast_message("user-joined", alias)

async def handle_leave_room_event(socket: WebSocket, message: str):
    message = json.loads(message)
    room_id = int(message["id"])
    print("leave-room", room_id)
    if room_id not in rooms:
        await send_data(socket, "room-not-found", "Room not found")
        return

    room = rooms[room_id]
    user = room.get_user(socket=socket)
    if not user:
        await send_data(socket, "not-in-room", "Not in room")
        return

    room.users.remove(user)
    await room.broadcast_message("user-left", user.alias)

EVENT_HANDLERS = {
    "message": handle_message_event,
    "video-paused": handle_video_paused_event,
    "video-seek": handle_video_seek_event,
    "disconnect": handle_disconnect_event,
    "get-room": handle_get_room_event,
    "join-room": handle_join_room_event,
    "leave-room": handle_leave_room_event,
}

async def handle_message(socket: WebSocket, data: dict):
    event = data.get("event")
    message = data.get("message")
    print("Received", event, message)

    handler = EVENT_HANDLERS.get(event)
    if handler:
        await handler(socket, message)
    else:
        await send_error(socket, f"Invalid event {event}")

async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            await handle_message(websocket, data)
    except WebSocketDisconnect:
        await handle_message(websocket, {"event": "disconnect", "message": ""})

def get_new_room_id():
    id = 0
    while id in rooms:
        id = random.randint(1000, 9999)
    return id

async def create_room(request: Request):
    data = await request.json()
    alias = data.get("alias")
    if not alias:
        raise HTTPException(status_code=400, detail="Alias is required")
    user = User(alias=alias)
    id = get_new_room_id()
    room = Room(host=user, id=id)
    rooms[id] = room
    host_credential = generate_host_credential()
    room.host_credential = host_credential
    return {"message": room.get_data_json(), "hostCredential": host_credential}
