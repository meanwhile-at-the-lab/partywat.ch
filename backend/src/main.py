from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv
from routes import websocket_endpoint, create_room

load_dotenv(dotenv_path="../.env")

app = FastAPI()

print(os.getenv('FRONTEND_PORT'))

app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://localhost:{os.getenv('FRONTEND_PORT')}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_api_websocket_route("/ws", websocket_endpoint)
app.add_api_route("/api/create-room", create_room, methods=["POST"])

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    print(f"Running server at {host}:{port}")
    uvicorn.run(app, host=host, port=port)