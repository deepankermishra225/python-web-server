import httpx
import asyncio
import time 

async def hit(count=None):
    tasks = []
    count = count or 5
    timeout = httpx.Timeout(1000, read=1000)
    async with httpx.AsyncClient(timeout=timeout) as client:
        for _ in range(0, count):
            tasks.append(_hit(client))

        return await asyncio.gather(*tasks)

async def _hit(client):
    try:
        start_time = time.perf_counter()
        response = await client.get("http://localhost:8080")
        end_time = time.perf_counter()

        print(f"Time taken for request: {end_time-start_time}")
        return response
    except httpx.ConnectError as e:
        print(str(e))


if __name__ == '__main__':
    asyncio.run(hit(9))

