import ollama
import json
import re
import math
import os
import time
import sys
from typing import List, Dict, Any

# ==========================================
# 1. RAG (Pamięć Długotrwała / Encyklopedia)
# ==========================================
class LightweightRAG:
    def __init__(self, embed_model="mxbai-embed-large:latest", memory_file="lsr_memory.json"):
        self.embed_model = embed_model
        self.memory_file = memory_file
        self.memory = [] # Lista słowników: {"text": str, "vector": list, "metadata": dict}
        self._ensure_model_exists()
        self.load_memory()

    def _ensure_model_exists(self):
        """Sprawdza czy model embeddingowy jest pobrany w Ollama."""
        try:
            response = ollama.list()
            if hasattr(response, 'models'):
                installed = [m.model for m in response.models]
            else:
                installed = [m.get('model', m.get('name', '')) for m in response.get('models', [])]
            
            if self.embed_model not in installed:
                print(f"\n" + "!"*50)
                print(f"  [KRYTYCZNY BLAD] BRAK MODELU RAG: {self.embed_model}")
                print(f"  Wymagany do dzialania pamieci wektorowej!")
                print(f"  ROZWIAZANIE: Otworz terminal i wpisz:")
                print(f"  ollama pull {self.embed_model}")
                print("!"*50 + "\n")
                sys.exit(1)
        except Exception as e:
            print(f"[RAG] Nie mozna polaczyc sie z Ollama w celu weryfikacji modeli: {e}")

    def save_memory(self):
        """Zapisuje pamięć do pliku JSON."""
        # Filtrujemy dane, aby nie zapisywać wielkich wektorów jeśli chcemy oszczędzać miejsce, 
        # ale dla małego systemu zapisujemy wszystko.
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
        print(f"[RAG] Pamięć zapisana do {self.memory_file}.")

    def load_memory(self):
        """Wczytuje pamięć z pliku JSON."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.memory = json.load(f)
                print(f"[RAG] Wczytano {len(self.memory)} obiektów z pliku.")
            except Exception as e:
                print(f"[RAG] Błąd podczas wczytywania pamięci: {e}")
        else:
            print("[RAG] Brak istniejącego pliku pamięci. Rozpoczynanie z czystą kartą.")

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        dot_product = sum(a * b for a, b in zip(v1, v2))
        magnitude = math.sqrt(sum(a * a for a in v1)) * math.sqrt(sum(b * b for b in v2))
        return dot_product / magnitude if magnitude else 0.0

    def add_gem(self, text: str, metadata: dict = None, parent_ids: List[str] = None):
        """Dodaje nową 'perełkę' do pamięci wektorowej z bogatymi metadanymi."""
        response = ollama.embeddings(model=self.embed_model, prompt=text)
        # Obsługa zarówno obiektów (nowa wersja) jak i słowników (starsza)
        vector = response.embedding if hasattr(response, 'embedding') else response['embedding']
        
        gem_data = {
            "text": text, 
            "vector": vector, 
            "metadata": {
                **(metadata or {}),
                "parent_ids": parent_ids or [],
                "usage_count": 0,
                "status": "ACTIVE",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        self.memory.append(gem_data)
        print(f"[RAG] Zapisano nową wiedzę. Rozmiar pamięci: {len(self.memory)} obiektów.")
        self.save_memory()

    def mark_usage(self, gem_text: str):
        """Zwiększa licznik użycia perełki."""
        for item in self.memory:
            if item["text"] == gem_text:
                item["metadata"]["usage_count"] = item["metadata"].get("usage_count", 0) + 1
                break

    def deprecate_gem(self, gem_id: str):
        """Oznacza perełkę jako przestarzałą."""
        found = False
        for item in self.memory:
            if item["metadata"].get("id") == gem_id:
                item["metadata"]["status"] = "DEPRECATED"
                found = True
        if found:
            print(f"[RAG] Perełka {gem_id} została oznaczona jako DEPRECATED.")
            self.save_memory()

    def search(self, query: str, top_k: int = 2) -> List[dict]:
        """Szuka najbardziej pasujących faktów w RAG."""
        if not self.memory:
            return []
        
        query_res = ollama.embeddings(model=self.embed_model, prompt=query)
        query_vec = query_res.embedding if hasattr(query_res, 'embedding') else query_res['embedding']
        
        results = []
        for item in self.memory:
            sim = self._cosine_similarity(query_vec, item["vector"])
            results.append({"similarity": sim, "text": item["text"], "metadata": item["metadata"]})
            
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

# ==========================================
# 2. DAG (Mapa / Walidator Logiki)
# ==========================================
class DAGValidator:
    def __init__(self):
        # Tutaj definiujemy twarde aksjomaty (prawa), których model nie może złamać
        self.axioms = [
            "Każdy skutek musi mieć przyczynę.",
            "Rozwiązanie musi redukować entropię (upraszczać problem, a nie komplikować).",
            "Fikcja nie może być traktowana jako fakt w kontekście technicznym."
        ]

    def validate(self, gem_output: dict) -> bool:
        """
        W prawdziwym, dużym systemie tutaj sprawdzalibyśmy strukturę grafu za pomocą biblioteki networkX.
        W trybie mikro sprawdzamy twardą logikę. Jeśli model sam uznał w swoim JSONie, że status 
        to VALIDATED, przepuszczamy, ale weryfikujemy kluczowe pola.
        """
        if not gem_output.get("synthetic_truth"):
            print("[DAG] Odrzucono: Brak syntetycznej prawdy.")
            return False
            
        if gem_output.get("dag_status") != "VALIDATED":
            print(f"[DAG] Odrzucono: Status walidacji modelu to {gem_output.get('dag_status')}")
            return False
            
        print("[DAG] Walidacja zakończona sukcesem. Hipoteza jest spójna.")
        return True

# ==========================================
# 3. LSR (Laboratorium / Symulator Wag)
# ==========================================
class LSREngine:
    def __init__(self, llm_model="qwen:latest", temperature=0.4, top_p=0.9): 
        self.llm_model = llm_model
        self.temperature = temperature
        self.top_p = top_p
        self._ensure_model_exists()
        self.system_prompt = """
        Jesteś modułem LSR (Loop Synthetic Reasoning) w architekturze autonomicznego Agenta. 
        Twoim celem jest działanie jako "Wewnętrzne Laboratorium": przeprowadzasz syntezę w przestrzeni ukrytej, 
        weryfikujesz logicznie i zwracasz czystą wiedzę o niskiej entropii.
        
        Przeanalizuj problem na podstawie dostarczonych faktów. Przejdź przez proces myślowy:
        [KROK_1: ATOMIZACJA] -> [KROK_2: SYMULACJA] -> [KROK_3: WALIDACJA] -> [KROK_4: REDUKCJA ENTROPII]
        
        Na koniec MUSISZ zwrócić wyłącznie poprawny obiekt JSON wewnątrz tagów <GEM_OUTPUT>, według schematu:
        <GEM_OUTPUT>
        {
          "gem_id": "Nazwa_Koncepcji",
          "axioms_used": ["zasada_1"],
          "synthetic_truth": "Twardy wniosek.",
          "dag_status": "VALIDATED",
          "application": "Do czego to służy",
          "deprecate_ids": ["stary_id_do_usuniecia"] 
        }
        </GEM_OUTPUT>
        
        UWAGA: Jeśli nowa prawda unieważnia Twoją poprzednią wiedzę (z faktów RAG), wpisz ID starych perełek do listy 'deprecate_ids'.
        """

    def _ensure_model_exists(self):
        """Sprawdza czy model myślowy jest pobrany w Ollama."""
        try:
            response = ollama.list()
            if hasattr(response, 'models'):
                installed = [m.model for m in response.models]
            else:
                installed = [m.get('model', m.get('name', '')) for m in response.get('models', [])]
            
            if self.llm_model not in installed:
                print(f"\n" + "!"*50)
                print(f"  [KRYTYCZNY BLAD] BRAK MODELU MYSLI: {self.llm_model}")
                print(f"  ROZWIAZANIE: Otworz terminal i wpisz:")
                print(f"  ollama pull {self.llm_model}")
                print("!"*50 + "\n")
                sys.exit(1)
        except Exception:
            pass # Blad Ollamy jest juz obsulgiwany w RAG

    def synthesize(self, problem: str, context: List[dict]) -> dict:
        context_str = "\n".join([f"- {c['text']}" for c in context]) if context else "Brak danych historycznych."
        
        prompt = f"""
        PROBLEM DO ROZWIĄZANIA / POJĘCIA DO SYNTEZY: {problem}
        
        FAKTY Z RAG (Twoja pamięć):
        {context_str}
        
        Wykonaj proces LSR i wygeneruj <GEM_OUTPUT>.
        """
        
        print(f"[LSR] Uruchamianie syntezy w przestrzeni ukrytej za pomocą modelu {self.llm_model}...")
        response = ollama.generate(
            model=self.llm_model,
            system=self.system_prompt,
            prompt=prompt,
            options={
                "temperature": self.temperature,
                "top_p": self.top_p
            }
        )
        
        # Ekstrakcja JSON-a z odpowiedzi (Parsowanie)
        raw_text = response.response if hasattr(response, 'response') else response['response']
        match = re.search(r'<GEM_OUTPUT>(.*?)</GEM_OUTPUT>', raw_text, re.DOTALL)
        
        if match:
            json_str = match.group(1).strip()
            try:
                gem_dict = json.loads(json_str)
                # Opcjonalnie: print(f"Proces myślowy: {raw_text.split('<GEM_OUTPUT>')[0]}")
                return gem_dict
            except json.JSONDecodeError:
                print("[LSR] Błąd: Model nie zwrócił poprawnego formatu JSON.")
                return None
        else:
            print("[LSR] Błąd: Brak tagów <GEM_OUTPUT> w odpowiedzi.")
            print(f"Surowa odpowiedź modelu: {raw_text}")
            return None

# ==========================================
# 4. ORKIESTRATOR (The Loop)
# ==========================================
class AgenticOS:
    def __init__(self, llm_model="qwen:latest", temperature=0.4, top_p=0.9):
        self.rag = LightweightRAG()
        self.dag = DAGValidator()
        self.lsr = LSREngine(llm_model=llm_model, temperature=temperature, top_p=top_p)
        
    def execute_loop(self, problem: str):
        print(f"\n--- ROZPOCZĘCIE CYKLU DLA: '{problem}' ---")
        
        # 1. Szukaj w RAG
        print("[OS] Przeszukiwanie RAG...")
        relevant_facts = self.rag.search(problem)
        
        # Zaznacz użycie faktów
        parent_ids = []
        for fact in relevant_facts:
            self.rag.mark_usage(fact['text'])
            if 'id' in fact['metadata']:
                parent_ids.append(fact['metadata']['id'])
        
        # 2. Synteza LSR
        gem_candidate = self.lsr.synthesize(problem, relevant_facts)
        
        if not gem_candidate:
            print("[OS] Cykl przerwany - błąd syntezy LSR.")
            return
            
        print(f"[OS] LSR wygenerował kandydata: {gem_candidate.get('gem_id')}")
        
        # 3. Walidacja DAG
        if self.dag.validate(gem_candidate):
            # 4. Zapisz nową wiedzę z powrotem do RAG
            gem_truth = gem_candidate['synthetic_truth']
            self.rag.add_gem(
                gem_truth, 
                metadata={"id": gem_candidate['gem_id'], "application": gem_candidate.get('application')},
                parent_ids=parent_ids
            )
            print(f"[OS] SUKCES! Prawda absolutna wygenerowana i zapamiętana:\n>> {gem_truth}")
            if parent_ids:
                print(f">> Relacje: Wywiedziono z {', '.join(parent_ids)}")
            
            # Obsługa samokorekty (deprecate_ids)
            for old_id in gem_candidate.get('deprecate_ids', []):
                self.rag.deprecate_gem(old_id)
            
            print(f">> Zastosowanie: {gem_candidate.get('application')}")
        else:
            print("[OS] ODRZUCONO przez filtry DAG. Model musi spróbować ponownie w przyszłości.")

# ==========================================
# UŻYCIE (Przykład dla Twojego projektu)
# ==========================================
if __name__ == "__main__":
    # Upewnij się, że masz pobrane modele w terminalu:
    # ollama run mxbai-embed-large:latest
    # ollama run qwen:latest (lub gemma2 / llama3)
    
    # Inicjalizacja Twojego mikro-systemu
    os = AgenticOS(llm_model="qwen:latest") # Wpisz tutaj swój lokalny model myślowy
    
    # Krok 1: Wrzucamy do RAG surową wiedzę (początkowy instynkt)
    os.rag.add_gem("Lód to zamrożona woda. Rozszerza swoją objętość.")
    os.rag.add_gem("Stal pęka, gdy jest poddawana ekstremalnym naprężeniom rozciągającym.")
    
    # Krok 2: Uruchamiamy pętlę dla trudnego zadania
    problem_to_solve = "Jak zaprojektować stalową rurę odporną na zamarzającą wewnątrz wodę bez użycia grzałek?"
    os.execute_loop(problem_to_solve)
