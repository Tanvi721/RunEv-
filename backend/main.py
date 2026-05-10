from fastapi import FastAPI
from backend.database import Base, engine
from backend.api.auth import router as auth_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Auth"]
)

@app.get("/")
def home():
    return {"message": "RunEv Backend Running Successfully"}