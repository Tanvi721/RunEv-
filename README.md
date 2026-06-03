# ⚡ RunEV - On-Demand EV Charging Platform

<div align="center">

![RunEV Banner](https://img.shields.io/badge/RunEV-Mobile%20EV%20Charging-blueviolet?style=for-the-badge)

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-User%20%2B%20Driver%20Apps-ff4b4b?style=flat-square)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-bb2222?style=flat-square)
![Supabase](https://img.shields.io/badge/Supabase-Auth-3ECF8E?style=flat-square)
![Razorpay](https://img.shields.io/badge/Razorpay-Payments-02042B?style=flat-square)
![Pytest](https://img.shields.io/badge/Pytest-Tested-0A9EDC?style=flat-square)

### 🚐 Smart mobile EV charging with live dispatch, trip tracking, OTP verification, billing, payments, ratings, and analytics.

</div>

---

## 🌟 Overview

RunEV is a full-stack platform for mobile EV charging services. Customers can request a charging van at their live location, track the driver, complete payment, download an invoice, and rate the service. Drivers and admins can manage fleet profiles, accept trips, verify trip OTPs, update charging progress, generate bills, and monitor operations.

The project is built with FastAPI, Streamlit, SQLAlchemy, Alembic, Supabase integration, Razorpay-ready payments, JWT authentication, live geolocation, custom Streamlit UI components, and Pytest coverage.

---

## ✨ Current Project Highlights

- 🚀 FastAPI backend mounted under `/api/v1`.
- 👤 Customer app entry point: `user_app/app.py`.
- 🛠️ Driver/admin console entry point: `admin_app/app.py`.
- 🗄️ SQLite local database with PostgreSQL production support.
- 🔐 JWT login, email/password auth, phone OTP, email OTP, Supabase session login, profile updates, and saved preferences.
- 📍 Live browser geolocation for customer pickup and driver van location.
- 🚐 Provider fleet profiles with vehicle number, connector type, charging speed, driver phone, image, price per kWh, and availability.
- 🔄 Dispatch lifecycle from request creation to payment completion.
- 🔢 Trip OTP verification before charging starts.
- 💰 Fare calculation with base fee, distance fee, charging rate, platform fee, emergency fee, and night fee support.
- 💳 Razorpay order and verification path with local/demo fallback behavior.
- 📲 UPI QR and cash payment flows.
- ⭐ Ratings for completed charging sessions.
- 📊 Customer and fleet analytics dashboards.
- ✅ Alembic migrations and focused automated tests.

---

## 🎯 Features

### 👥 Customer App

- 🔐 Register and log in with email/password.
- 📱 Login with phone OTP or email OTP.
- 🟢 Supabase session login support.
- 💾 Persistent JWT session in browser storage.
- 📍 Live pickup location capture.
- 🚐 Nearby charging van discovery.
- ⚡ Charging request creation.
- 🧭 Live trip status timeline.
- 🗺️ Route map, ETA, driver details, and vehicle details.
- 🔢 Trip OTP display for driver verification.
- 🧾 Pending bill and payment screen.
- 💳 UPI QR, cash confirmation, and Razorpay checkout path.
- 📄 Invoice download after payment.
- ⭐ Charging history and session rating.
- 🎨 Account settings and theme preferences.

### 🧑‍✈️ Driver/Admin Console

- 🔐 Driver/admin login and persistent session.
- 🚐 Charging van profile creation and editing.
- 📍 Live driver/van location capture.
- 🪪 Driver details, mobile number, connector type, charging speed, and pricing controls.
- 🖼️ Vehicle image upload support.
- 🟢 Availability management.
- 📥 Pending request queue.
- ✅ Trip accept, reject, arrived, OTP verify, start charging, complete charging, and bill generation actions.
- 🗺️ Live route map for active trips.
- 📊 Earnings, payments, trip history, ratings, and fleet analytics.
- 💰 Admin pricing controls for platform-wide fare settings.
- 🎨 Theme and dashboard appearance preferences.

### ⚙️ Backend

- 🚀 REST API with FastAPI.
- 🧩 Versioned API routes.
- 🗄️ SQLAlchemy models and service layer.
- 🔁 Alembic migrations.
- 🔐 JWT-protected endpoints.
- 🧪 Password, phone, vehicle, coordinate, and upload validation.
- 🔢 OTP request and verification services.
- 🟢 Supabase auth handoff.
- 💰 Pricing and dispatch services.
- 💳 Payment gateway abstraction.
- ⭐ Ratings and tracking APIs.
- 🔴 Websocket router for tracking support.
- ✅ Pytest coverage for auth, payments, ratings, OTP, and core services.

---

## 🧰 Tech Stack

| Technology | Usage |
| --- | --- |
| Python 3.11 | Main language |
| FastAPI | Backend API |
| Uvicorn | ASGI server |
| Streamlit | Customer app and driver/admin console |
| SQLAlchemy | ORM and database models |
| SQLite | Local development database |
| PostgreSQL | Production database option |
| Alembic | Database migrations |
| Supabase | External auth/session integration |
| JWT | API session authentication |
| Twilio Verify | Phone OTP provider option |
| SMTP | Email OTP delivery option |
| Razorpay | Payment order and verification integration |
| Folium / streamlit-folium | Maps |
| Plotly | Analytics charts |
| Pytest / HTTPX | Automated tests |

---

## 📁 Project Structure

```text
RUNEV/
|-- admin_app/
|   `-- app.py
|-- backend/
|   |-- api/
|   |   |-- auth.py
|   |   `-- v1/
|   |       |-- auth.py
|   |       |-- payments.py
|   |       |-- pricing.py
|   |       |-- providers.py
|   |       |-- ratings.py
|   |       |-- requests.py
|   |       `-- tracking.py
|   |-- core/
|   |   |-- security.py
|   |   `-- validation.py
|   |-- schemas/
|   |-- services/
|   |-- database.py
|   |-- main.py
|   `-- models.py
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
|   |   `-- ui.py
|   |-- styles/
|   |   |-- premium_user.css
|   |   `-- theme.py
|   `-- utils/
|       |-- live.py
|       `-- supabase_auth.py
|-- migrations/
|   |-- versions/
|   |   |-- 0001_initial_schema.py
|   |   |-- 0002_add_ratings.py
|   |   |-- 0003_add_request_otp.py
|   |   `-- 0004_add_user_preferences.py
|   `-- 20260601_auth_security_upgrade.sql
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
|-- .env.example
|-- Dockerfile
|-- init_db.py
|-- requirements.txt
|-- run_all.bat
|-- run_silently.vbs
`-- stop_all.bat
```

Local and generated files such as `.env`, `.git/`, `.pytest_cache/`, `.run_logs/`, `__pycache__/`, and `runev.db` are intentionally excluded from the tree above.

---

## ⚙️ Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/Tanvi721/RunEv-.git
cd RunEv-
```

### 2️⃣ Create Virtual Environment

```powershell
python -m venv venv
venv\Scripts\activate
```

Linux / macOS:

```bash
python -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4️⃣ Configure Environment

```powershell
copy .env.example .env
```

Update `.env` with your local or production values.

```env
DATABASE_URL=sqlite:///./runev.db
JWT_SECRET=super_secret_jwt_key_change_in_production
RUNEV_API_BASE_URL=http://127.0.0.1:8000
RUNEV_USER_APP_URL=http://localhost:8501

SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key

PHONE_OTP_PROVIDER=twilio
DEFAULT_PHONE_COUNTRY_CODE=+91
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_VERIFY_SERVICE_SID=VAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_VERIFY_CHANNEL=sms

EMAIL_OTP_PROVIDER=smtp
EMAIL_OTP_TTL_SECONDS=300
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
SMTP_FROM=your_email@gmail.com
SMTP_USE_TLS=true

RAZORPAY_KEY_ID=rzp_test_yourkeyid
RAZORPAY_KEY_SECRET=your_razorpay_secret
```

### 5️⃣ Initialize Database

Quick SQLite setup:

```powershell
python init_db.py
```

Alembic migration setup:

```powershell
alembic upgrade head
```

---

## ▶️ Run Locally

### 🚀 Start Backend

```powershell
uvicorn backend.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

### 👤 Start Customer App

```powershell
streamlit run user_app/app.py
```

Customer app:

```text
http://localhost:8501
```

### 🧑‍✈️ Start Driver/Admin Console

```powershell
streamlit run admin_app/app.py --server.port 8502
```

Driver/admin console:

```text
http://localhost:8502
```

Windows helpers:

```powershell
run_all.bat
stop_all.bat
```

---

## 🔌 API Overview

| Area | Routes |
| --- | --- |
| Health | `GET /` |
| Auth | `/api/v1/auth/*` |
| Requests | `/api/v1/requests/*` |
| Providers | `/api/v1/providers/*` |
| Payments | `/api/v1/payments/*` |
| Pricing | `/api/v1/pricing/*` |
| Ratings | `/api/v1/ratings/*` |
| Tracking | `/api/v1/tracking/*` |

For exact schemas, see `backend/schemas/`. For route behavior, see `backend/api/v1/`.

---

## 🧪 Testing

Run the full test suite:

```powershell
pytest
```

Run one test file:

```powershell
pytest tests/test_payment_gateway.py
```

Current test coverage includes:

- 🔐 Auth login options and OTP flows.
- ⚙️ Core service behavior.
- 💳 Payment gateway behavior.
- ⭐ Ratings API behavior.
- 🔢 Request OTP API behavior.

---

## 🌐 Deployment

### 🚀 Backend

Example production command:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 10000
```

Production checklist:

- 🗄️ Use PostgreSQL through `DATABASE_URL`.
- 🔐 Set a strong `JWT_SECRET`.
- 🟢 Configure Supabase redirect URLs.
- 📱 Configure Twilio Verify for phone OTP.
- 📧 Configure SMTP for email OTP.
- 💳 Configure Razorpay test or live credentials.
- 🔁 Run Alembic migrations.
- 🙈 Keep `.env` and secrets out of git.

### 🎨 Streamlit Apps

Deploy the two apps as separate services when possible:

- Customer app: `user_app/app.py`
- Driver/admin console: `admin_app/app.py`

Set `RUNEV_API_BASE_URL` to the deployed backend URL.

---

## 🛠️ Development Notes

- 🚀 `backend/main.py` creates the FastAPI app and mounts all routers.
- 🔌 `utils/api_client.py` centralizes Streamlit-to-backend calls.
- 🧩 `frontend/components/` stores shared UI, payment, auth, maps, analytics, and geolocation helpers.
- 🎨 `frontend/styles/theme.py` and `frontend/styles/premium_user.css` define the app styling.
- 🧪 `backend/core/validation.py` contains input validation and normalization.
- 💰 `backend/services/pricing_service.py` handles fare calculation.
- 🔄 `backend/services/dispatch_service.py` handles trip status behavior.
- 💳 `backend/services/payment_gateway.py` handles Razorpay/mock payment behavior.

---

## 🚀 Future Improvements

- 🔴 Production websocket trip updates in the Streamlit apps.
- 💳 Payment webhook handling.
- 🔔 Push notifications.
- 🛡️ Stronger role-based admin controls.
- 🧠 Driver ETA prediction.
- 📈 Demand forecasting and charging intelligence.
- ✅ More end-to-end request-to-payment tests.
- 📱 Mobile-first deployment polish.

---

## 👩‍💻 Author

### Tanvi Barve

MCA Student • Python Developer • AI and Full Stack Enthusiast

GitHub: https://github.com/Tanvi721

---

## 📜 License

This project is licensed under the MIT License.

---

<div align="center">

## ⚡ RunEV - Charging the Future Anywhere

</div>
