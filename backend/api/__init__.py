from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend import models
from backend.api.v1 import auth, payments, pricing, providers, ratings, requests, tracking
from backend.database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RunEV - On-Demand Charging API",
    version="1.0.0",
    description="Backend API for rider requests, provider dispatch, and charging van operations.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:8501",
        "http://localhost:8502",
        "http://127.0.0.1:8501",
        "http://127.0.0.1:8502",
        "http://172.20.10.5:8501",
        "http://172.20.10.5:8502",
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+|192\.168\.\d+\.\d+):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["health"])
def read_root():
    return {"message": "Welcome to RunEV API Layer"}


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


app.include_router(auth.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")
app.include_router(pricing.router, prefix="/api/v1")
app.include_router(providers.router, prefix="/api/v1")
app.include_router(requests.router, prefix="/api/v1")
app.include_router(ratings.router, prefix="/api/v1")
app.include_router(tracking.router, prefix="/api/v1")
app.include_router(tracking.ws_router)

# Keep existing Streamlit clients working while the frontend migrates to /api/v1.
app.include_router(providers.legacy_router, prefix="/api")
app.include_router(requests.legacy_router, prefix="/api")
