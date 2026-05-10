@echo off
setlocal

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_CMD=.venv\Scripts\python.exe"
) else (
    set "PYTHON_CMD=python"
)

echo Using Python: %PYTHON_CMD%
set "RUNEV_API_BASE_URL=http://127.0.0.1:8000"

echo Initializing database if needed...
%PYTHON_CMD% init_db.py
if errorlevel 1 (
    echo.
    echo Failed to initialize the database.
    echo Install dependencies first with: python -m pip install -r requirements.txt
    pause
    exit /b 1
)

echo Starting RunEV Backend (FastAPI)...
start "RunEV Backend" cmd /k "%PYTHON_CMD% -m uvicorn backend.api:app --host 127.0.0.1 --port 8000"

echo Starting RunEV User App (Streamlit)...
start "RunEV User App" cmd /k "%PYTHON_CMD% -m streamlit run user_app/app.py --server.port 8501 --server.headless true"

echo Starting RunEV Admin App (Streamlit)...
start "RunEV Admin App" cmd /k "%PYTHON_CMD% -m streamlit run admin_app/app.py --server.port 8502 --server.headless true"

echo All services are starting up!
echo - Backend: http://localhost:8000
echo - User App: http://localhost:8501
echo - Admin App: http://localhost:8502
