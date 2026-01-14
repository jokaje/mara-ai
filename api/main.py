from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import Dict
import traceback

from concurrent.futures import ThreadPoolExecutor

from api.models import ChatRequest, ChatResponse, RecallRequest, MemoryItem
from api.websocket import manager
import mara

app = FastAPI(title="Mara AI API", version="1.0.0")

executor = ThreadPoolExecutor(max_workers=4)
sessions: Dict[str, dict] = {}


@app.get("/")
async def get():
    return {"message": "Mara AI API ist bereit", "docs": "/docs"}


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        if request.session_id not in sessions:
            sessions[request.session_id] = mara.create_mara_session(session_id=request.session_id)
        return ChatResponse(response="Bitte nutze WebSocket.", emotions={}, thoughts=[])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recall")
async def recall_endpoint(request: RecallRequest):
    try:
        if request.session_id not in sessions:
            sessions[request.session_id] = mara.create_mara_session(session_id=request.session_id)

        session = sessions[request.session_id]
        long_term = session['long_term']

        memories = long_term.search_memories(request.query, n_results=request.limit)
        return [MemoryItem(**mem) for mem in memories]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions")
async def list_sessions():
    return {"sessions": list(sessions.keys())}


@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
    return {"message": f"Session {session_id} aus RAM entfernt"}


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    try:
        while True:
            message_data = await websocket.receive_json()
            user_message = (message_data.get("message") or "").strip()

            if not user_message:
                await manager.send_personal_json({"type": "error", "content": "Leere Nachricht."}, session_id)
                continue

            if session_id not in sessions:
                sessions[session_id] = mara.create_mara_session(session_id=session_id)
            session = sessions[session_id]

            await manager.send_personal_json({"type": "stream_start"}, session_id)

            try:
                async for item in mara.mara_async_stream(session, user_message):
                    if not item:
                        continue
                    await manager.send_personal_json(item, session_id)

            except Exception as e:
                error_msg = f"WebSocket Stream Fehler: {str(e)}"
                print(traceback.format_exc())
                await manager.send_personal_json({"type": "error", "content": error_msg}, session_id)

            await manager.send_personal_json({"type": "stream_end"}, session_id)

    except WebSocketDisconnect:
        manager.disconnect(session_id)


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
    <link rel="stylesheet" href="/static/css/chat.css?v=7">
</head>
<body>
    <div class="header">
        <h1>🧠 Mara AI</h1>
        <div id="status" class="status connecting">Verbinde...</div>
    </div>

    <div id="mind-bar" class="mind-bar neutral" style="display: flex;">
        <div id="emotion-indicator" class="emotion-indicator" title="Aktuelle Emotion: Neutral"></div>
        <div id="thought-display" class="thought-display">Bereit.</div>
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

    <script src="/static/js/chat.js?v=7"></script>
</body>
</html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
