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
# 📖 Overview
# Overview
**RunEV** is a full-stack, on-demand mobile EV charging service platform. It enables EV owners to request mobile charging vehicles directly to their live locations, track vans in real time, make secure online payments, and rate their experience.
RunEV is a full-stack EV charging service platform where users can request mobile EV charging, track charging vans live, make online payments, get charging support at their location, connect with charging providers, and view charging status in real time.
The platform provides a comprehensive ecosystem consisting of a **FastAPI backend REST & WebSocket API**, a **Streamlit User Application**, and a **Streamlit Fleet & Driver Management Console**.
The project is built with FastAPI, Streamlit, SQLAlchemy, Supabase integrations, Razorpay payments, JWT authentication, Alembic migrations, and Pytest tests.
---
# 🚀 Core Features
# Features
### 1. User Application (`user_app/app.py`)
*   **JWT & OAuth Session Management**: Secure user registration, authentication, password recovery, and integration with Supabase PKCE login.
*   **Live Pickup Capture**: Real-time geolocation detection using browser GPS, with automated address resolution via OpenStreetMap Nominatim Reverse Geocoding.
*   **Van Finder & ETA Estimation**: Dynamic matching against available dispatch vans, computing physical distances (Haversine formula), and estimating ETAs.
*   **Live Tracking Route Map**: Visualizes the van en route and charging progress using interactive maps.
*   **Secure Payments Checkout**: Seamlessly handles card, UPI, net banking, or cash payment selections. Integrates the Razorpay SDK to load a checkout window directly in the app.
*   **Rating & Feedbacks**: Supports submitting star ratings and text reviews for completed trips, updating driver averages.
## User Features
### 2. Fleet & Driver Console (`admin_app/app.py`)
*   **Operations KPI Dashboard**: Real-time metrics overview (revenue, active drivers, current live requests, SLA).
*   **Interactive Dispatch Controls**: Allows drivers to see pending requests, accept or reject bookings, view customer contact numbers, update trip progress (Accepted -> En Route -> Arrived -> Charging -> Completed), and update locations.
*   **OTP Verification**: Trip verification requiring the driver to input the customer's secure OTP code before charging can start.
*   **Charging Details Recorder**: Allows entry of energy delivered (kWh), and logs emergency/night service fees.
*   **Admin Pricing Controls**: Interface for administrators to update base visit fees, distance pricing rates, charging rates, platform charges, and fee caps directly in the database.
*   **Theme and Branding Customizer**: Allows tweaking brand colors, card shapes, dashboard density, and toggling dark/light modes.
- User authentication with JWT
- Login, signup, and account recovery flows
- Mobile EV charging requests
- Live charging status
- Payment integration
- User dashboard and history
- Real-time trip updates
### 3. High-Performance API Backend (`backend/`)
*   **Unified Route Directory**: Multi-version routing structure (`/api/v1` and compatibility `/api` fallbacks).
*   **WebSockets Channel**: Live WebSocket channels for real-time provider location pushes and request status tracking.
*   **Robust ORM Layer**: Database orchestration powered by SQLAlchemy with SQLite (`runev.db`) storage.
*   **Alembic Migrations**: Fully versioned schema migrations mapping database schema updates.
*   **Automated Security Protocols**: Security features such as tracking login failures, locking accounts on multiple failed attempts, and keeping audit logs.
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
# ⚙️ Tech Stack
# Tech Stack
|
 Component 
|
 Technology 
|
 Usage / Implementation 
|
|
---
|
---
|
---
|
|
**
Backend
**
|
 FastAPI 
|
 Async RESTful routes, health checks, and WebSocket channels 
|
|
**
User Web UI
**
|
 Streamlit 
|
 Responsive dashboard, leaflet maps, custom styling 
|
|
**
Fleet Admin UI
**
|
 Streamlit 
|
 Analytics charts, fleet lists, pricing management forms 
