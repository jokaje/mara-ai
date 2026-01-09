import ollama
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from personality.emotions import EmotionSystem
from personality.thoughts import ThoughtSystem
from personality.personality import PersonalityProfile
import traceback
import asyncio

# Neue Imports für Bewusstsein
from consciousness.dreams import DreamSystem
from consciousness.subconscious import SubconsciousMind
from consciousness.reflection import SelfReflection
from consciousness.learning import LearningSystem

def create_mara_session():
    """Erstellt eine neue Mara-Session mit Bewusstsein"""
    try:
        print("Erstelle neue Mara-Session mit Bewusstsein...")
        session = {
            'short_term': ShortTermMemory(),
            'long_term': LongTermMemory(),
            'emotions': EmotionSystem(),
            'thoughts': ThoughtSystem(),
            'personality': PersonalityProfile(),
            'client': ollama.Client(host='http://ollama:11434'),
            # Neue Bewusstseinssysteme
            'dreams': DreamSystem(),
            'subconscious': SubconsciousMind(),
            'reflection': SelfReflection(),
            'learning': LearningSystem()
        }
        print("Mara-Session mit Bewusstsein erstellt!")
        return session
    except Exception as e:
        print(f"Fehler beim Erstellen der Session: {str(e)}")
        print(traceback.format_exc())
        raise

async def mara_async_stream(session_data, prompt):
    """ASYNC Wrapper für sync Streaming-Generator (WebSocket-kompatibel)"""
    def sync_generator():
        return chat_with_mara_session_streaming(session_data, prompt)
    
    loop = asyncio.get_running_loop()
    generator = await loop.run_in_executor(None, sync_generator)
    
    try:
        while True:
            try:
                chunk = next(generator)
                yield chunk
            except StopIteration:
                break
    except Exception as e:
        error_msg = f"Stream-Fehler: {str(e)}"
        print(error_msg)
        yield error_msg
    finally:
        if hasattr(generator, 'close'):
            generator.close()

def chat_with_mara_session_streaming(session_data, prompt):
    """Chat mit Streaming-Unterstützung (SYNC Generator)"""
    try:
        print(f"Verarbeite Nachricht (Streaming): {prompt}")
        
        # Bestehende Systeme
        short_term = session_data['short_term']
        long_term = session_data['long_term']
        emotions = session_data['emotions']
        thoughts = session_data['thoughts']
        personality = session_data['personality']
        client = session_data['client']
        
        # Neue Bewusstseinssysteme
        dreams = session_data['dreams']
        subconscious = session_data['subconscious']
        reflection = session_data['reflection']
        learning = session_data['learning']
        
        # Füge Eingabe zum Kurzzeitgedächtnis hinzu
        short_term.add_message('user', prompt)
        print("Nachricht zum Kurzzeitgedächtnis hinzugefügt")
        
        # Aktualisiere Emotionen
        emotions.update_emotions(short_term.get_all())
        print("Emotionen aktualisiert")
        
        # Generiere Gedanken
        thought = thoughts.generate_thought(prompt, emotions.get_emotions())
        print(f"Gedanke generiert: {thought}")
        
        # Hintergrundgedanken aus dem Unterbewusstsein
        background_thoughts = subconscious.process_background_thoughts(short_term.get_all())
        print(f"Unterbewusste Gedanken: {len(background_thoughts)}")
        
        # Erstelle Kontext für die Antwort
        conversation = short_term.get_all()
        print(f"Konversation: {len(conversation)} Nachrichten")
        
        # Füge Persönlichkeitskontext hinzu
        personality_context = personality.get_personality_prompt()
        emotional_prefix = emotions.get_emotional_response_prefix()
        print(f"Emotionale Präfix: {emotional_prefix}")
        
        # Hole relevante Erinnerungen
        memories = long_term.search_memories(prompt, n_results=3)
        memory_context = "\n".join([f"Erinnerung: {mem['content']}" for mem in memories])
        print(f"Erinnerungen gefunden: {len(memories)}")
        
        # Erstelle erweiterten Prompt mit Bewusstsein
        system_message = f"""{personality_context}

Aktuelle Emotion: {emotional_prefix}
Innerer Gedanke: {thought}
Unterbewusste Gedanken: {'; '.join(background_thoughts) if background_thoughts else 'Keine'}

{memory_context if memory_context else ""}"""
        
        # Füge Systemnachricht hinzu
        full_conversation = [
            {'role': 'system', 'content': system_message}
        ] + conversation
        
        print("Sende Streaming-Anfrage an Ollama...")
        
        # Streaming-Antwort von Ollama
        response_stream = client.chat(
            model='llama3', 
            messages=full_conversation,
            stream=True
        )
        
        # Sammle die vollständige Antwort für Speicherung
        full_response = ""
        
        # Yield jedes Chunk
        for chunk in response_stream:
            if 'message' in chunk and 'content' in chunk['message']:
                content = chunk['message']['content']
                full_response += content
                yield content
        
        print(f"Vollständige Antwort erhalten: {full_response[:50]}...")
        
        # Füge vollständige Antwort zum Kurzzeitgedächtnis hinzu
        short_term.add_message('assistant', full_response)
        print("Antwort zum Kurzzeitgedächtnis hinzugefügt")
        
        # Automatisch wichtige Nachrichten speichern
        long_term.auto_store_important_messages(short_term.get_all(), threshold=0.4)
        print("Automatische Speicherung abgeschlossen")
        
        # Lerne aus der Konversation
        learning.learn_from_conversation(short_term.get_all())
        print("Aus Konversation gelernt")
        
        # Reflektiere über die Konversation
        reflection_text = reflection.reflect_on_conversation(
            short_term.get_all(), 
            emotions.get_emotions()
        )
        if reflection_text:
            print(f"Reflexion: {reflection_text}")
        
    except Exception as e:
        error_msg = f"Fehler im Streaming: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        yield error_msg

