from typing import List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"WS connected: {len(self.active_connections)} clients")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"WS disconnected: {len(self.active_connections)} clients")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Failed to send WS message: {e}")


manager = ConnectionManager()
