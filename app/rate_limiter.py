from fastapi import HTTPException
from app.redis_client import redis_client
from app.config import RATE_LIMIT, WINDOW_SIZE


def check_rate_limit(user_id: str) -> None:
    key = f"rate_limit:{user_id}"
    count = redis_client.get(key)

    if count and int(count) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded for {user_id}. Try again after 1 minute."
        )

    pipe = redis_client.pipeline()
    pipe.incr(key)
    pipe.expire(key, WINDOW_SIZE)
    pipe.execute()