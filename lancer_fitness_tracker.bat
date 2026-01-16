@echo off
title Fitness Tracker

REM Change to the project directory
cd /d "c:\Users\Clement\.gemini\antigravity\playground\icy-interstellar\fitness-tracker"

REM Get IP Address
for /f "tokens=14" %%a in ('ipconfig ^| findstr IPv4') do set IP=%%a

REM Start the Django server
echo ========================================
echo    Demarrage de Fitness Tracker...
echo ========================================
echo.
echo ACCES PC (Local) :      http://127.0.0.1:8000
echo.
echo ACCES TABLETTE :        http://%IP%:8000
echo (Tapez cette adresse sur votre tablette connectee au meme Wi-Fi)
echo.
echo Appuyez sur Ctrl+C pour arreter le serveur.
echo ========================================
echo.

REM Open the browser
start "" timeout /t 2 /nobreak >nul && start http://127.0.0.1:8000

REM Run the server accessible from network
python manage.py runserver 0.0.0.0:8000
