from pydantic import BaseModel
from typing import List, Dict, Optional

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    emotions: Optional[Dict[str, float]] = None
    thoughts: Optional[List[str]] = None

class MemoryItem(BaseModel):
    content: str
    metadata: Optional[Dict] = None
    distance: Optional[float] = None

class RecallRequest(BaseModel):
    query: str
    session_id: str = "default"
    limit: int = 5
