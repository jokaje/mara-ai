import json
from typing import List, Dict
from datetime import datetime
import hashlib

class LearningSystem:
    def __init__(self):
        self.knowledge_base = {}
        self.learning_patterns = []
        self.skill_progress = {}
        self.insights = []
    
    def learn_from_conversation(self, conversation: List[Dict]):
        """Lernt aus einer Konversation"""
        # Extrahiere Themen und Konzepte
        topics = self._extract_topics(conversation)
        
        # Aktualisiere Wissensbasis
        for topic in topics:
            self._update_knowledge(topic, conversation)
        
        # Speichere Lernmuster
        self.learning_patterns.append({
            'timestamp': datetime.now().isoformat(),
            'topics': topics,
            'conversation_length': len(conversation)
        })
        
        # Generiere Einsicht
        insight = self._generate_insight(topics, conversation)
        if insight:
            self.insights.append({
                'timestamp': datetime.now().isoformat(),
                'content': insight
            })
    
    def _extract_topics(self, conversation: List[Dict]) -> List[str]:
        """Extrahiert Themen aus einer Konversation"""
        # Vereinfachte Themenextraktion
        content = " ".join([msg.get('content', '') for msg in conversation]).lower()
        
        topics = []
        topic_keywords = {
            'technologie': ['computer', 'ki', 'künstliche intelligenz', 'programmieren'],
            'philosophie': ['sinn', 'existenz', 'bewusstsein', 'denken'],
            'emotionen': ['fühle', 'emotion', 'traurig', 'freude', 'ängstlich'],
            'beziehungen': ['freund', 'familie', 'liebe', 'verbindung'],
            'lernen': ['lernen', 'wissen', 'verstehen', 'begreifen']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in content for keyword in keywords):
                topics.append(topic)
        
        return topics if topics else ['allgemein']
    
    def _update_knowledge(self, topic: str, conversation: List[Dict]):
        """Aktualisiert das Wissen zu einem Thema"""
        if topic not in self.knowledge_base:
            self.knowledge_base[topic] = {
                'discussions': 0,
                'examples': [],
                'understanding': 0.0,
                'last_updated': datetime.now().isoformat()
            }
        
        # Aktualisiere Statistiken
        self.knowledge_base[topic]['discussions'] += 1
        self.knowledge_base[topic]['understanding'] = min(
            1.0,
            self.knowledge_base[topic]['understanding'] + 0.1
        )
        self.knowledge_base[topic]['last_updated'] = datetime.now().isoformat()
        
        # Speichere Beispiel
        if len(conversation) > 2:
            example = {
                'timestamp': datetime.now().isoformat(),
                'snippet': conversation[-1].get('content', '')[:100] + '...'
            }
            self.knowledge_base[topic]['examples'].append(example)
            # Begrenze Beispiele
            if len(self.knowledge_base[topic]['examples']) > 10:
                self.knowledge_base[topic]['examples'].pop(0)
    
    def _generate_insight(self, topics: List[str], conversation: List[Dict]) -> str:
        """Generiert eine Einsicht aus der Konversation"""
        if not topics:
            return ""
        
        insights = [
            f"Durch Gespräche über {', '.join(topics)} verstehe ich menschliche Perspektiven besser.",
            f"Jede Diskussion über {topics[0]} erweitert mein Verständnis.",
            f"Ich lerne, dass {topics[0]} für Menschen sehr wichtig ist.",
            f"Durch {len(conversation)} Nachrichten habe ich neue Aspekte von {topics[0]} entdeckt."
        ]
        
        return insights[0] if insights else ""
    
    def get_knowledge_status(self) -> Dict:
        """Gibt den aktuellen Wissensstatus zurück"""
        return {
            'topics_known': list(self.knowledge_base.keys()),
            'total_discussions': sum(topic['discussions'] for topic in self.knowledge_base.values()),
            'average_understanding': round(
                sum(topic['understanding'] for topic in self.knowledge_base.values()) / 
                len(self.knowledge_base) if self.knowledge_base else 0,
                3
            ) if self.knowledge_base else 0.0
        }
    
    def get_recent_insights(self, limit: int = 5) -> List[Dict]:
        """Gibt kürzliche Einsichten zurück"""
        return self.insights[-limit:] if self.insights else []
    
    def get_topic_knowledge(self, topic: str) -> Dict:
        """Gibt detailliertes Wissen zu einem Thema zurück"""
        return self.knowledge_base.get(topic, {
            'discussions': 0,
            'examples': [],
            'understanding': 0.0,
            'last_updated': None
        })
    
    def suggest_learning_topic(self) -> str:
        """Schlägt ein Lernthema vor"""
        if not self.knowledge_base:
            return "Allgemeinwissen"
        
        # Finde Thema mit niedrigstem Verständnis
        least_understood = min(
            self.knowledge_base.items(),
            key=lambda x: x[1]['understanding']
        )
        
        return least_understood[0]