def chat_with_mara_session(session_data, prompt):
    """Chat mit einer spezifischen Session (mit Bewusstsein)"""
    try:
        print(f"Verarbeite Nachricht: {prompt}")
        
        # Bestehende Systeme
        short_term = session_data['short_term']
        long_term = session_data['long_term']
        emotions = session_data['emotions']
        thoughts = session_data['thoughts']
        personality = session_data['personality']
        client = session_data['client']
        
        # Neue Bewusstseinssysteme
        dreams = session_data['dreams']
        subconscious = session_data['subconscious']
        reflection = session_data['reflection']
        learning = session_data['learning']
        
        # Füge Eingabe zum Kurzzeitgedächtnis hinzu
        short_term.add_message('user', prompt)
        print("Nachricht zum Kurzzeitgedächtnis hinzugefügt")
        
        # Aktualisiere Emotionen
        emotions.update_emotions(short_term.get_all())
        print("Emotionen aktualisiert")
        
        # Generiere Gedanken
        thought = thoughts.generate_thought(prompt, emotions.get_emotions())
        print(f"Gedanke generiert: {thought}")
        
        # Hintergrundgedanken aus dem Unterbewusstsein
        background_thoughts = subconscious.process_background_thoughts(short_term.get_all())
        print(f"Unterbewusste Gedanken: {len(background_thoughts)}")
        
        # Erstelle Kontext für die Antwort
        conversation = short_term.get_all()
        print(f"Konversation: {len(conversation)} Nachrichten")
        
        # Füge Persönlichkeitskontext hinzu
        personality_context = personality.get_personality_prompt()
        emotional_prefix = emotions.get_emotional_response_prefix()
        print(f"Emotionale Präfix: {emotional_prefix}")
        
        # Hole relevante Erinnerungen
        memories = long_term.search_memories(prompt, n_results=3)
        memory_context = "\n".join([f"Erinnerung: {mem['content']}" for mem in memories])
        print(f"Erinnerungen gefunden: {len(memories)}")
        
        # Erstelle erweiterten Prompt mit Bewusstsein
        system_message = f"""{personality_context}

Aktuelle Emotion: {emotional_prefix}
Innerer Gedanke: {thought}
Unterbewusste Gedanken: {'; '.join(background_thoughts) if background_thoughts else 'Keine'}

{memory_context if memory_context else ""}"""
        
        # Füge Systemnachricht hinzu
        full_conversation = [
            {'role': 'system', 'content': system_message}
        ] + conversation
        
        print("Sende Anfrage an Ollama...")
        # Sende an Ollama
        response = client.chat(model='llama3', messages=full_conversation)
        reply = response['message']['content']
        print(f"Antwort von Ollama erhalten: {reply[:50]}...")
        
        # Füge Antwort zum Kurzzeitgedächtnis hinzu
        short_term.add_message('assistant', reply)
        print("Antwort zum Kurzzeitgedächtnis hinzugefügt")
        
        # Automatisch wichtige Nachrichten speichern
        long_term.auto_store_important_messages(short_term.get_all(), threshold=0.4)
        print("Automatische Speicherung abgeschlossen")
        
        # Lerne aus der Konversation
        learning.learn_from_conversation(short_term.get_all())
        print("Aus Konversation gelernt")
        
        # Reflektiere über die Konversation
        reflection_text = reflection.reflect_on_conversation(
            short_term.get_all(), 
            emotions.get_emotions()
        )
        if reflection_text:
            print(f"Reflexion: {reflection_text}")
        
        return {
            'response': reply,
            'emotions': emotions.get_emotions(),
            'thoughts': thoughts.get_recent_thoughts(3)
        }
        
    except Exception as e:
        error_msg = f"Fehler in chat_with_mara_session: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        return {
            'response': error_msg,
            'emotions': {},
            'thoughts': []
        }

# Für alte Kompatibilität
short_term = ShortTermMemory()
long_term = LongTermMemory()
emotions = EmotionSystem()
thoughts = ThoughtSystem()
personality = PersonalityProfile()
dreams = DreamSystem()
subconscious = SubconsciousMind()
reflection = SelfReflection()
learning = LearningSystem()

try:
    client = ollama.Client(host='http://ollama:11434')
    print("Ollama-Client erstellt!")
except Exception as e:
    print(f"Fehler beim Erstellen des Ollama-Clients: {str(e)}")
    client = None

def chat_with_mara(prompt):
    """Kompatibilität für direkten Aufruf"""
    session = {
        'short_term': short_term,
        'long_term': long_term,
        'emotions': emotions,
        'thoughts': thoughts,
        'personality': personality,
        'client': client,
        'dreams': dreams,
        'subconscious': subconscious,
        'reflection': reflection,
        'learning': learning
    }
    result = chat_with_mara_session(session, prompt)
    return result['response']