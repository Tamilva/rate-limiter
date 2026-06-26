import httpx
import asyncio

BASE_URL = "http://localhost:8000/api/data"
TOTAL_USERS = 100
REQUESTS_PER_USER = 15  


async def send_request(client: httpx.AsyncClient, user_id: str, request_num: int) -> None:
    headers = {"user-id": user_id}

    try:
        response = await client.get(BASE_URL, headers=headers)

        if response.status_code == 200:
            print(f"user_{user_id} | request_{request_num} | 200 OK - Allowed")
        elif response.status_code == 429:
            print(f"user_{user_id} | request_{request_num} | 429 Too Many Requests - Blocked")

    except Exception as e:
        print(f"user_{user_id} | request_{request_num} | Error: {str(e)}")


async def simulate_user(client: httpx.AsyncClient, user_id: str) -> None:
    for request_num in range(1, REQUESTS_PER_USER + 1):
        await send_request(client, user_id, request_num)


async def main() -> None:
    print("=" * 60)
    print(f"Simulating {TOTAL_USERS} users with {REQUESTS_PER_USER} requests each")
    print(f"Rate limit: 10 requests per user per minute")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        tasks = [
            simulate_user(client, str(user_id))
            for user_id in range(1, TOTAL_USERS + 1)
        ]
        await asyncio.gather(*tasks)

    print("=" * 60)
    print("Simulation complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())