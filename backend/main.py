from fastapi import FastAPI
from backend.database import Base, engine, ensure_auth_security_columns, ensure_pricing_columns
from backend.api.v1.auth import router as auth_router
from backend.api.v1.payments import router as payments_router
from backend.api.v1.pricing import router as pricing_router
from backend.api.v1.providers import legacy_router as legacy_providers_router
from backend.api.v1.providers import router as providers_router
from backend.api.v1.ratings import router as ratings_router
from backend.api.v1.requests import legacy_router as legacy_requests_router
from backend.api.v1.requests import router as requests_router
from backend.api.v1.tracking import router as tracking_router
from backend.api.v1.tracking import ws_router as tracking_ws_router

app = FastAPI()

Base.metadata.create_all(bind=engine)
ensure_auth_security_columns()
ensure_pricing_columns()

app.include_router(auth_router, prefix="/api/v1")
app.include_router(requests_router, prefix="/api/v1")
app.include_router(providers_router, prefix="/api/v1")
app.include_router(payments_router, prefix="/api/v1")
app.include_router(pricing_router, prefix="/api/v1")
app.include_router(tracking_router, prefix="/api/v1")
app.include_router(ratings_router, prefix="/api/v1")
app.include_router(tracking_ws_router)
app.include_router(legacy_requests_router)
app.include_router(legacy_providers_router)

@app.get("/")
def home():
    return {"message": "RunEv Backend Running Successfully"}
