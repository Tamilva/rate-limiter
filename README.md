# Rate Limiter API

A FastAPI-based rate limiter that limits 10 requests per user per minute using Redis as the counter store.

## Algorithm Used — Fixed Window Counter

Each user gets a counter in Redis that increments with every request. The counter expires automatically after 60 seconds using Redis TTL, which acts as the window reset.

```
Request comes in
      ↓
Extract user_id from header
      ↓
Get counter from Redis → rate_limit:{user_id}
      ↓
Counter >= 10 → 429 Too Many Requests
Counter < 10  → Allow + Increment counter
      ↓
First request? → Set TTL = 60 seconds (auto reset)
```

## Why Fixed Window?

- Simple and fast to implement
- Redis TTL handles the 60 second window reset automatically
- No need to store timestamps — just a single counter per user
- Easy to debug and reason about in production

## Known Limitation — Boundary Burst Problem

A user can send 20 requests in 2 seconds by sending 10 requests at second 59 (window 1) and 10 more at second 61 (window 2 resets the counter). Both batches are allowed even though 20 requests fired in 2 seconds.

## Production Improvement — Sliding Window Counter

Instead of resetting at fixed intervals, sliding window tracks requests in a rolling 60 second window from the current timestamp.

It uses two counters per user:
- current window count
- previous window count

Effective count is calculated as:

```
previous_count × (1 - elapsed%) + current_count
```

This eliminates the boundary burst problem while staying memory efficient — no need to store individual timestamps like Sliding Window Log.

## Tech Stack

- FastAPI — API framework
- Redis — counter store with TTL
- Docker — runs Redis as a container
- httpx + asyncio — async simulation of 100 users

## Project Structure

```
rate-limiter/
├── app/
│   ├── main.py           # API endpoints
│   ├── rate_limiter.py   # rate limit logic
│   └── redis_client.py   # Redis connection
├── simulate.py           # simulates 100 users
├── docker-compose.yml    # Redis container setup
├── requirements.txt      # dependencies
└── README.md
```

## How to Run

### 1. Start Redis
```
docker-compose up -d
```

### 2. Install dependencies
```
pip install -r requirements.txt
```

### 3. Start API
```
uvicorn app.main:app --reload
```

### 4. Run Simulation (open new terminal)
```
python simulate.py
```

## Simulation Result

100 users each sending 15 requests (limit is 10):

```
user_1 | request_1  | ✅ 200 OK
user_1 | request_2  | ✅ 200 OK
...
user_1 | request_10 | ✅ 200 OK
user_1 | request_11 | ❌ 429 Too Many Requests
user_1 | request_12 | ❌ 429 Too Many Requests
```

| | Count |
|---|---|
| Total users | 100 |
| Requests per user | 15 |
| Total requests | 1500 |
| Allowed | 1000 ✅ |
| Blocked | 500 ❌ |

## API Endpoint

```
GET /api/data

Headers:
  user-id: user_1

Response 200:
{
  "status": "success",
  "user_id": "user_1",
  "message": "Request processed successfully"
}

Response 429:
{
  "detail": "Rate limit exceeded for user_1. Try again after 1 minute."
}
```
