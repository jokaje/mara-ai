from fastapi import WebSocket
from typing import Dict, Any


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.sessions: Dict[str, dict] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        await websocket.send_json({"type": "system", "content": f"Verbunden mit Session {session_id}"})

    def disconnect(self, session_id: str):
        self.active_connections.pop(session_id, None)

    async def send_personal_json(self, data: Dict[str, Any], session_id: str):
        websocket = self.active_connections.get(session_id)
        if not websocket:
            return
        try:
            await websocket.send_json(data)
        except Exception as e:
            print(f"❌ WebSocket send_json error {session_id}: {e}")
            self.disconnect(session_id)

    async def send_personal_message(self, message: str, session_id: str):
        websocket = self.active_connections.get(session_id)
        if not websocket:
            return
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"❌ WebSocket send_text error {session_id}: {e}")
            self.disconnect(session_id)


manager = ConnectionManager()
