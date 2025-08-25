import os
import json
import base64
import asyncio
from dotenv import load_dotenv
import requests
from typing import Set
from fastapi import FastAPI, WebSocket
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import uvicorn

load_dotenv()
# -------------------- Config --------------------
API_CITY = "Santo Antonio de Jesus"
API_KEY = os.getenv("API_KEY", "")
API_URL = f"https://api.openweathermap.org/data/2.5/weather?q={API_CITY},br&appid={API_KEY}"
print(API_URL)

AES_KEY_ENV = os.getenv("AES_KEY", "")  # 32 bytes
AES_KEY = AES_KEY_ENV.encode()
if len(AES_KEY) != 32:
    raise RuntimeError("AES_KEY deve ter 32 bytes para AES-256")

FETCH_INTERVAL = 10  

# -------------------- App & state --------------------
app = FastAPI()
connected_websockets: Set[WebSocket] = set()
ASYNCIO_LOOP = None  

# -------------------- AES helpers --------------------
def encrypt_payload(data: dict) -> str:
    aesgcm = AESGCM(AES_KEY)
    nonce = os.urandom(12)
    plaintext = json.dumps(data).encode("utf-8")
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return base64.b64encode(nonce + ciphertext).decode("utf-8")

# -------------------- WebSocket / broadcast --------------------
async def broadcast(message: str):
    to_remove = []
    for ws in set(connected_websockets):
        try:
            await ws.send_text(message)
        except Exception:
            to_remove.append(ws)
    for ws in to_remove:
        connected_websockets.discard(ws)

@app.websocket("/ws-umidade")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connected_websockets.add(ws)
    print(f"[WS] Cliente conectado (umidade). Total: {len(connected_websockets)}")
    try:
        while True:
            try:
                _ = await ws.receive_text()
            except Exception:
                break
    finally:
        connected_websockets.discard(ws)
        print(f"[WS] Cliente desconectado (umidade). Total: {len(connected_websockets)}")

# -------------------- API polling --------------------
async def fetch_weather_data():
    while True:
        try:
            resp = requests.get(API_URL, timeout=5)
            data = resp.json()
            umidade = data.get("main", {}).get("humidity")
            print(f"[API] Umidade atual em {API_CITY}: {umidade}%")

            package = {"sensor": "humidity", "value": umidade}
            payload_encrypted = encrypt_payload(package)

            if ASYNCIO_LOOP:
                asyncio.run_coroutine_threadsafe(
                    broadcast(json.dumps({"topic": "sensors/humidity", "payload": payload_encrypted})),
                    ASYNCIO_LOOP
                )
        except Exception as e:
            print(f"[API] Erro ao consultar OpenWeatherMap: {e}")
        await asyncio.sleep(FETCH_INTERVAL)

# -------------------- Startup event --------------------
@app.on_event("startup")
async def startup_event():
    global ASYNCIO_LOOP
    ASYNCIO_LOOP = asyncio.get_running_loop()
    asyncio.create_task(fetch_weather_data())
    print("[APP] Backend de umidade iniciado e consultando API pública.")

# -------------------- Run --------------------
if __name__ == "__main__":
    uvicorn.run("sensor_umidade:app", host="0.0.0.0", port=8001, reload=True)
