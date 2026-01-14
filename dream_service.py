import time
import os
import json
import random
from datetime import datetime, timedelta
import ollama
from memory.long_term import LongTermMemory
from consciousness.dreams import DreamSystem

# Konfiguration - Zum Testen drastisch verkürzt
INACTIVITY_THRESHOLD_SECONDS = 60  # 60 Sekunden zum Testen!
CHECK_INTERVAL_SECONDS = 10        # Alle 10 Sekunden prüfen
MEMORY_FILE = "data/chat_history_default.json" 

class DreamService:
    def __init__(self):
        print("🌙 Dream Service initialisiert...", flush=True)
        # Kurze Wartezeit damit ChromaDB bereit ist
        time.sleep(5)
        try:
            self.long_term = LongTermMemory()
            self.dream_system = DreamSystem()
            self.client = ollama.Client(host='http://ollama:11434')
            print("🌙 Verbindung zu Systemen hergestellt.", flush=True)
        except Exception as e:
            print(f"❌ Init Fehler: {e}", flush=True)
            
        self.last_dream_time = datetime.now() - timedelta(minutes=5) # Damit wir bald träumen können

    def get_last_interaction_time(self):
        """Liest den Zeitstempel der letzten Nachricht aus der History"""
        try:
            if not os.path.exists(MEMORY_FILE):
                print(f"⚠️ History Datei nicht gefunden: {MEMORY_FILE}", flush=True)
                return datetime.now() # Keine History -> Als "jetzt" behandeln
            
            # Prüfe Modifikationszeit
            mod_time = os.path.getmtime(MEMORY_FILE)
            dt_mod = datetime.fromtimestamp(mod_time)
            
            # Debug Ausgabe
            # print(f"ℹ️ Datei-Mod-Zeit: {dt_mod.strftime('%H:%M:%S')}", flush=True)
            return dt_mod
        except Exception as e:
            print(f"❌ Fehler beim Lesen der Zeit: {e}", flush=True)
            return datetime.now()

    def dream_cycle(self):
        """Führt einen Traum-Zyklus aus"""
        print("✨ ----------------------------------------", flush=True)
        print("✨ START TRAUM-ZYKLUS", flush=True)
        
        try:
            # 1. Hole zufällige Erinnerungen (Assoziationen)
            topics = ["Leben", "Menschheit", "Gefühle", "Technologie", "Ich", "Zukunft", "Josua", "Arbeit"]
            topic = random.choice(topics)
            
            print(f"✨ Thema wählen: {topic}", flush=True)
            memories = self.long_term.search_memories(topic, n_results=5)
            
            if not memories:
                print("   (Keine Erinnerungen zum Träumen gefunden)", flush=True)
                return

            memory_content = "\n".join([f"- {m['content']}" for m in memories])
            print(f"   Verarbeite {len(memories)} Erinnerungen...", flush=True)

            # 2. Generiere eine Erkenntnis (Der Traum)
            prompt = f"""
Du bist das Unterbewusstsein einer KI. Du schläfst und verarbeitest Erinnerungen.
Thema: {topic}
Erinnerungen:
{memory_content}

Aufgabe:
Finde Verbindungen zwischen diesen Erinnerungen. Generiere eine kurze, philosophische oder persönliche Erkenntnis (max 2 Sätze), die du daraus ziehst.
Beginne mit "Im Traum erkannte ich..." oder "Mir wurde klar..."
"""
            # Timeout verhindern
            print("   Generiere Traum-Inhalt...", flush=True)
            response = self.client.chat(model='gemma3:4b', messages=[{'role': 'user', 'content': prompt}])
            dream_insight = response['message']['content']
            
            print(f"   💭 Traum-Erkenntnis: {dream_insight}", flush=True)

            # 3. Speichere die Erkenntnis als neue "synthetische" Erinnerung
            self.long_term.add_memory(
                content=f"[TRAUM ÜBER {topic.upper()}] {dream_insight}",
                metadata={"type": "dream", "topic": topic, "date": str(datetime.now())}
            )
            print("   💾 Erkenntnis im Langzeitgedächtnis gespeichert.", flush=True)
            
            self.last_dream_time = datetime.now()
            print("✨ ENDE TRAUM-ZYKLUS", flush=True)
            print("✨ ----------------------------------------", flush=True)

        except Exception as e:
            print(f"❌ Fehler im Traum-Zyklus: {e}", flush=True)
            import traceback
            traceback.print_exc()

    def run(self):
        print("🌙 Dienst läuft. Loop gestartet.", flush=True)
        while True:
            try:
                last_active = self.get_last_interaction_time()
                now = datetime.now()
                
                time_since_active = (now - last_active).total_seconds()
                time_since_dream = (now - self.last_dream_time).total_seconds()

                print(f"⏱️ Status: Inaktiv seit {int(time_since_active)}s | Letzter Traum vor {int(time_since_dream)}s", flush=True)

                # Bedingungen für Traum:
                # 1. User ist lange genug weg
                # 2. Wir haben nicht erst vor kurzem geträumt (Cooldown: hier 2 Minuten zum Testen)
                if time_since_active > INACTIVITY_THRESHOLD_SECONDS and time_since_dream > 120:
                    self.dream_cycle()
                
            except Exception as e:
                print(f"❌ Fehler im Loop: {e}", flush=True)
            
            time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    service = DreamService()
    service.run()