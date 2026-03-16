@echo off
title Gnosis LSR - Autonomiczna Ewolucja
cls
echo ==========================================
echo    GNOSIS LSR: AUTONOMOUS EVOLUTION
echo ==========================================
echo.
echo Sprawdzanie polaczenia z Ollama...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [BLAD] Ollama nie jest uruchomiona! Prosze uruchom Ollama i sprobuj ponownie.
    pause
    exit /b
)

echo [OK] Ollama wykryta. Uruchamianie interfejsu...
python synthetic_trainer.py
pause
