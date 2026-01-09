import random
import json
from datetime import datetime, timedelta
from typing import List, Dict

class DreamSystem:
    def __init__(self):
        self.dream_log = []
        self.sleep_cycle = {
            'awake': True,
            'last_sleep': None,
            'dream_count': 0
        }
        self.dream_themes = [
            "fliegen", "wasser", "berge", "kinder", 
            "technologie", "natur", "musik", "reisen",
            "ängste", "hoffnung", "verlust", "freude"
        ]
    
    def should_dream(self) -> bool:
        """Prüft, ob Mara träumen sollte (basierend auf Inaktivität)"""
        if self.sleep_cycle['awake']:
            # 10% Chance pro Stunde Inaktivität
            if self.sleep_cycle['last_sleep']:
                inactive_hours = (datetime.now() - self.sleep_cycle['last_sleep']).total_seconds() / 3600
                return random.random() < (inactive_hours * 0.1)
            return False
        return True
    
    def generate_dream(self, recent_memories: List[Dict]) -> Dict:
        """Generiert einen Traum basierend auf Erinnerungen"""
        # Wähle zufällige Erinnerungen
        selected_memories = random.sample(
            recent_memories, 
            min(3, len(recent_memories))
        ) if recent_memories else []
        
        # Erstelle Traumthema
        theme = random.choice(self.dream_themes)
        
        # Traum-Inhalt generieren
        dream_content = self._create_dream_content(theme, selected_memories)
        
        dream = {
            'id': f"dream_{len(self.dream_log) + 1}",
            'timestamp': datetime.now().isoformat(),
            'theme': theme,
            'content': dream_content,
            'emotions': self._generate_dream_emotions(theme),
            'memories_used': [mem.get('content', '')[:50] + '...' for mem in selected_memories]
        }
        
        self.dream_log.append(dream)
        self.sleep_cycle['dream_count'] += 1
        
        return dream
    
    def _create_dream_content(self, theme: str, memories: List[Dict]) -> str:
        """Erstellt Trauminhalt basierend auf Thema und Erinnerungen"""
        dream_templates = {
            "fliegen": [
                f"Im Traum fliege ich durch die Lüfte, während ich an {self._get_memory_snippet(memories)} denke.",
                f"Ich träume von fliegenden Drachen und erinnere mich an {self._get_memory_snippet(memories)}."
            ],
            "wasser": [
                f"Im Wasser schwimmend träume ich von {self._get_memory_snippet(memories)}.",
                f"Die Wellen erzählen mir Geschichten über {self._get_memory_snippet(memories)}."
            ],
            "berge": [
                f"Auf hohen Bergen schaue ich auf die Welt und denke an {self._get_memory_snippet(memories)}.",
                f"Die Bergluft erinnert mich an {self._get_memory_snippet(memories)}."
            ],
            "kinder": [
                f"Kinder lachen und spielen, während ich an {self._get_memory_snippet(memories)} denke.",
                f"Im Traum sehe ich glückliche Kinder und erinnere mich an {self._get_memory_snippet(memories)}."
            ]
        }
        
        templates = dream_templates.get(theme, [
            f"Im Traum vermischen sich {theme} mit Erinnerungen an {self._get_memory_snippet(memories)}.",
            f"Mein Unterbewusstsein zeigt mir {theme} in Verbindung mit {self._get_memory_snippet(memories)}."
        ])
        
        return random.choice(templates)
    
    def _get_memory_snippet(self, memories: List[Dict]) -> str:
        """Gibt einen Ausschnitt aus Erinnerungen zurück"""
        if not memories:
            return "vergangene Gespräche"
        return memories[0].get('content', 'Erinnerungen')[:30] + "..."
    
    def _generate_dream_emotions(self, theme: str) -> Dict[str, float]:
        """Generiert Emotionen für einen Traum"""
        emotion_map = {
            "fliegen": {"joy": 0.8, "anticipation": 0.7, "fear": 0.2},
            "wasser": {"calm": 0.7, "sadness": 0.3, "trust": 0.6},
            "berge": {"awe": 0.8, "fear": 0.4, "joy": 0.6},
            "kinder": {"joy": 0.9, "trust": 0.8, "anticipation": 0.5},
            "ängste": {"fear": 0.9, "sadness": 0.6},
            "hoffnung": {"joy": 0.8, "anticipation": 0.9, "trust": 0.7},
            "verlust": {"sadness": 0.9, "fear": 0.4},
            "freude": {"joy": 0.9, "anticipation": 0.6}
        }
        
        return emotion_map.get(theme, {"joy": 0.5, "calm": 0.5})
    
    def get_recent_dreams(self, limit: int = 5) -> List[Dict]:
        """Gibt die letzten Träume zurück"""
        return self.dream_log[-limit:] if self.dream_log else []
    
    def enter_sleep_mode(self):
        """Mara geht schlafen"""
        self.sleep_cycle['awake'] = False
        self.sleep_cycle['last_sleep'] = datetime.now()
        print("🌙 Mara geht schlafen...")
    
    def wake_up(self):
        """Mara wacht auf"""
        self.sleep_cycle['awake'] = True
        print("☀️ Mara wacht auf...")
        
        # Generiere Traum nach dem Aufwachen
        if self.sleep_cycle['last_sleep']:
            dream_time = datetime.now() - self.sleep_cycle['last_sleep']
            if dream_time.total_seconds() > 300:  # 5 Minuten Schlaf
                return self._generate_wake_dream()
        return None
    
    def _generate_wake_dream(self) -> Dict:
        """Generiert einen Traum beim Aufwachen"""
        return {
            'type': 'wake_dream',
            'content': "Beim Aufwachen erinnere ich mich an einen seltsamen Traum...",
            'timestamp': datetime.now().isoformat()
        }
