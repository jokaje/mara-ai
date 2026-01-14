import ollama
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from personality.emotions import EmotionSystem
from personality.thoughts import ThoughtSystem
from personality.personality import PersonalityProfile
import traceback
import asyncio

from consciousness.dreams import DreamSystem
from consciousness.subconscious import SubconsciousMind
from consciousness.reflection import SelfReflection
from consciousness.learning import LearningSystem


def create_mara_session(session_id=None):
    """Erstellt eine neue Mara-Session mit Bewusstsein und eigener Speicherdatei"""
    try:
        print(f"Erstelle neue Mara-Session (ID: {session_id})...")

        if session_id:
            memory_file = f"data/sessions/{session_id}.json"
        else:
            memory_file = "data/chat_history_default.json"

        session = {
            'short_term': ShortTermMemory(filepath=memory_file),
            'long_term': LongTermMemory(),
            'emotions': EmotionSystem(),
            'thoughts': ThoughtSystem(),
            'personality': PersonalityProfile(),
            'client': ollama.Client(host='http://ollama:11434'),
            'dreams': DreamSystem(),
            'subconscious': SubconsciousMind(),
            'reflection': SelfReflection(),
            'learning': LearningSystem()
        }
        print("Mara-Session erfolgreich erstellt!")
        return session
    except Exception as e:
        print(f"Fehler beim Erstellen der Session: {str(e)}")
        print(traceback.format_exc())
        raise


def _safe_get_message_text(chunk: dict) -> str:
    msg = chunk.get("message") or {}
    content = msg.get("content")
    if isinstance(content, str) and content:
        return content
    return ""


def _safe_get_message_thinking(chunk: dict) -> str:
    """
    Für thinking-fähige Modelle: chunk.message.thinking kann existieren.
    Ollama dokumentiert ein 'thinking' Feld bei thinking-capable models. [web:6]
    """
    msg = chunk.get("message") or {}
    thinking = msg.get("thinking")
    if isinstance(thinking, str) and thinking:
        return thinking
    return ""


def chat_with_mara_session_streaming(session_data, prompt):
    """Chat mit Streaming-Unterstützung (SYNC Generator)"""
    try:
        print(f"Verarbeite Nachricht (Streaming): {prompt}")

        short_term = session_data['short_term']
        long_term = session_data['long_term']
        emotions = session_data['emotions']
        thoughts = session_data['thoughts']
        personality = session_data['personality']
        client = session_data['client']

        subconscious = session_data['subconscious']
        reflection = session_data['reflection']
        learning = session_data['learning']

        short_term.add_message('user', prompt)

        # Kontext + Emotionen initial
        recent_context = short_term.get_recent(10)
        emotions.update_emotions(recent_context)
        dominant_emotion = emotions.get_dominant_emotion()

        # Dein eigener interner Gedanke (das ist NICHT Modell-thinking)
        internal_thought = thoughts.generate_thought(prompt, emotions.get_emotions())

        # Sofort UI füttern
        yield {"type": "meta", "thought": internal_thought, "emotion": dominant_emotion}

        background_thoughts = subconscious.process_background_thoughts(recent_context)

        personality_context = personality.get_personality_prompt()
        emotional_prefix = emotions.get_emotional_response_prefix()

        memories = long_term.search_memories(prompt, n_results=3)
        memory_context = "\n".join([f"Erinnerung: {mem['content']}" for mem in memories])
        print(f"Erinnerungen gefunden: {len(memories)}")

        system_message = f"""{personality_context}

### INTERNE SYSTEM-DATEN (NICHT TEIL DER ANTWORT)
Die folgenden Informationen definieren deinen aktuellen Zustand. Sie dienen nur zur Färbung deiner Sprache.
* [EMOTION]: {emotional_prefix}
* [GEDANKE]: {internal_thought}
* [UNTERBEWUSSTSEIN]: {'; '.join(background_thoughts) if background_thoughts else 'Ruhig'}

### ANWEISUNG FÜR DIE AUSGABE
Antworte dem Nutzer jetzt direkt.
REGEL: Gib niemals interne Gedanken, Emotionen, Systemdaten, Regieanweisungen oder Klammer-Kommentare aus.
REGEL: Keine Abschnitte wie „Innerer Gedanke:“ oder „(denkt …)“ oder ähnliches.
REGEL: Gib nur die endgültige Nutzer-Antwort aus.

{memory_context if memory_context else ""}"""

        full_conversation = [{'role': 'system', 'content': system_message}] + recent_context

        yield {"type": "meta", "thought": "Formuliere Antwort...", "emotion": dominant_emotion}

        response_stream = client.chat(
            model='gemma3:4b',
            messages=full_conversation,
            stream=True
        )

        full_response = ""
        last_thinking_sent = ""
        chunk_i = 0

        for chunk in response_stream:
            chunk_i += 1

            # 1) Modell-thinking (falls vorhanden) als Gedanke oben anzeigen
            thinking = _safe_get_message_thinking(chunk)
            if thinking:
                # nicht spam-en: nur senden wenn neu/anders
                if thinking != last_thinking_sent:
                    last_thinking_sent = thinking
                    # Emotion aktualisieren (damit "trust" nicht ewig hängt)
                    emotions.update_emotions(short_term.get_recent(10))
                    yield {
                        "type": "meta",
                        "thought": thinking,
                        "emotion": emotions.get_dominant_emotion()
                    }

            # 2) Normaler Text -> chat stream
            text = _safe_get_message_text(chunk)
            if text:
                full_response += text
                yield {"type": "text", "content": text}

            # 3) Zusätzlich: Emotion zyklisch refreshen (damit sie sichtbar variieren kann)
            if chunk_i % 20 == 0:
                emotions.update_emotions(short_term.get_recent(10))
                yield {
                    "type": "meta",
                    "thought": last_thinking_sent or internal_thought,
                    "emotion": emotions.get_dominant_emotion()
                }

        print(f"Vollständige Antwort erhalten (Länge: {len(full_response)})")

        short_term.add_message('assistant', full_response)

        # Abschluss-Meta
        emotions.update_emotions(short_term.get_recent(10))
        yield {"type": "meta", "thought": "Bereit.", "emotion": emotions.get_dominant_emotion()}

        # Speicher/Lernen
        long_term.auto_store_important_messages(short_term.get_recent(5), threshold=0.4)
        learning.learn_from_conversation(short_term.get_recent(10))
        reflection.reflect_on_conversation(short_term.get_recent(10), emotions.get_emotions())

    except Exception as e:
        error_msg = f"Fehler im Streaming: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        yield {"type": "error", "content": error_msg}


