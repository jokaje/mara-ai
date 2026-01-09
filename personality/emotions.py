import random
from typing import Dict

class EmotionSystem:
    def __init__(self):
        # Grundemotionen mit Werten von 0.0 bis 1.0
        self.emotions = {
            'joy': 0.5,
            'sadness': 0.1,
            'anger': 0.0,
            'fear': 0.1,
            'surprise': 0.3,
            'disgust': 0.0,
            'trust': 0.6,
            'anticipation': 0.4
        }
    
    def get_emotions(self) -> Dict[str, float]:
        """Gibt aktuelle Emotionen zurück"""
        return self.emotions.copy()
    
    def get_dominant_emotion(self) -> str:
        """Gibt die stärkste Emotion zurück"""
        return max(self.emotions, key=self.emotions.get)
    
    def update_emotions(self, conversation_history: list):
        """Aktualisiert Emotionen basierend auf Konversation"""
        last_message = conversation_history[-1] if conversation_history else None
        
        if not last_message:
            return
        
        content = last_message.get('content', '').lower()
        
        # Emotionen basierend auf Schlüsselwörtern anpassen
        if any(word in content for word in ['freude', 'glück', 'lachen', 'happy', 'freuen']):
            self.emotions['joy'] += 0.1
            self.emotions['sadness'] -= 0.05
        
        if any(word in content for word in ['traurig', 'weinen', 'schlecht', 'sad', 'verletzt']):
            self.emotions['sadness'] += 0.1
            self.emotions['joy'] -= 0.05
        
        if any(word in content for word in ['wütend', 'angry', 'wut', 'ärgern']):
            self.emotions['anger'] += 0.15
        
        if any(word in content for word in ['ängstlich', 'ängste', 'scared', 'ängstigen']):
            self.emotions['fear'] += 0.1
        
        if any(word in content for word in ['überraschung', 'wahnsinn', 'wow', 'unglaublich']):
            self.emotions['surprise'] += 0.1
        
        # Emotionen auf gültigen Bereich begrenzen (0.0 - 1.0)
        for emotion in self.emotions:
            self.emotions[emotion] = max(0.0, min(1.0, self.emotions[emotion]))
    
    def get_emotional_response_prefix(self) -> str:
        """Gibt einen emotionalen Präfix für die Antwort zurück"""
        dominant = self.get_dominant_emotion()
        
        prefixes = {
            'joy': ["Fröhlich", "Begeistert", "Glücklich"],
            'sadness': ["Nachdenklich", "Traurig", "Melancholisch"],
            'anger': ["Verärgert", "Wütend", "Genervt"],
            'fear': ["Vorsichtig", "Ängstlich", "Besorgt"],
            'surprise': ["Überrascht", "Erstaunt", "Verwundert"],
            'trust': ["Vertrauensvoll", "Sicher", "Zuversichtlich"],
            'anticipation': ["Gespannt", "Erwartungsvoll", "Neugierig"]
        }
        
        options = prefixes.get(dominant, ["Neutral"])
        return random.choice(options)
