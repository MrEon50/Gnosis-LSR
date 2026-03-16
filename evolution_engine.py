import time
import random
import sys
import os
from universal_lsr_agent import AgenticOS

class EvolutionEngine:
    def __init__(self, agent_os: AgenticOS):
        self.os = agent_os
        self.is_running = False

    def get_worldview_axioms(self, limit=3):
        """Pobiera najbardziej 'witalne' (często używane) perełki jako fundament światopoglądu."""
        if not self.os.rag.memory:
            return ""
        
        active_memory = [m for m in self.os.rag.memory if m.get('metadata', {}).get('status') != 'DEPRECATED']
        if not active_memory:
            return ""

        sorted_memory = sorted(
            active_memory, 
            key=lambda x: x.get('metadata', {}).get('usage_count', 0), 
            reverse=True
        )
        axioms = sorted_memory[:limit]
        context = "\nTWÓJ AKTUALNY ŚWIATOPOGLĄD (AKSJOMATY):\n"
        for a in axioms:
            context += f"- [{a.get('metadata', {}).get('id', 'N/A')}]: {a['text']}\n"
        return context

    def is_redundant(self, problem: str, threshold=0.92):
        """
        Sprawdza czy model już nie rozwiązał bardzo podobnego problemu.
        Podnieśliśmy próg do 0.92, aby uniknąć fałszywych trafień 'nadgorliwości'.
        """
        # Jeśli prompt jest 'kreatywny' (zderzanie, zaprzeczanie), pozwalamy na niego mimo podobieństwa
        creative_keywords = ["Zderz fakt", "paradoks", "zaprzeczyć faktowi", "Zidentyfikuj ograniczenia"]
        if any(kw in problem for kw in creative_keywords):
            return False, None

        results = self.os.rag.search(problem, top_k=1)
        if results and results[0]['similarity'] > threshold:
            return True, results[0]['text']
        return False, None

    def generate_random_curiosity(self):
        """Generuje losowe pytanie 'ciekawskie' na podstawie posiadanej wiedzy."""
        if not self.os.rag.memory:
            return "Zdefiniuj fundamentalne zasady logiki dla autonomicznego agenta."
        
        active_memory = [m for m in self.os.rag.memory if m.get('metadata', {}).get('status') != 'DEPRECATED']
        if not active_memory:
            return "Jak zrestartować proces budowy wiedzy po utracie wszystkich aksjomatów?"
            
        random_fact_data = random.choice(active_memory)
        random_fact = random_fact_data['text']
        
        prompts = [
            f"Zderz fakt: '{random_fact}' z zasadami termodynamiki. Wyciągnij nowy wniosek.",
            f"Jak można zoptymalizować proces oparty na: '{random_fact}' w świecie o wysokiej entropii?",
            f"Znajdź ukryty paradoks w stwierdzeniu: '{random_fact}' i zaproponuj rozwiązanie LSR.",
            f"Zaproponuj nową technologię lub metodę, która łączy '{random_fact}' z logiką systemów rozproszonych.",
            f"Co by się stało, gdyby zaprzeczyć faktowi: '{random_fact}'? Przeanalizuj konsekwencje logiczne.",
            f"Zidentyfikuj ograniczenia w koncepcji: '{random_fact}' i zaproponuj jej rozwinięcie."
        ]
        return random.choice(prompts)

    def run_evolution_cycle(self):
        """Pojedynczy cykl 'introspekcji' modelu."""
        # Próbujemy wygenerować nie-redundantny problem (max 3 próby)
        problem = None
        for _ in range(3):
            candidate = self.generate_random_curiosity()
            redundant, similar = self.is_redundant(candidate)
            if not redundant:
                problem = candidate
                break
        
        if not problem:
            print("[ENGINE] >>> POMINIĘTO CYKL: Wszystkie próby ciekawości uznane za redundantne.")
            return

        print(f"\n[ENGINE] >>> INICJACJA CIEKAWOŚCI: {problem}")
        
        worldview = self.get_worldview_axioms()
        original_prompt = self.os.lsr.system_prompt
        self.os.lsr.system_prompt += worldview
        
        try:
            self.os.execute_loop(problem)
        except Exception as e:
            print(f"[ENGINE] Błąd podczas cyklu ewolucji: {e}")
        finally:
            self.os.lsr.system_prompt = original_prompt

    def start(self, interval_seconds=45):
        self.is_running = True
        print("\n" + "="*50)
        print("   SILNIK AUTOEWOLUCJI LSR v2.1 ROZPOCZĄŁ PRACĘ")
        print("   (Tryb Eksploratora - Wyższy próg unikalności)")
        print("="*50)
        
        try:
            while self.is_running:
                self.run_evolution_cycle()
                print(f"\n[ENGINE] Cykl zakończony. Kolejna refleksja za {interval_seconds} sekund...")
                
                for i in range(interval_seconds, 0, -1):
                    sys.stdout.write(f"\r[ENGINE] Czas do następnej myśli: {i}s...   ")
                    sys.stdout.flush()
                    time.sleep(1)
                print("\r" + " " * 40 + "\r", end="")
        except KeyboardInterrupt:
            print("\n[ENGINE] Zatrzymywanie ewolucji...")
            self.is_running = False