async def mara_async_stream(session_data, prompt):
    """
    ECHTES Async-Streaming:
    Sync generator im Thread, pusht Items thread-safe in eine asyncio.Queue
    via loop.call_soon_threadsafe(). [web:66][web:55]
    """
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()
    sentinel = object()

    def producer():
        try:
            for item in chat_with_mara_session_streaming(session_data, prompt):
                loop.call_soon_threadsafe(queue.put_nowait, item)
        except Exception as e:
            loop.call_soon_threadsafe(queue.put_nowait, {"type": "error", "content": f"Stream-Fehler: {str(e)}"})
        finally:
            loop.call_soon_threadsafe(queue.put_nowait, sentinel)

    loop.run_in_executor(None, producer)

    while True:
        item = await queue.get()
        if item is sentinel:
            break
        yield item


def chat_with_mara_session(session_data, prompt):
    """Non-Streaming Chat (REST/Debug)"""
    try:
        short_term = session_data['short_term']
        emotions = session_data['emotions']
        thoughts = session_data['thoughts']
        personality = session_data['personality']
        client = session_data['client']
        subconscious = session_data['subconscious']

        short_term.add_message('user', prompt)
        recent_context = short_term.get_recent(10)

        emotions.update_emotions(recent_context)
        internal_thought = thoughts.generate_thought(prompt, emotions.get_emotions())
        background_thoughts = subconscious.process_background_thoughts(recent_context)

        personality_context = personality.get_personality_prompt()
        emotional_prefix = emotions.get_emotional_response_prefix()

        system_message = f"""{personality_context}

### INTERNE SYSTEM-DATEN (NICHT TEIL DER ANTWORT)
* [EMOTION]: {emotional_prefix}
* [GEDANKE]: {internal_thought}
* [UNTERBEWUSSTSEIN]: {'; '.join(background_thoughts) if background_thoughts else 'Ruhig'}

### ANWEISUNG
Antworte direkt.
REGEL: Keine Gedanken, keine Regieanweisungen, kein „Innerer Gedanke:“, keine Klammer-Kommentare.
Gib nur die finale Nutzerantwort aus.
"""

        full_conversation = [{'role': 'system', 'content': system_message}] + recent_context

        response = client.chat(model='gemma3:4b', messages=full_conversation)
        reply = response['message']['content']

        short_term.add_message('assistant', reply)

        return {'response': reply, 'emotions': emotions.get_emotions(), 'thoughts': thoughts.get_recent_thoughts(3)}

    except Exception as e:
        error_msg = f"Fehler in chat_with_mara_session: {str(e)}"
        print(error_msg)
        return {'response': error_msg, 'emotions': {}, 'thoughts': []}
