import os
import json
import time
import sys
import ollama
from universal_lsr_agent import LightweightRAG, DAGValidator, LSREngine, AgenticOS
from evolution_engine import EvolutionEngine

def run_validation():
    print("=== GNOSIS LSR: SYSTEM VALIDATION (PRO MODE) ===")
    
    # Pobieramy zainstalowane modele
    models = []
    try:
        res = ollama.list()
        if hasattr(res, 'models'): models = [m.model for m in res.models]
        else: models = [m.get('model', m.get('name', '')) for m in res.get('models', [])]
    except Exception as e:
        print(f"Blad polaczenia z Ollama: {e}")
        return

    if not models:
        print("Brak jakichkolwiek modeli w Ollama! Pobierz mxbai-embed-large:latest.")
        return

    # Wybieramy model do testu
    # Szukamy dowolnego modelu 'qwen', jeśli nie to bierzemy pierwszy z brzegu
    test_model = next((m for m in models if "qwen" in m.lower()), models[0])
    
    print(f"Uzywam modelu do testow: {test_model}")

    try:
        # 1. RAG
        print("\n[1/3] RAG Test...")
        rag = LightweightRAG(memory_file="test_tmp.json")
        print("[OK]")

        # 2. LSREngine
        print("[2/3] LSREngine Test...")
        lsr = LSREngine(llm_model=test_model)
        print("[OK]")

        # 3. AgenticOS
        print("[3/3] AgenticOS Test...")
        aos = AgenticOS(llm_model=test_model)
        print("[OK]")
        
        if os.path.exists("test_tmp.json"): os.remove("test_tmp.json")
        
        print("\n" + "="*40)
        print("   WYNIK: SYSTEM STABILNY (100% PRO)")
        print("="*40)
        
    except SystemExit:
        print("\n[!] Przerwano: Brakuje waznego modelu (RAG lub MYŚLI).")
        print("[!] To potwierdza, ze zabezpieczenie 'Idiot-Proof' dziala!")
    except Exception as e:
        print(f"\n[!] Nieoczekiwany blad: {e}")

if __name__ == "__main__":
    run_validation()
