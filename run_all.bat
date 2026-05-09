@echo off
echo Starting RunEV Backend (FastAPI)...
start "RunEV Backend" cmd /k ".venv\Scripts\python.exe -m uvicorn backend.api:app --host 127.0.0.1 --port 8000"

echo Starting RunEV User App (Streamlit)...
start "RunEV User App" cmd /k ".venv\Scripts\python.exe -m streamlit run user_app/app.py --server.port 8501 --server.headless true"

echo Starting RunEV Admin App (Streamlit)...
start "RunEV Admin App" cmd /k ".venv\Scripts\python.exe -m streamlit run admin_app/app.py --server.port 8502 --server.headless true"

echo All services are starting up!
echo - Backend: http://localhost:8000
echo - User App: http://localhost:8501
echo - Admin App: http://localhost:8502
