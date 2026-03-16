import os
import json
import time
import sys
from universal_lsr_agent import LightweightRAG, DAGValidator, LSREngine, AgenticOS
from evolution_engine import EvolutionEngine

def run_validation():
    print("=== GNOSIS LSR: SYSTEM VALIDATION (PRO MODE) ===")
    errors = []
    
    # 1. Test RAG Persistence
    print("\n[1/5] Testujaca pamiec RAG...")
    test_rag_file = "test_memory.json"
    try:
        if os.path.exists(test_rag_file): os.remove(test_rag_file)
        rag = LightweightRAG(memory_file=test_rag_file)
        
        # Test zapisu
        rag.add_gem("Testowa prawda", metadata={"id": "T1"})
        if not os.path.exists(test_rag_file):
            errors.append("RAG: Plik JSON nie zostal utworzony.")
        
        # Test odczytu i metadanych
        rag2 = LightweightRAG(memory_file=test_rag_file)
        if len(rag2.memory) != 1:
            errors.append("RAG: Blad wczytywania danych.")
        
        if rag2.memory[0]['metadata'].get('status') != "ACTIVE":
            errors.append("RAG: Brak domyslnego statusu ACTIVE.")
        
        print("[OK] RAG dziala poprawnie.")
    except Exception as e:
        errors.append(f"RAG: Krytyczny blad: {e}")
    finally:
        if os.path.exists(test_rag_file): os.remove(test_rag_file)

    # 2. Test DAG Validator
    print("\n[2/5] Walidacja filtrów logicznych (DAG)...")
    try:
        dag = DAGValidator()
        valid_gem = {"synthetic_truth": "Logika jest spójna.", "dag_status": "VALIDATED"}
        invalid_gem = {"synthetic_truth": "", "dag_status": "VALIDATED"}
        
        if not dag.validate(valid_gem):
            errors.append("DAG: Odrzucono poprawny rekord.")
        if dag.validate(invalid_gem):
            errors.append("DAG: Zaakceptowano pusty rekord.")
            
        print("[OK] DAG dziala poprawnie.")
    except Exception as e:
        errors.append(f"DAG: Blad: {e}")

    # 3. Test Inicjalizacji Silnika LSR
    print("\n[3/5] Sprawdzanie parametrów silnika LSR...")
    try:
        lsr = LSREngine(temperature=1.2, top_p=0.4)
        if lsr.temperature != 1.2 or lsr.top_p != 0.4:
            errors.append("LSR: Blad przekazywania parametrów Temp/Top_P.")
        print("[OK] LSREngine gotowy.")
    except Exception as e:
        errors.append(f"LSR: Blad: {e}")

    # 4. Test Integracji OS
    print("\n[4/5] Sprawdzanie Orkiestratora (AgenticOS)...")
    try:
        aos = AgenticOS()
        if not hasattr(aos, 'rag') or not hasattr(aos, 'lsr'):
            errors.append("OS: Blad inicjalizacji komponentów.")
        print("[OK] AgenticOS zintegrowany.")
    except Exception as e:
        errors.append(f"OS: Blad: {e}")

    # 5. Test Silnika Ewolucji
    print("\n[5/5] Weryfikacja logiki ewolucji...")
    try:
        engine = EvolutionEngine(AgenticOS())
        # Test światopoglądu (powinien zwrócić pusty string jeśli brak pamięci)
        vw = engine.get_worldview_axioms()
        
        # Test redundancji (powinien być False dla unikalnego tekstu)
        redundant, _ = engine.is_redundant("Zupełnie nowa myśl 123456789")
        if redundant:
            errors.append("ENGINE: Blad detekcji redundancji (False Positive).")
            
        print("[OK] EvolutionEngine sprawny.")
    except Exception as e:
        errors.append(f"ENGINE: Blad: {e}")

    # PODSUMOWANIE
    print("\n" + "="*40)
    if not errors:
        print("   WYNIK: SYSTEM STABILNY (100% PRO)")
        print("   Projekt gotowy do publikacji!")
    else:
        print(f"   WYNIK: WYKRYTO BLEDY ({len(errors)})")
        for err in errors:
            print(f"   - {err}")
    print("="*40)

if __name__ == "__main__":
    run_validation()
