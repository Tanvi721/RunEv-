# RunEV - On-Demand EV Charging Platform

<div align="center">

![RunEV Banner](https://img.shields.io/badge/RunEV-EV%20Charging-blueviolet?style=for-the-badge)

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red?style=flat-square)
![Supabase](https://img.shields.io/badge/Supabase-Database-3ECF8E?style=flat-square)
![Razorpay](https://img.shields.io/badge/Razorpay-Payments-02042B?style=flat-square)

### Smart mobile EV charging platform with real-time tracking, online payments, and driver dispatch.

</div>

---

# Overview

RunEV is a full-stack EV charging service platform where users can request mobile EV charging, track charging vans live, make online payments, get charging support at their location, connect with charging providers, and view charging status in real time.

The project is built with FastAPI, Streamlit, SQLAlchemy, Supabase integrations, Razorpay payments, JWT authentication, Alembic migrations, and Pytest tests.

---

# Features

## User Features

- User authentication with JWT
- Login, signup, and account recovery flows
- Mobile EV charging requests
- Live charging status
- Payment integration
- User dashboard and history
- Real-time trip updates

## Provider Features

- Provider login and fleet registration
- Charging request acceptance and rejection
- Vehicle and driver management
- Dispatch workflow
- Driver location tracking
- Billing and trip status updates

## Payment Features

- Razorpay order creation and verification
- UPI and cash payment flows
- Payment status tracking
- Invoice-style summaries

## Backend Features

- REST API with FastAPI
- JWT authentication
- SQLAlchemy models and migrations
- Versioned API routes
- Modular services and schemas
- Focused test coverage for auth, payments, ratings, and OTP flows

---

# Tech Stack

| Technology | Usage |
|---|---|
| FastAPI | Backend framework |
| Streamlit | User and driver apps |
| SQLAlchemy | ORM |
| Alembic | Database migrations |
| Supabase | External auth/database integration |
| Razorpay | Payments |
| JWT | Session authentication |
| Pytest | Automated tests |
| Render / Fly.io | Deployment targets |

---
# Project Structure

```text
RUNEV/
|-- admin_app/
|   `-- app.py
|-- backend/
|   |-- api/
|   |   |-- v1/
|   |   |   |-- auth.py
|   |   |   |-- payments.py
|   |   |   |-- pricing.py
|   |   |   |-- providers.py
|   |   |   |-- ratings.py
|   |   |   |-- requests.py
|   |   |   |-- tracking.py
|   |   |   `-- __init__.py
|   |   |-- auth.py
|   |   `-- __init__.py
|   |-- core/
|   |   |-- security.py
|   |   |-- validation.py
|   |   `-- __init__.py
|   |-- schemas/
|   |   |-- auth.py
|   |   |-- payment.py
|   |   |-- pricing.py
|   |   |-- provider.py
|   |   |-- rating.py
|   |   |-- service_request.py
|   |   |-- tracking.py
|   |   `-- __init__.py
|   |-- services/
|   |   |-- auth_service.py
|   |   |-- booking_service.py
|   |   |-- dispatch_service.py
|   |   |-- geo_service.py
|   |   |-- payment_gateway.py
|   |   |-- payment_service.py
|   |   |-- pricing_service.py
|   |   |-- realtime_service.py
|   |   |-- recommendation_service.py
|   |   `-- station_service.py
|   |-- database.py
|   |-- main.py
|   |-- models.py
|   |-- requirements.txt
|   `-- runtime.txt
|-- frontend/
|   |-- components/
|   |   |-- geolocation_component/
|   |   |   `-- index.html
|   |   |-- analytics.py
|   |   |-- auth.py
|   |   |-- geolocation.py
|   |   |-- maps.py
|   |   |-- payment.py
|   |   |-- theme.py
|   |   |-- ui.py
|   |   `-- __init__.py
|   |-- styles/
|   |   |-- theme.py
|   |   `-- __init__.py
|   |-- utils/
|   |   |-- live.py
|   |   |-- supabase_auth.py
|   |   `-- __init__.py
|   `-- __init__.py
|-- migrations/
|   |-- versions/
|   |   |-- 0001_initial_schema.py
|   |   |-- 0002_add_ratings.py
|   |   |-- 0003_add_request_otp.py
|   |   `-- 0004_add_user_preferences.py
|   |-- 20260601_auth_security_upgrade.sql
|   |-- env.py
|   `-- script.py.mako
|-- tests/
|   |-- test_auth_login_options.py
|   |-- test_core_services.py
|   |-- test_payment_gateway.py
|   |-- test_ratings_api.py
|   `-- test_request_otp_api.py
|-- user_app/
|   `-- app.py
|-- utils/
|   |-- api_client.py
|   |-- distance.py
|   `-- otp.py
|-- .dockerignore
|-- .env.example
|-- .gitignore
|-- alembic.ini
|-- Dockerfile
|-- init_db.py
|-- PRODUCTION_NEXT_STEPS.md
|-- pytest.ini
|-- README.md
|-- requirements.txt
|-- runtime.txt
|-- run_all.bat
`-- stop_all.bat
```

Local-only and generated folders such as `.git/`, `.pytest_cache/`, `.run_logs/`, `__pycache__/`, `.env`, and `runev.db` are intentionally excluded from the tree above.

---

# ⚙️ Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/Tanvi721/RunEv-.git
cd RunEv-
```

---

# 🔧 Backend Setup

## Create Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r backend/requirements.txt
```

---

# 🗄️ Database Setup

Create `.env` file inside backend folder:

```env
DATABASE_URL=postgresql://postgres:PASSWORD@HOST:5432/postgres

JWT_SECRET=your_secret_key

RAZORPAY_KEY_ID=your_key

RAZORPAY_KEY_SECRET=your_secret

# Real-time phone OTP with Twilio Verify
PHONE_OTP_PROVIDER=twilio
DEFAULT_PHONE_COUNTRY_CODE=+91
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_VERIFY_SERVICE_SID=VAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_VERIFY_CHANNEL=sms
```

---

# ▶️ Run Backend

```bash
cd backend
uvicorn main:app --reload
```

Backend will run at:

```bash
http://127.0.0.1:8000
```

---

# 🎨 Frontend Setup

## Install Frontend Dependencies

```bash
pip install -r requirements.txt
```

---

## Run Streamlit App

```bash
streamlit run streamlit_app.py
```

Frontend will run at:

```bash
http://localhost:8501
```

---

# 🌐 Deployment

## Backend Deployment (Render / Fly.io)

### Start Command

```bash
uvicorn main:app --host 0.0.0.0 --port 10000
```

### Python Version

```txt
python-3.11.9
```

---

## Frontend Deployment (Streamlit Cloud)

Update API URL:

```python
API_BASE_URL = "https://your-backend-url.onrender.com"
```

Deploy using:

- Streamlit Community Cloud

---

# 🔐 Authentication APIs

## Register

```http
POST /register
```

## Login

```http
POST /login
```

## Current User

```http
GET /me
```

---

# 💳 Payment APIs

- Create Payment Order
- Verify Payment
- UPI Integration
- Razorpay Checkout

---

# 📸 Screenshots

## User Dashboard

- Modern dark UI
- EV request flow
- Real-time tracking

## Provider Console

- Charging dispatch management
- Request handling
- Live status updates

---

# 🚀 Future Improvements

- AI-based charging prediction
- Google Maps integration
- Driver ETA prediction
- Push notifications
- Multi-provider system
- Advanced analytics dashboard

---

# 👩💻 Author

## Tanvi Barve

MCA Student • Python Developer • AI & Full Stack Enthusiast

GitHub:

https://github.com/Tanvi721

---

# ⭐ Support

If you like this project:

- ⭐ Star the repository
- 🍴 Fork the project
- 🚀 Contribute improvements

---

# 📜 License

This project is licensed under the MIT License.

---

<div align="center">

## ⚡ RunEV — Charging the Future Anywhere

</div>
