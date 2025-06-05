import websockets
import asyncio
import os
import json
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
connected_clients = set()


async def handler(websocket, path):
    query = parse_qs(urlparse(path).query)
    key = query.get("api_key", [None])[0]

    if key != API_KEY:
        await websocket.send(json.dumps({"error": "unauthorized"}))
        await websocket.close()
        return
    connected_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        connected_clients.remove(websocket)


async def start_websocket_server():
    print("✅ WebSocket server listening on ws://0.0.0.0:8765")
    return await websockets.serve(handler, "0.0.0.0", 8765)
