from fastapi import FastAPI, Header
from app.rate_limiter import check_rate_limit
from app.config import RATE_LIMIT, WINDOW_SIZE

app = FastAPI(title="Rate Limiter API")


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/")
def home():
    return {"message": "Rate Limiter API is running"}


@app.get("/api/data")
def get_data(user_id: str = Header(...)):
    check_rate_limit(user_id)
    return {
        "status": "success",
        "user_id": user_id,
        "message": "Request processed successfully"
    }