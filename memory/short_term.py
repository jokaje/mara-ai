import json
import os
from typing import List, Dict

class ShortTermMemory:
    def __init__(self, filepath: str = "data/chat_history_default.json"):
        self.filepath = filepath
        self.conversation = []
        self._load_memory()
    
    def _load_memory(self):
        """Lädt den Verlauf aus der JSON-Datei"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.conversation = data
            except Exception as e:
                print(f"Fehler beim Laden des Gedächtnisses: {e}")
                self.conversation = []

    def _save_memory(self):
        """Speichert den Verlauf in die JSON-Datei"""
        try:
            # Stelle sicher, dass der Ordner existiert
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.conversation, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Fehler beim Speichern des Gedächtnisses: {e}")

    def add_message(self, role: str, content: str):
        """Fügt eine Nachricht hinzu und speichert sofort"""
        self.conversation.append({
            'role': role,
            'content': content
        })
        self._save_memory()
    
    def get_recent(self, limit: int = 10) -> List[Dict]:
        """Gibt nur die letzten X Nachrichten zurück (wichtig für CPU Performance!)"""
        return self.conversation[-limit:]
    
    def get_all(self) -> List[Dict]:
        """Gibt den gesamten Verlauf zurück"""
        return self.conversation
    
    def clear(self):
        """Löscht das Gedächtnis"""
        self.conversation = []
        self._save_memory()