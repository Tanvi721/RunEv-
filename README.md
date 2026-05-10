# 🚗⚡ RunEV — On-Demand EV Charging Platform

<div align="center">

![RunEV Banner](https://img.shields.io/badge/RunEV-EV%20Charging-blueviolet?style=for-the-badge)

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red?style=flat-square)
![Supabase](https://img.shields.io/badge/Supabase-Database-3ECF8E?style=flat-square)
![Razorpay](https://img.shields.io/badge/Razorpay-Payments-02042B?style=flat-square)

### Smart mobile EV charging platform with real-time tracking, online payments, and driver dispatch system.

</div>

---

# 🌍 Overview

RunEV is a full-stack EV charging service platform where users can:

- 🔋 Request mobile EV charging
- 📍 Track charging van live
- 💳 Make online payments
- 🚚 Get charging support at their location
- 👨‍🔧 Connect with charging providers
- 📊 View charging status in real time

The project is built using:

- **FastAPI** → Backend APIs
- **Streamlit** → Frontend UI
- **Supabase PostgreSQL** → Cloud Database
- **Razorpay** → Payment Gateway
- **Render / Fly.io** → Deployment

---

# ✨ Features

## 👤 User Features

- User Authentication (JWT)
- Login / Signup
- Request EV charging
- Live charging status
- Payment integration
- Modern UI dashboard
- Real-time updates

---

## 🚚 Provider Features

- Provider login
- Accept charging requests
- Vehicle management
- Dispatch system
- Location tracking

---

## 💳 Payment Features

- Razorpay Integration
- UPI Support
- Secure payment flow
- Payment verification

---

## 📡 Backend Features

- REST API with FastAPI
- JWT Authentication
- PostgreSQL Database
- SQLAlchemy ORM
- API routing system
- Modular architecture

---

# 🛠️ Tech Stack

| Technology | Usage |
|---|---|
| FastAPI | Backend Framework |
| Streamlit | Frontend UI |
| PostgreSQL | Database |
| Supabase | Cloud Database Hosting |
| SQLAlchemy | ORM |
| Razorpay | Payments |
| JWT | Authentication |
| Render / Fly.io | Deployment |

---

# 📂 Project Structure

```bash
RunEv-
│
├── backend/
│   ├── api/
│   ├── services/
│   ├── schemas/
│   ├── core/
│   ├── database.py
│   ├── models.py
│   ├── main.py
│   ├── requirements.txt
│
├── frontend/
│
├── streamlit_app.py
├── requirements.txt
└── README.md
```

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

# 👩‍💻 Author

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