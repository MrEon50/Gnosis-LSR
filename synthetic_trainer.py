import sys
import time
import ollama
import os
from evolution_engine import EvolutionEngine
from universal_lsr_agent import AgenticOS

class SyntheticTrainerCLI:
    def __init__(self):
        self.selected_model = None
        self.tempo_enabled = True
        self.cpm = 3000  # Znaków na minutę (Characters Per Minute)
        self.temperature = 1
        self.top_p = 0.6
        self.system_memory = [] # Tu w przyszłości podepniemy moduł RAG z poprzedniego skryptu

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_with_tempo(self, text: str):
        """Symuluje tempo pisania modelu."""
        if not self.tempo_enabled:
            print(text)
            return

        # 3000 znaków na minutę = 50 znaków na sekundę -> 0.02s na znak
        delay = 60.0 / self.cpm if self.cpm > 0 else 0
        
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            if delay > 0:
                time.sleep(delay)
        print() # Nowa linia na końcu

    def fetch_local_models(self):
        """Pobiera listę modeli zainstalowanych w Ollama."""
        try:
            response = ollama.list()
            # W nowszych wersjach 'ollama' zwraca obiekt z atrybutem 'models'
            if hasattr(response, 'models'):
                return [m.model for m in response.models]
            # Kompatybilność ze starszymi wersjami (słownik)
            models = response.get('models', [])
            return [m.get('model', m.get('name', 'Unknown')) for m in models]
        except Exception as e:
            print(f"[Błąd] Problem z pobraniem listy modeli Ollama: {e}")
            return []

    def menu_select_model(self):
        self.clear_screen()
        print("=== WYBÓR MODELU OLLAMA ===")
        models = self.fetch_local_models()
        
        if not models:
            input("\nNaciśnij Enter, aby wrócić...")
            return

        for i, model in enumerate(models, 1):
            print(f"{i}. {model}")
            
        try:
            choice = int(input("\nWybierz numer modelu: "))
            if 1 <= choice <= len(models):
                self.selected_model = models[choice-1]
                print(f"Ustawiono model: {self.selected_model}")
            else:
                print("Nieprawidłowy wybór.")
        except ValueError:
            print("To nie jest liczba.")
        
        time.sleep(1)

    def menu_settings(self):
        while True:
            self.clear_screen()
            print("=== USTAWIENIA ===")
            print(f"1. Tempo pisania: {'[WŁĄCZONE]' if self.tempo_enabled else '[WYŁĄCZONE]'}")
            print(f"2. Prędkość (CPM): {self.cpm} znaków/minutę")
            print(f"3. Temperatura: {self.temperature}")
            print(f"4. Top_P: {self.top_p}")
            print("5. Powrót do menu")
            
            choice = input("\nWybierz opcję: ")
            
            if choice == '1':
                self.tempo_enabled = not self.tempo_enabled
            elif choice == '2':
                try:
                    new_cpm = int(input("Podaj nową wartość (np. 60-4000): "))
                    if new_cpm > 0:
                        self.cpm = new_cpm
                except ValueError:
                    pass
            elif choice == '3':
                try:
                    new_temp = float(input("Podaj temperaturę (np. 0.1 - 1.0): "))
                    self.temperature = new_temp
                except ValueError:
                    pass
            elif choice == '4':
                try:
                    new_top_p = float(input("Podaj Top_P (np. 0.1 - 1.0): "))
                    self.top_p = new_top_p
                except ValueError:
                    pass
            elif choice == '5':
                break

    def chat_interface(self):
        if not self.selected_model:
            print("Najpierw wybierz model z menu!")
            time.sleep(1.5)
            return

        self.clear_screen()
        print(f"=== TRYB TRENINGU (Model: {self.selected_model}) ===")
        print("Komendy: '/menu' - wyjście, '/tempo <liczba>' - zmiana prędkości.")
        print("-" * 50)

        # Inicjalizacja OS dla dostępu do RAG
        agent_os = AgenticOS(
            llm_model=self.selected_model, 
            temperature=self.temperature, 
            top_p=self.top_p
        )
        
        # Historia rozmowy
        messages = [{"role": "system", "content": "Jesteś analitycznym agentem LSR. Korzystasz z własnej bazy wiedzy (RAG), aby odpowiadać spójnie ze swoim wypracowanym światopoglądem."}]

        while True:
            try:
                user_input = input("\nTy: ").strip()
            except (KeyboardInterrupt, EOFError):
                break

            if not user_input:
                continue

            # Obsługa komend wewnątrz czatu
            if user_input.lower() == '/menu':
                break
            elif user_input.lower().startswith('/tempo'):
                parts = user_input.split()
                if len(parts) == 2 and parts[1].isdigit():
                    self.cpm = int(parts[1])
                    print(f"[System] Zmieniono tempo na {self.cpm} CPM.")
                else:
                    print("[System] Użycie: /tempo <liczba>")
                continue

            # 1. Przeszukiwanie RAG dla kontekstu
            relevant_gems = agent_os.rag.search(user_input, top_k=3)
            context_block = ""
            if relevant_gems:
                context_block = "\n\n[KONTEKST Z TWOJEJ PAMIĘCI RAG]:\n"
                for gem in relevant_gems:
                    context_block += f"- {gem['text']}\n"
                    # Opcjonalnie: odznaczamy użycie
                    agent_os.rag.mark_usage(gem['text'])

            # 2. Budowanie promptu z kontekstem
            full_user_input = user_input + context_block
            messages.append({"role": "user", "content": full_user_input})

            # Generowanie odpowiedzi przez Ollama
            sys.stdout.write("AI: ")
            sys.stdout.flush()
            
            try:
                # Pobieramy pełną odpowiedź
                response = ollama.chat(
                    model=self.selected_model, 
                    messages=messages,
                    options={
                        "temperature": self.temperature,
                        "top_p": self.top_p
                    }
                )
                
                # Obsługa zarówno obiektów jak i słowników
                if hasattr(response, 'message'):
                    ai_reply = response.message.content
                else:
                    ai_reply = response['message']['content']
                
                self.print_with_tempo(ai_reply)
                
                # Zapisujemy odpowiedź AI do historii, by model pamiętał wątek
                messages.append({"role": "assistant", "content": ai_reply})
                
                # TUTAJ MOŻEMY DODAĆ LOGIKĘ: 
                # Jeśli ai_reply zawiera nową, cenną zasadę, wyślij ją do RAG (LightweightRAG z poprzedniego kodu)!
                
            except Exception as e:
                print(f"\n[Błąd generowania odpowiedzi]: {e}")

    def run_evolution_monitor(self):
        """Uruchamia podgląd ewolucji."""
        if not self.selected_model:
            print("Najpierw wybierz model z menu!")
            time.sleep(1.5)
            return

        self.clear_screen()
        print(f"=== MONITOR EWOLUCJI LSR (Model: {self.selected_model}) ===")
        print("Model będzie teraz samodzielnie generował 'Perełki' wiedzy.")
        print("Naciśnij Ctrl+C, aby przerwać i wrócić do menu.")
        print("-" * 50)
        print(f"PARAMETRY: Temp={self.temperature}, Top_P={self.top_p}")
        print("-" * 50)
        
        agent_os = AgenticOS(
            llm_model=self.selected_model, 
            temperature=self.temperature, 
            top_p=self.top_p
        )
        engine = EvolutionEngine(agent_os)
        engine.start(interval_seconds=30)
        
        input("\nEwolucja zatrzymana. Naciśnij Enter, aby kontynuować...")

    def show_stats(self):
        """Pokazuje statystyki wiedzy."""
        agent_os = AgenticOS(llm_model=self.selected_model) if self.selected_model else AgenticOS()
        self.clear_screen()
        print("=== STATYSTYKI ŚWIATOPOGLĄDU LSR ===")
        
        # Debugowanie zawartości pamięci
        raw_count = len(agent_os.rag.memory)
        
        if raw_count == 0:
            print("Pamięć RAG jest całkowicie pusta.")
            print("Wskazówka: Uruchom 'Monitor ewolucji', aby model wygenerował pierwsze Perełki.")
        else:
            # Upewniamy się, że każda perełka ma pole status i id
            active = []
            deprecated = []
            for m in agent_os.rag.memory:
                meta = m.get('metadata', {})
                if meta.get('status') == 'DEPRECATED':
                    deprecated.append(m)
                else:
                    active.append(m)
            
            print(f"Całkowita liczba rekordów: {raw_count}")
            print(f"Aktywne Perełki: {len(active)}")
            print(f"Przestarzałe Perełki: {len(deprecated)}")
            print("-" * 30)
            
            # Top 5 aksjomatów
            sorted_m = sorted(active, key=lambda x: x.get('metadata', {}).get('usage_count', 0), reverse=True)
            print("TOP 5 AKSJOMATÓW (Najczęściej używane):")
            for m in sorted_m[:5]:
                meta = m.get('metadata', {})
                print(f"- [{meta.get('id', 'Brak ID')}] Użyć: {meta.get('usage_count', 0)} | {m['text'][:60]}...")
        
        input("\nNaciśnij Enter, aby powrócić do menu...")

    def run(self):
        while True:
            self.clear_screen()
            print("=========================================")
            print("   GNOSIS LSR - GŁÓWNE MENU   ")
            print("=========================================")
            print(f"Aktywny model: {self.selected_model or 'BRAK'}")
            print("-----------------------------------------")
            print("1. Wybierz model Ollama")
            print("2. Ustawienia")
            print("3. Uruchom Czat (Dotrenowywanie)")
            print("4. Monitor ewolucji (Auto-rozrost)")
            print("5. Statystyki wiedzy (Światopogląd)")
            print("6. Wyjście")
            print("=========================================")
            
            choice = input("Wybierz opcję (1-6): ")
            
            if choice == '1':
                self.menu_select_model()
            elif choice == '2':
                self.menu_settings()
            elif choice == '3':
                self.chat_interface()
            elif choice == '4':
                self.run_evolution_monitor()
            elif choice == '5':
                self.show_stats()
            elif choice == '6':
                self.clear_screen()
                print("Zamykanie środowiska treningowego...")
                break
            else:
                print("Nieprawidłowy wybór.")
                time.sleep(1)

if __name__ == "__main__":
    app = SyntheticTrainerCLI()
    app.run()