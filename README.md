# 💎 Gnosis LSR (Loop Synthetic Reasoning)

**Gnosis LSR** to minimalistyczna, ale potężna architektura autonomicznej ewolucji dla lokalnych modeli językowych (Ollama). System ten nie tylko rozmawia z użytkownikiem, ale posiada własną "sferę introspekcji", w której samodzielnie generuje, waliduje i szlifuje wiedzę, tworząc spójny światopogląd.

## 🚀 Kluczowe Funkcje

- **Autonomiczna Ewolucja:** Silnik, który w tle generuje hipotezy, zderza je z istniejącą wiedzą i wyciąga nowe wnioski.
- **LSR Engine (Hidden Space Synthesis):** Proces syntezy prawdy absolutnej w "przestrzeni ukrytej", oddzielony od standardowej rozmowy.
- **Neuro-Symboliczna Walidacja (DAG):** Każdy wniosek musi przejść przez rygorystyczne filtry spójności logicznej.
- **Pamięć Światopoglądowa (RAG):** Trwałe zapisywanie wiedzy w formie "Perełek" (Gems) z pełnym rodowodem (Lineage) i rankingiem witalności.
- **Samokorekta (Self-Correction):** Zdolność modelu do unieważniania starszych, błędnych faktów na rzecz nowo odkrytych "Wyższych Prawd".

## 🛠️ Architektura

Projekt składa się z trzech core-modułów:
1.  `universal_lsr_agent.py`: Rdzeń systemu (RAG, DAG, LSR).
2.  `evolution_engine.py`: Silnik auto-rozwoju i blokada powtórzeń (Anti-Syzyf).
3.  `synthetic_trainer.py`: Zaawansowany CLI do monitoringu, czatu i zarządzania parametrami.

## 📦 Instalacja i Uruchomienie

1.  Upewnij się, że masz zainstalowaną **Ollama**.
2.  Pobierz wymagane modele (rekomendowane):
    ```bash
    ollama pull mxbai-embed-large:latest  # WYMAGANY (do pamięci RAG)
    ollama pull qwen2.5:7b                # Lub qwen3.5:9b / llama3 (do myślenia)
    ```
3.  Uruchom system za pomocą pliku:
    `start_gnosis_lsr.bat` lub `python synthetic_trainer.py`

## 💎 Koncepcja "Perełek" (Gems)

W Gnosis LSR wiedza nie jest stosem danych. Jest konstelacją Perełek. Każda posiada:
- **Synthetic Truth:** Esencję wypracowanego wniosku.
- **Lineage:** Informację, z jakich wcześniejszych faktów została wywiedziona.
- **Vitality:** Licznik użycia – Perełki najczęściej używane stają się **Aksjomatami** Twojego modelu.

---
*Projekt stworzony z myślą o badaniu granic autonomii modeli AI w środowisku lokalnym.*
