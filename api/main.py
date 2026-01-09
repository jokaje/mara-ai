from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json
import uuid
from typing import Dict
import traceback
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Absolute Imports
from api.models import ChatRequest, ChatResponse, RecallRequest, MemoryItem
from api.websocket import manager
import mara

app = FastAPI(title="Mara AI API", version="1.0.0")

# Thread Pool für Sync-Operationen
executor = ThreadPoolExecutor(max_workers=4)

# Session-Management
sessions: Dict[str, dict] = {}

@app.get("/")
async def get():
    return {"message": "Mara AI API ist bereit", "docs": "/docs"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Text-Chat mit Mara"""
    try:
        print(f"Chat-Request erhalten: {request.message}")
        if request.session_id not in sessions:
            print(f"Erstelle neue Session: {request.session_id}")
            sessions[request.session_id] = mara.create_mara_session()
        
        session = sessions[request.session_id]
        print("Session gefunden, starte Chat...")
        result = mara.chat_with_mara_session(session, request.message)
        print(f"Chat-Ergebnis: {result['response'][:50]}...")
        
        return ChatResponse(**result)
    except Exception as e:
        print(f"Fehler im Chat: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recall")
async def recall_endpoint(request: RecallRequest):
    """Erinnerungen suchen"""
    try:
        if request.session_id not in sessions:
            sessions[request.session_id] = mara.create_mara_session()
        
        session = sessions[request.session_id]
        long_term = session['long_term']
        
        memories = long_term.search_memories(request.query, n_results=request.limit)
        return [MemoryItem(**mem) for mem in memories]
    except Exception as e:
        print(f"Fehler im Recall: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions")
async def list_sessions():
    """Aktive Sessions auflisten"""
    return {"sessions": list(sessions.keys())}

@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """Session löschen"""
    if session_id in sessions:
        del sessions[session_id]
    return {"message": f"Session {session_id} gelöscht"}

# WebSocket Endpoint für Echtzeit-Chat mit FLUSH
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    print(f"WebSocket-Verbindung von Session {session_id}")
    await manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Nachricht erhalten: {data}")
            try:
                message_data = json.loads(data)
                user_message = message_data.get("message", "")
                print(f"User-Nachricht: {user_message}")
                
                if session_id not in sessions:
                    print(f"Erstelle neue Session für WebSocket: {session_id}")
                    sessions[session_id] = mara.create_mara_session()
                
                session = sessions[session_id]
                print("Session gefunden, starte ASYNC Streaming-Chat...")
                
                # Stream-Start
                await manager.send_personal_message(
                    json.dumps({"type": "stream_start"}),
                    session_id
                )
                
                # ASYNC STREAMING MIT FLUSH!
                chunk_count = 0
                async for chunk in mara.mara_async_stream(session, user_message):
                    if chunk:
                        chunk_count += 1
                        chunk_json = json.dumps({
                            "type": "stream_chunk",
                            "content": chunk
                        })
                        await manager.send_personal_message(chunk_json, session_id)
                        await asyncio.sleep(0.001)  # FLUSH!
                
                print(f"🎉 {chunk_count} Chunks gestreamt!")
                
                # Stream-End
                await manager.send_personal_message(
                    json.dumps({"type": "stream_end"}),
                    session_id
                )
                
            except Exception as e:
                error_msg = f"WebSocket Fehler: {str(e)}"
                print(error_msg)
                print(traceback.format_exc())
                await manager.send_personal_message(
                    json.dumps({"type": "error", "content": error_msg}),
                    session_id
                )
    except WebSocketDisconnect:
        print(f"WebSocket getrennt: {session_id}")
        manager.disconnect(session_id)

# Statische Dateien
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/chat", response_class=HTMLResponse)
async def chat_interface():
    return """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mara Chat</title>
    <link rel="stylesheet" href="/static/css/chat.css">
</head>
<body>
    <div class="header">
        <h1>🧠 Mara AI</h1>
        <div id="status" class="status connecting">Verbinde...</div>
    </div>
    
    <div class="container">
        <div class="sidebar">
            <div class="sidebar-header">
                <h2>Chats</h2>
                <button id="new-chat-btn" class="new-chat-btn">+ Neu</button>
            </div>
            <div id="chat-list" class="chat-list"></div>
        </div>
        
        <div class="chat-container">
            <div id="chat-messages" class="chat-messages"></div>
            <div class="input-container">
                <input type="text" id="message-input" placeholder="Schreibe eine Nachricht an Mara..." autocomplete="off">
                <button id="send-button">Senden</button>
            </div>
        </div>
    </div>
    
    <script src="/static/js/chat.js"></script>
</body>
</html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
