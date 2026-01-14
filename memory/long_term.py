import chromadb
import ollama
import numpy as np
from typing import List, Dict, Optional, Any
import json
from datetime import datetime
import uuid

class LongTermMemory:
    def __init__(self):
        # ChromaDB Client
        self.client = chromadb.HttpClient(host="chromadb", port=8000)
        
        # Ollama Client mit richtigem Hostnamen
        self.ollama_client = ollama.Client(host='http://ollama:11434')
        
        # Erstelle oder hole Collection
        try:
            self.collection = self.client.get_or_create_collection(name="mara_memories")
        except Exception as e:
            print(f"Fehler beim Verbinden mit Collection: {e}")
            self.collection = self.client.create_collection("mara_memories")
    
    def _get_embedding(self, text: str) -> List[float]:
        """Erstelle Embedding mit Ollama"""
        try:
            # Nutze das schnellere Embedding-Modell
            response = self.ollama_client.embeddings(model='nomic-embed-text', prompt=text) 
            return response['embedding']
        except Exception as e:
            print(f"Embedding Fehler: {e}")
            return []
    
    def add_memory(self, content: str, metadata: Optional[Dict] = None):
        """Speichere Gedächtnis in Vector-Datenbank (Hieß vorher store_memory)"""
        if not content:
            return

        embedding = self._get_embedding(content)
        if not embedding:
            return
        
        # Standard-Metadaten
        default_metadata = {
            'timestamp': str(datetime.now()),
            'type': 'user_generated' if not metadata else metadata.get('type', 'user_generated')
        }
        
        # Kombiniere Metadaten
        if metadata:
            default_metadata.update(metadata)
        
        # IDs müssen Strings sein
        self.collection.add(
            documents=[content],
            embeddings=[embedding],
            metadatas=[default_metadata],
            ids=[str(uuid.uuid4())]
        )
        print(f"💾 Erinnerung gespeichert: {content[:30]}...")
    
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
        
        self.add_memory(conversation_text, metadata)
    
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
        if not conversation_history:
            return

        for message in conversation_history[-5:]:  # Nur letzte 5 prüfen
            importance = self.evaluate_importance(message['content'], message['role'])
            if importance >= threshold:
                metadata = {
                    'type': 'auto_detected',
                    'importance_score': importance,
                    'role': message['role']
                }
                # Nutze add_memory statt store_memory
                self.add_memory(message['content'], metadata)
    
    def search_memories(self, query: str, n_results: int = 5, min_importance: float = 0.0) -> List[Dict]:
        """Suche ähnliche Erinnerungen"""
        embedding = self._get_embedding(query)
        if not embedding:
            return []
        
        # Filter für minimale Wichtigkeit (optional)
        # Hinweis: where-Filter funktioniert nur, wenn 'importance' auch in Metadaten existiert
        where_filter = {"importance": {"$gte": min_importance}} if min_importance > 0 else None
        
        try:
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=n_results,
                where=where_filter
            )
        except Exception as e:
            print(f"Fehler bei der Suche: {e}")
            return []
        
        # Sicherstellen, dass Ergebnisse da sind
        if not results or not results['documents'] or not results['documents'][0]:
            return []
        
        memories = []
        for i, doc in enumerate(results['documents'][0]):
            memories.append({
                'content': doc,
                'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                'distance': results['distances'][0][i] if results['distances'] else 0
            })
            
        return memories