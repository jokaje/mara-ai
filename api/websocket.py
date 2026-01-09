from fastapi import WebSocket
from typing import Dict
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        # Speichert aktive Sessions
        self.active_connections: Dict[str, WebSocket] = {}
        self.sessions: Dict[str, dict] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        
        await websocket.send_text(json.dumps({
            "type": "system",
            "content": f"Verbunden mit Session {session_id}"
        }))

    def disconnect(self, session_id: str):
        self.active_connections.pop(session_id, None)

    async def send_personal_message(self, message: str, session_id: str):
        """FIX: Einfache Version ohne WebSocketState"""
        websocket = self.active_connections.get(session_id)
        if websocket:
            try:
                await websocket.send_text(message)
                print(f"✅ Chunk gesendet an {session_id}")  # DEBUG
            except Exception as e:
                print(f"❌ WebSocket send error {session_id}: {e}")
                # Cleanup bei Fehler
                self.disconnect(session_id)

    async def broadcast(self, message: str):
        disconnected = []
        for session_id, connection in list(self.active_connections.items()):
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"WebSocket broadcast error {session_id}: {e}")
                disconnected.append(session_id)
        
        # Cleanup disconnected
        for session_id in disconnected:
            self.disconnect(session_id)

manager = ConnectionManager()
