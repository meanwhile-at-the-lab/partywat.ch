from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json

app = FastAPI()

rooms = {1234: {"name": "Room 1", "users": 0}, 5678: {"name": "Room 2", "users": 0}}


async def send_data(socket: WebSocket, event: str, message: str):
    await socket.send_text(json.dumps({"event": event, "message": message}))

async def handle_message(socket: WebSocket, data: dict):
    print(data)
    match data["event"]:
        case "message":
            await socket.send_text(data["message"])
        case "get-room":
            room_id = int(data["message"])
            if room_id not in rooms:
                await send_data(socket, "room-not-found", "Room not found")
            else:
                await send_data(socket, "room-data", json.dumps(rooms[room_id]))
        case "create-room":
            room_id = int(data["message"])
            rooms[room_id] = []
            await send_data(socket, "room-created", "Room created")
        case "join-room":
            room_id = int(data["message"])
            if room_id not in rooms:
                await send_data(socket, "room-not-found", "Room not found")
            else:
                rooms[room_id].append(socket)
                await send_data(socket, "room-joined", "Room joined")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            print("GOT MESSAGE", data)
            await handle_message(websocket, data)
    except WebSocketDisconnect:
        print("Client disconnected")
