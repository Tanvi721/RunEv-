from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "RunEv Backend Running Successfully"}