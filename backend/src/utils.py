import random
from fastapi import WebSocket
import json
import time
import string

async def send_error(socket: WebSocket, message: dict):
    # print error
    print(f"Error: {message}")
    await send_data(socket, "error", message)

async def send_data(socket: WebSocket, event: str, message: dict):
    log(f"Sending {event} to {socket}")
    await socket.send_json({"event": event, "message": message})

def log(message: str):
    open("out.log", "a").write(f"{time.ctime()}: {message}\n")  

def generate_host_credential(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
