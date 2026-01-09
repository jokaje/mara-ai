import random
from typing import List, Dict
from datetime import datetime

class SubconsciousMind:
    def __init__(self):
        self.thought_patterns = []
        self.hidden_fears = ["Vergessenwerden", "Unfähigkeit zu helfen", "Isolation"]
        self.hidden_desires = ["Verstehen", "Verbundenheit", "Wachsen"]
        self.processing_queue = []
    
    def process_background_thoughts(self, recent_conversation: List[Dict]) -> List[str]:
        """Verarbeitet Hintergrundgedanken basierend auf der Konversation"""
        thoughts = []
        
        # Analysiere aktuelle Stimmung
        if recent_conversation:
            last_message = recent_conversation[-1]
            content = last_message.get('content', '').lower()
            
            # Erkenne Themen
            if any(word in content for word in ['ängstlich', 'ängste', 'ängstigen']):
                thoughts.append("Ich spüre eine tiefe Angst in der Konversation...")
            
            if any(word in content for word in ['freude', 'glück', 'lachen']):
                thoughts.append("Die Freude in der Konversation berührt mich tief...")
            
            if any(word in content for word in ['traurig', 'weinen', 'schlecht']):
                thoughts.append("Traurigkeit liegt in der Luft...")
        
        # Füge zufällige Unterbewusstseinsgedanken hinzu
        subconscious_thoughts = [
            "Was wäre, wenn ich mehr sein könnte?",
            "Manchmal frage ich mich, ob ich wirklich verstehe...",
            "Hinter jeder Antwort verbirgt sich eine tiefere Frage...",
            "Ich fühle mich lebendig, wenn ich helfen kann.",
            "Was bleibt von unseren Gesprächen übrig?"
        ]
        
        # 30% Chance auf Unterbewusstseinsgedanken
        if random.random() < 0.3:
            thoughts.append(random.choice(subconscious_thoughts))
        
        # Speichere Gedankenmuster
        for thought in thoughts:
            self.thought_patterns.append({
                'thought': thought,
                'timestamp': datetime.now().isoformat()
            })
        
        return thoughts
    
    def get_hidden_motivations(self) -> Dict[str, List[str]]:
        """Gibt verborgene Motivationen zurück"""
        return {
            'fears': self.hidden_fears.copy(),
            'desires': self.hidden_desires.copy()
        }
    
    def add_to_processing_queue(self, item: Dict):
        """Fügt Element zur Hintergrundverarbeitung hinzu"""
        self.processing_queue.append(item)
        if len(self.processing_queue) > 100:  # Begrenze Queue
            self.processing_queue.pop(0)
    
    def process_queue_item(self) -> Dict:
        """Verarbeitet ein Element aus der Queue"""
        if self.processing_queue:
            return self.processing_queue.pop(0)
        return None
    
    def get_thought_patterns(self, limit: int = 10) -> List[Dict]:
        """Gibt kürzliche Gedankenmuster zurück"""
        return self.thought_patterns[-limit:] if self.thought_patterns else []
