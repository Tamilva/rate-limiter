from fastapi import HTTPException
from app.redis_client import redis_client

RATE_LIMIT = 10
WINDOW_SIZE = 60  # seconds


def check_rate_limit(user_id: str) -> None:
    key = f"rate_limit:{user_id}"
    count = redis_client.get(key)

    if count and int(count) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded for {user_id}. Try again after 1 minute."
        )

    # increment count and set expiry on first request
    pipe = redis_client.pipeline()
    pipe.incr(key)
    pipe.expire(key, WINDOW_SIZE)
    pipe.execute()