import chromadb
import ollama
import numpy as np
from typing import List, Dict, Optional
import json
from datetime import datetime

class LongTermMemory:
    def __init__(self):
        # ChromaDB Client
        self.client = chromadb.HttpClient(host="chromadb", port=8000)
        
        # Ollama Client mit richtigem Hostnamen
        self.ollama_client = ollama.Client(host='http://ollama:11434')
        
        # Erstelle oder hole Collection
        try:
            self.collection = self.client.create_collection("mara_memories")
        except:
            self.collection = self.client.get_collection("mara_memories")
    
    def _get_embedding(self, text: str) -> List[float]:
        """Erstelle Embedding mit Ollama"""
        response = self.ollama_client.embeddings(model='llama3', prompt=text)
        return response['embedding']
    
    def store_memory(self, content: str, metadata: Optional[Dict] = None):
        """Speichere Gedächtnis in Vector-Datenbank"""
        embedding = self._get_embedding(content)
        
        # Standard-Metadaten
        default_metadata = {
            'timestamp': datetime.now().isoformat(),
            'type': 'user_generated' if not metadata else metadata.get('type', 'user_generated')
        }
        
        # Kombiniere Metadaten
        if metadata:
            default_metadata.update(metadata)
        
        self.collection.add(
            documents=[content],
            embeddings=[embedding],
            metadatas=[default_metadata],
            ids=[f"memory_{len(self.collection.get()['ids']) + 1}_{int(datetime.now().timestamp())}"]
        )
    
    def store_conversation_memory(self, conversation: List[Dict], importance_score: float = 0.0):
        """Speichere eine ganze Konversation mit Wichtigkeitsbewertung"""
        # Erstelle Zusammenfassung der Konversation
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in conversation
        ])
        
        metadata = {
            'type': 'conversation',
            'importance': importance_score,
            'message_count': len(conversation)
        }
        
        self.store_memory(conversation_text, metadata)
    
    def evaluate_importance(self, message: str, role: str) -> float:
        """Bewerte die Wichtigkeit einer Nachricht (0.0 - 1.0)"""
        # Schlüsselwörter, die Wichtigkeit signalisieren
        important_keywords = [
            'wichtig', 'erinnere', 'merke', 'vergiss nicht', 'wichtig ist',
            'birthday', 'geburtstag', 'anniversary', 'hochzeitstag',
            'liebe', 'freund', 'familie', 'kind', 'sohn', 'tochter',
            'arbeit', 'job', 'projekt', 'ziel', 'traum',
            'problem', 'schwierig', 'hilfe', 'brauche'
        ]
        
        # Namen (könnte erweitert werden)
        names = ['josua', 'joshi', 'mara', 'frau', 'sohn']
        
        message_lower = message.lower()
        score = 0.0
        
        # Prüfe auf wichtige Schlüsselwörter
        for keyword in important_keywords:
            if keyword in message_lower:
                score += 0.3
        
        # Prüfe auf Namen
        for name in names:
            if name in message_lower:
                score += 0.2
        
        # Längere Nachrichten sind oft wichtiger
        if len(message) > 100:
            score += 0.1
        if len(message) > 200:
            score += 0.1
        
        # Assistant-Nachrichten mit persönlichen Inhalten
        if role == 'assistant' and any(word in message_lower for word in ['du hast', 'ich merke', 'wichtig']):
            score += 0.2
        
        return min(1.0, score)  # Maximal 1.0
    
    def auto_store_important_messages(self, conversation_history: List[Dict], threshold: float = 0.5):
        """Automatisch wichtige Nachrichten speichern"""
        for message in conversation_history[-5:]:  # Nur letzte 5 prüfen
            importance = self.evaluate_importance(message['content'], message['role'])
            if importance >= threshold:
                metadata = {
                    'type': 'auto_detected',
                    'importance_score': importance,
                    'role': message['role']
                }
                self.store_memory(message['content'], metadata)
    
    def search_memories(self, query: str, n_results: int = 5, min_importance: float = 0.0) -> List[Dict]:
        """Suche ähnliche Erinnerungen"""
        query_embedding = self._get_embedding(query)
        
        # Filter für minimale Wichtigkeit (optional)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where={"importance": {"$gte": min_importance}} if min_importance > 0 else None
        )
        
        # Sicherstellen, dass alle Listen existieren
        if not results['documents'][0]:
            return []
        
        return [
            {
                'content': doc,
                'metadata': meta if meta else {},
                'distance': dist
            }
            for doc, meta, dist in zip(
                results['documents'][0],
                results['metadatas'][0] if results['metadatas'][0] else [{} for _ in results['documents'][0]],
                results['distances'][0]
            )
        ]