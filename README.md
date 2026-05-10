# RunEV

RunEV is an on-demand EV charging project with a FastAPI backend and two Streamlit clients:

- `user_app/` for customers requesting mobile charging.
- `admin_app/` for drivers/admin operations.
- `backend/` for API routes, database models, schemas, and services.

## Project Layout

```text
RUNEV/
  admin_app/       Streamlit driver/admin console
  backend/         FastAPI app, models, schemas, services
  frontend/        Shared Streamlit UI components and styles
  migrations/      Alembic database migrations
  tests/           Pytest test suite
  user_app/        Streamlit customer app
  utils/           Shared client/helper utilities
```

## Run Locally

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python init_db.py
.\run_all.bat
```

Backend: `http://localhost:8000`

User app: `http://localhost:8501`

Admin app: `http://localhost:8502`

## Tests

```powershell
.\.venv\Scripts\pytest -q
```