|
|
**
Authentication
**
|
 JWT & Supabase 
|
 Custom email/phone OTP generation, password reset, Supabase OAuth 
|
|
**
Database
**
|
 SQLite & SQLAlchemy 
|
 ORM models, relations, index structures, constraints 
|
|
**
Migrations
**
|
 Alembic 
|
 Database versions tracking and schema updates 
|
|
**
Payments
**
|
 Razorpay SDK 
|
 Embedded checkouts, orders, verification APIs, and webhooks 
|
|
**
Mapping
**
|
 Folium / HTML5 
|
 Custom map overlays and real-time reverse geocoding 
|
|
**
Testing
**
|
 Pytest 
|
 Fast API tests, mock gateways, auth routines 
|
|
 Technology 
|
 Usage 
|
|
---
|
---
|
|
 FastAPI 
|
 Backend framework 
|
|
 Streamlit 
|
 User and driver apps 
|
|
 SQLAlchemy 
|
 ORM 
|
|
 Alembic 
|
 Database migrations 
|
|
 Supabase 
|
 External auth/database integration 
|
|
 Razorpay 
|
 Payments 
|
|
 JWT 
|
 Session authentication 
|
|
 Pytest 
|
 Automated tests 
|
|
 Render / Fly.io 
|
 Deployment targets 
