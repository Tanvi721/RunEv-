@echo off
echo Stopping RunEV services on ports 8000, 8501, and 8502...

for /f "tokens=5" %%p in ('netstat -ano ^| findstr /R /C:":8000 .*LISTENING" /C:":8501 .*LISTENING" /C:":8502 .*LISTENING"') do (
    echo Stopping PID %%p
    taskkill /PID %%p /F
)

echo Done. You can run run_all.bat again.
