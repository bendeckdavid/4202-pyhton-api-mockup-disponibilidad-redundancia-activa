import os
import asyncio
import requests
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.responses import JSONResponse

app = FastAPI()
load_dotenv()

SERVERS = [
    ("server_1", os.getenv("SERVER_1_URL")),
    ("server_2", os.getenv("SERVER_2_URL"))
]


@app.api_route("/{path:path}")
async def proxy(path: str):
    async def server_request(server):
        name, url = server
        try:
            return name, requests.get(f"{url}/{path}")
        except Exception:
            return name, None

    tasks = [server_request(server) for server in SERVERS]

    for task in asyncio.as_completed(tasks):
        server, response = await task
        print(response)
        if response and response.status_code == 200:
            return JSONResponse(
                status_code=response.status_code,
                content={
                    "servidor": server,
                    "tiempo": response.elapsed.total_seconds(),
                    "response": response.json(),
                }
            )

    return {"error": "Los servicios de backend no están respondiendo"}, 503
