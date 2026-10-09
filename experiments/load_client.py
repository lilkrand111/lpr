import asyncio
import time
import sys

import httpx2

BASE = 'http://127.0.0.1:8000'

async def one_request(client, path):
    start = time.perf_counter()
    await client.get(path)
    return time.perf_counter() - start


async def load(path, n):
    async with httpx2.AsyncClient(base_url=BASE, timeout=120, limits=httpx2.Limits(max_connections=None)) as client:
        start = time.perf_counter()
        times = await asyncio.gather(*(one_request(client, path) for _ in range(n)))
        total = time.perf_counter() - start
        print(f"Total time: {total}")
        print("Request times: ", [t for t in times])


async def ping_during_blocking():
    async with httpx2.AsyncClient(base_url=BASE, timeout=120) as client:
        blockers = [
            asyncio.create_task(client.get("/sleep-blocking")) for _ in range(5)
        ]
        await asyncio.sleep(0.5)  # дать запросам дойти до сервера
        start = time.perf_counter()
        await client.get("/ping")
        print(f"/ping ответил через {time.perf_counter() - start:.2f} с")
        await asyncio.gather(*blockers)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "ping-blocking":
        asyncio.run(ping_during_blocking())
    else:
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        asyncio.run(load(mode, n))