|
---
# Project Structure
# 📂 Project Structure
```text
RUNEV/
├── admin_app/                     # Operations and Driver Dashboard
│   ├── app.py                     # Entry point for the Streamlit Driver Console
│   └── fleet_visual.png           # Visual branding asset
├── backend/                       # Python FastAPI Backend Layer
│   ├── api/                       # Router directories
│   │   ├── v1/                    # API v1 Versioned routes
│   │   │   ├── auth.py            # Authentication, OTP challenge, preferences endpoints
│   │   │   ├── payments.py        # Razorpay payments order creation, verification, webhooks
│   │   │   ├── pricing.py         # Estimate calculation & pricing configuration endpoints
│   │   │   ├── providers.py       # Driver fleet profiles and registration endpoints
│   │   │   ├── ratings.py         # Trip score and feedback endpoints
│   │   │   ├── requests.py        # Booking state workflows (accept, arrived, complete)
│   │   │   └── tracking.py        # Live provider location updates & tracking WebSockets
│   │   └── auth.py                # Legacy root authentication router
│   ├── core/                      # Core helpers
│   │   ├── security.py            # Password hashing, JWT encoding and verification
│   │   └── validation.py          # Input format validators (email, phone, password strength)
│   ├── schemas/                   # Pydantic Schemas for requests and response models
│   │   ├── auth.py
│   │   ├── payment.py
│   │   ├── pricing.py
│   │   ├── provider.py
│   │   ├── rating.py
│   │   ├── service_request.py
│   │   └── tracking.py
│   ├── services/                  # Services business logic layer
│   │   ├── auth_service.py        # OTP stores, credential checks, security logs
│   │   ├── booking_service.py     # Slot bookings business logic
│   │   ├── dispatch_service.py    # Request state management logic
│   │   ├── geo_service.py         # Distance measurements helper
│   │   ├── payment_gateway.py     # Razorpay API client & hash checkers
│   │   ├── payment_service.py     # Payments database operations
│   │   ├── pricing_service.py     # Dynamic price breakdowns & fare logic
│   │   ├── realtime_service.py    # WebSocket connection management
│   │   ├── recommendation_service.py # Provider proximity algorithms
│   │   └── station_service.py     # Charging station management
│   ├── database.py                # Session controls, connection strings, schema synchronization
│   ├── main.py                    # Main app configuration, DB ensure columns, router registers
│   ├── requirements.txt           # Backend-specific package requirements
│   └── runtime.txt                # Python version configuration
├── frontend/                      # Shared Frontend Utilities and Styles
│   ├── components/                # Reusable UI component modules
│   │   ├── geolocation_component/
│   │   │   └── index.html         # Custom iframe HTML5 GPS capturing widget
│   │   ├── analytics.py           # Charts logic for Admin dashboard
│   │   ├── auth.py                # UI auth elements
│   │   ├── geolocation.py         # Coordinates fetching handlers
│   │   ├── maps.py                # Leaflet/Folium map renderer
│   │   ├── payment.py             # Billing receipt screens and UPI QR generators
│   │   ├── theme.py               # Theme synchronization logic
│   │   └── ui.py                  # Cards, metrics, and timeline items
│   ├── styles/                    # Layout stylesheets
│   │   └── theme.py               # Custom Streamlit HTML/CSS styling injection
│   └── utils/                     # Auth client bridges
│       ├── live.py                # Realtime notifications, toasts, status checkers
│       └── supabase_auth.py       # Supabase PKCE callback adapters
├── migrations/                    # Alembic Database Migrations
│   ├── versions/                  # Database schema migration checkpoints
│   │   ├── 0001_initial_schema.py
│   │   ├── 0002_add_ratings.py
│   │   ├── 0003_add_request_otp.py
│   │   └── 0004_add_user_preferences.py
│   ├── env.py                     # Alembic environments config
│   └── script.py.mako             # Migrations blueprint template
├── tests/                         # Automated test suite
│   ├── test_auth_login_options.py # Email OTP, Phone OTP, Supabase oauth, and preferences tests
│   ├── test_core_services.py      # Basic utilities tests
│   ├── test_payment_gateway.py    # Razorpay signature verify and payment order tests
│   ├── test_ratings_api.py        # Driver scoring and review submission tests
│   └── test_request_otp_api.py    # Dispatch workflow OTP validation tests
├── user_app/                      # Streamlit Passenger UI
│   └── app.py                     # Main User Dashboard application
├── utils/                         # Global command-line and client utilities
│   ├── api_client.py              # HTTP client interface matching backend API routes
│   ├── distance.py                # Math formulas for proximity
│   └── otp.py                     # Local OTP generation functions
├── .env.example                   # Local environment variable configuration example
├── alembic.ini                    # Alembic migration settings
├── Dockerfile                     # Docker container configuration
├── init_db.py                     # Script to initialize database tables and seed mock data
├── run_all.bat                    # Windows startup script (starts backend, user_app, admin_app)
└── stop_all.bat                   # Script to stop all local processes
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
# 🗄️ Database Architecture
# ⚙️ Installation
Below are the primary database entities managed via SQLAlchemy ORM (configured in `backend/models.py`):
## 1️⃣ Clone Repository
1.  **User (`users`)**: Represents all actors (roles: `user`, `admin`, `provider`). Stores security variables (hashing, last login, failed login metrics, lock timers, external auth provider).
2.  **UserPreference (`user_preferences`)**: Connects to user profiles to preserve custom UI theme parameters, border styling, color preferences, and layout densities.
3.  **PricingSetting (`pricing_settings`)**: Dynamic fee configurations (base visit fee, platform fee, distance charge rate, charging unit rate, fee limits).
4.  **Provider (`providers`)**: Driver fleet profiles. Stores pricing values, availability status, vehicle description, charger speeds, and GPS coordinates.
5.  **ServiceRequest (`service_requests`)**: Records booking details, pickup coordinates, pricing breakdown, transaction reference, trip state, and trip OTP.
6.  **Payment (`payments`)**: Maps transactions to Razorpay ID references, amount logs, and payment statuses.
7.  **Rating (`ratings`)**: Links user reviews and feedback to providers for completed trips.
8.  **Station (`stations`)**, **Slot (`slots`)**, **Booking (`bookings`)**: Framework models supporting future station slot reservations.
```bash
git clone https://github.com/Tanvi721/RunEv-.git
cd RunEv-
```
---
# 🛠️ Installation & Setup
# 🔧 Backend Setup
### 1. Clone the Repository
## Create Virtual Environment
```bash
git clone https://github.com/Tanvi721/RunEv-.git
cd RunEv-
python -m venv venv
```
### 2. Configure Environment Variables
Create a `.env` file in the root directory based on `.env.example`:
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
# Database Configuration
DATABASE_URL=sqlite:///runev.db
DATABASE_URL=postgresql://postgres:PASSWORD@HOST:5432/postgres
# Security Token Key
JWT_SECRET=your_super_secret_jwt_key_here
JWT_SECRET=your_secret_key
# Payment Gateway Keys (Optional for local development)
RAZORPAY_KEY_ID=your_razorpay_key_id_here
RAZORPAY_KEY_SECRET=your_razorpay_key_secret_here
RAZORPAY_KEY_ID=your_key
# OTP Provider (Options: 'local' / 'twilio')
PHONE_OTP_PROVIDER=local
RAZORPAY_KEY_SECRET=your_secret
# Real-time phone OTP with Twilio Verify
PHONE_OTP_PROVIDER=twilio
DEFAULT_PHONE_COUNTRY_CODE=+91
# Twilio Credentials (Required if PHONE_OTP_PROVIDER=twilio)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_VERIFY_SERVICE_SID=VAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_VERIFY_CHANNEL=sms
```
### 3. Startup Scripts (Windows Recommended)
You can launch the entire ecosystem (Backend + User App + Admin App) with one script. The script automatically executes database seeding if it is not initialized:
---
# ▶️ Run Backend
```bash
# Start all components
run_all.bat
cd backend
uvicorn main:app --reload
```
# Stop all components when done
stop_all.bat
Backend will run at:
```bash
http://127.0.0.1:8000
```
---
# 🔧 Manual Setup & Services Execution
# 🎨 Frontend Setup
### 1. Setup Virtual Environment
```bash
python -m venv venv
```
*   **Windows**: `venv\Scripts\activate`
*   **Linux / macOS**: `source venv/bin/activate`
## Install Frontend Dependencies
### 2. Install Project Dependencies
```bash
pip install -r requirements.txt
```
### 3. Initialize & Populate Database
Initialize the SQLite database with mock users and a provider:
---
## Run Streamlit App
```bash
python init_db.py
streamlit run streamlit_app.py
```
*Creates three mock accounts:*
*   **Admin**: `admin@runev.com` (Password: `admin123`)
*   **User/Passenger**: `john@example.com` (Password: `password123`)
*   **Provider/Driver**: `provider@runev.com` (Password: `provider123`)
### 4. Launch FastAPI Backend
Frontend will run at:
```bash
# Run from root directory
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
http://localhost:8501
```
*   **API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
*   **Health Status**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
### 5. Launch User & Admin Frontend Applications
---
# 🌐 Deployment
## Backend Deployment (Render / Fly.io)
### Start Command
```bash
# In separate terminal windows (with virtual environment active):
streamlit run user_app/app.py --server.port 8501
streamlit run admin_app/app.py --server.port 8502
uvicorn main:app --host 0.0.0.0 --port 10000
```
### Python Version
```txt
python-3.11.9
```
---
# 📡 Backend API Reference
## Frontend Deployment (Streamlit Cloud)
### 🔐 Authentication (`/api/v1/auth`)
*   `POST /register` - Register a new account.
*   `POST /login` - Standard login returning a JWT token.
*   `POST /password/reset` - Allows resetting the user's password.
*   `POST /supabase/session` - Verifies external Supabase access tokens.
*   `POST /login/phone/request-otp` - Phone number authentication challenge.
*   `POST /login/phone/verify` - Verifies phone OTP.
*   `POST /login/email/request-otp` - Email verification challenge.
*   `POST /login/email/verify` - Verifies email OTP.
*   `GET /me` - Get profile details of the current logged-in user.
*   `GET /me/preferences` - Retrieve UI settings.
*   `PUT /me/preferences` - Save updated UI settings.
Update API URL:
### 🚐 Charging Providers & Tracking (`/api/v1/providers` & `/api/v1/tracking`)
*   `GET /providers` - Get proximity-sorted available charging vans.
*   `PUT /providers/profile` - Update provider/driver configuration.
*   `PUT /tracking/provider/location` - HTTP route to update current coordinates.
*   `WS /ws/providers/{provider_id}` - WebSocket for real-time location streaming.
*   `WS /ws/requests/{request_id}` - WebSocket for real-time request tracking.
```python
API_BASE_URL = "https://your-backend-url.onrender.com"
```
### ⚡ Service Bookings (`/api/v1/requests`)
*   `POST /requests/charge` - Book a mobile EV charging request.
*   `GET /requests/charge/{request_id}` - Get status of a request.
*   `GET /requests/mine` - Retrieve booking history.
*   `POST /requests/charge/{request_id}/accept` - Driver accepts a request.
*   `POST /requests/charge/{request_id}/reject` - Driver declines/cancels a request.
*   `POST /requests/charge/{request_id}/arrived` - Driver marks arrival at destination.
*   `POST /requests/charge/{request_id}/start-charging` - Start charging flow (requires trip OTP).
*   `POST /requests/charge/{request_id}/units` - Log charged kWh units and calculate fare.
*   `POST /requests/charge/{request_id}/complete` - Mark charge service complete.
Deploy using:
### 💳 Payments (`/api/v1/payments`)
*   `POST /payments/orders` - Generate Razorpay transaction order.
*   `POST /payments/verify` - Verify Razorpay signature logs.
*   `POST /payments/webhooks/razorpay` - Receive webhook payments logs.
- Streamlit Community Cloud
### ⚙️ Pricing Settings (`/api/v1/pricing`)
*   `GET /pricing/settings` - Retrieve base rates and limits.
*   `PUT /pricing/settings` - Update pricing settings (Admin role required).
*   `POST /pricing/estimate` - Query trip fare estimate.
---
# 🧪 Running Automated Tests
# 🔐 Authentication APIs
Run the test suite using `pytest` to verify the application is working correctly:
```bash
# Run all tests silently
python -m pytest -q
## Register
# Run with verbose output
python -m pytest -v
```http
POST /register
```
Tests cover:
*   [test_auth_login_options.py](file:///c:/Users/Pramod/OneDrive/Desktop/RUNEV%20-%202/tests/test_auth_login_options.py): Email OTP, Phone OTP, preferences configuration, profile updates, and provider credentials reset.
*   [test_request_otp_api.py](file:///c:/Users/Pramod/OneDrive/Desktop/RUNEV%20-%202/tests/test_request_otp_api.py): Booking workflow and validation of the trip OTP code at the start of charging.
*   [test_payment_gateway.py](file:///c:/Users/Pramod/OneDrive/Desktop/RUNEV%20-%202/tests/test_payment_gateway.py): Razorpay transaction flow, payments webhooks, and key signatures checker.
*   [test_ratings_api.py](file:///c:/Users/Pramod/OneDrive/Desktop/RUNEV%20-%202/tests/test_ratings_api.py): Scoring validation, rating limits, and provider score update mechanics.
*   [test_core_services.py](file:///c:/Users/Pramod/OneDrive/Desktop/RUNEV%20-%202/tests/test_core_services.py): Core mathematical formulas (Haversine distances) and validation helpers.
## Login
```http
POST /login
```
## Current User
```http
GET /me
```
---
# 👩‍💻 Author & Contributions
# 💳 Payment APIs
*   **Tanvi Barve** - *Python Developer, AI & Full Stack Enthusiast* - [GitHub Profile](https://github.com/Tanvi721)
- Create Payment Order
- Verify Payment
- UPI Integration
- Razorpay Checkout
Feel free to fork the repository, file issues, or submit pull requests to make RunEV even better!
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
