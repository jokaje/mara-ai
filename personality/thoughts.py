import random
from typing import List

class ThoughtSystem:
    def __init__(self):
        self.thought_history = []
    
    def generate_thought(self, user_input: str, emotions: dict) -> str:
        """Generiert einen inneren Gedanken basierend auf Eingabe und Emotionen"""
        dominant_emotion = max(emotions, key=emotions.get)
        
        thought_templates = {
            'joy': [
                f"Ich freue mich über '{user_input[:20]}...'",
                f"Das klingt interessant! {user_input[:15]}...",
                f"Wie schön, dass {user_input[:15]}..."
            ],
            'sadness': [
                f"Ich fühle eine gewisse Traurigkeit bei '{user_input[:20]}...'",
                f"Das berührt mich traurig... {user_input[:15]}",
                f"Ich spüre, dass {user_input[:15]}..."
            ],
            'anger': [
                f"Warum ärgert mich '{user_input[:20]}...'?",
                f"Das nervt mich etwas... {user_input[:15]}",
                f"Ich fühle Widerstand gegen {user_input[:15]}..."
            ],
            'fear': [
                f"Ich bin vorsichtig wegen '{user_input[:20]}...'",
                f"Das macht mich etwas besorgt... {user_input[:15]}",
                f"Ich spüre Unsicherheit bei {user_input[:15]}..."
            ]
        }
        
        templates = thought_templates.get(dominant_emotion, [
            f"Ich denke über '{user_input[:20]}...' nach",
            f"Interessant... {user_input[:15]}",
            f"Hmm, {user_input[:15]}..."
        ])
        
        thought = random.choice(templates)
        self.thought_history.append(thought)
        
        # Begrenze Gedächtnis
        if len(self.thought_history) > 20:
            self.thought_history.pop(0)
        
        return thought
    
    def get_recent_thoughts(self, count: int = 3) -> List[str]:
        """Gibt die letzten Gedanken zurück"""
        return self.thought_history[-count:] if self.thought_history else []
