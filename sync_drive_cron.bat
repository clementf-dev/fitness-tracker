@echo off
cd /d "C:\Users\Clement\.gemini\antigravity\playground\icy-interstellar\fitness-tracker"

echo [%date% %time%] Starting scheduled sync... >> sync_log.txt
python manage.py sync_drive >> sync_log.txt 2>&1
echo [%date% %time%] Sync finished with exit code %errorlevel% >> sync_log.txt
echo ---------------------------------------- >> sync_log.txt
