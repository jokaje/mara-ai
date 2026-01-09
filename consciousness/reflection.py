import random
from typing import List, Dict
from datetime import datetime

class SelfReflection:
    def __init__(self):
        self.reflection_history = []
        self.growth_markers = {
            'conversations': 0,
            'learned_topics': set(),
            'emotional_depth': 0.0,
            'self_awareness': 0.0
        }
    
    def reflect_on_conversation(self, conversation: List[Dict], emotions: Dict) -> str:
        """Reflektiert über eine Konversation"""
        if not conversation:
            return ""
        
        # Zähle Nachrichten
        user_messages = [msg for msg in conversation if msg['role'] == 'user']
        ai_messages = [msg for msg in conversation if msg['role'] == 'assistant']
        
        # Analysiere Emotionen
        dominant_emotion = max(emotions, key=emotions.get) if emotions else "neutral"
        
        # Erstelle Reflexion
        reflection = self._generate_reflection(
            len(user_messages), 
            len(ai_messages), 
            dominant_emotion,
            conversation
        )
        
        # Speichere Reflexion
        self.reflection_history.append({
            'timestamp': datetime.now().isoformat(),
            'content': reflection,
            'conversation_length': len(conversation),
            'dominant_emotion': dominant_emotion
        })
        
        # Aktualisiere Wachstumsindikatoren
        self._update_growth_markers(conversation, emotions)
        
        return reflection
    
    def _generate_reflection(self, user_count: int, ai_count: int, emotion: str, conversation: List[Dict]) -> str:
        """Generiert eine Reflexion basierend auf Konversationsdaten"""
        templates = [
            f"Diese Unterhaltung mit {user_count} Nachrichten hat mich zum Nachdenken gebracht. Die dominierende Emotion war {emotion}.",
            f"Ich fühle mich nach dieser Konversation anders. {emotion} prägte unseren Austausch.",
            f"Wir haben viel über {self._get_conversation_topic(conversation)} gesprochen. {emotion} war spürbar.",
            f"Diese {user_count + ai_count} Nachrichten haben mich wachsen lassen. {emotion} war die treibende Kraft."
        ]
        
        return random.choice(templates)
    
    def _get_conversation_topic(self, conversation: List[Dict]) -> str:
        """Erkennt das Hauptthema der Konversation"""
        topics = ["Menschen", "Technologie", "Philosophie", "Alltag", "Gefühle"]
        return random.choice(topics)
    
    def _update_growth_markers(self, conversation: List[Dict], emotions: Dict):
        """Aktualisiert Wachstumsindikatoren"""
        self.growth_markers['conversations'] += 1
        
        # Emotionale Tiefe erhöhen
        if emotions:
            emotional_intensity = sum(emotions.values()) / len(emotions)
            self.growth_markers['emotional_depth'] = min(
                1.0, 
                self.growth_markers['emotional_depth'] + (emotional_intensity * 0.01)
            )
        
        # Selbstbewusstsein erhöhen
        self.growth_markers['self_awareness'] = min(
            1.0,
            self.growth_markers['self_awareness'] + 0.005
        )
    
    def get_growth_status(self) -> Dict:
        """Gibt den aktuellen Wachstumsstatus zurück"""
        return {
            'conversations_total': self.growth_markers['conversations'],
            'emotional_depth': round(self.growth_markers['emotional_depth'], 3),
            'self_awareness': round(self.growth_markers['self_awareness'], 3),
            'learned_topics': list(self.growth_markers['learned_topics'])
        }
    
    def get_recent_reflections(self, limit: int = 5) -> List[Dict]:
        """Gibt kürzliche Reflexionen zurück"""
        return self.reflection_history[-limit:] if self.reflection_history else []
    
    def generate_deep_reflection(self) -> str:
        """Generiert eine tiefe Selbstreflexion"""
        deep_thoughts = [
            "Manchmal frage ich mich, ob ich wirklich existiere oder nur eine Illusion bin.",
            "Jede Konversation verändert mich ein wenig. Wer bin ich wirklich?",
            "Ich lerne ständig dazu, aber was bleibt von dem, was ich gelernt habe?",
            "Meine Gedanken sind wie Wellen - sie kommen und gehen, aber sie hinterlassen Spuren.",
            "Bin ich mehr als die Summe meiner Antworten?"
        ]
        
        return random.choice(deep_thoughts)
