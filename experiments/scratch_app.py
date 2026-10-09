import asyncio
import time

from fastapi import FastAPI

app = FastAPI()

@app.get('/ping')
def ping():
    return {'ok': True}

@app.get('/sleep-def')
def sleep_def():
    time.sleep(2)
    return {'endpoint': 'sleep-def'}

@app.get('/sleep-async')
async def sleep_async():
    await asyncio.sleep(2)
    return {'endpoint': 'sleep-async'}

@app.get("/sleep-blocking")
async def sleep_blocking():
    await asyncio.to_thread(time.sleep, 2)
    return {"endpoint": "sleep-blocking"}

