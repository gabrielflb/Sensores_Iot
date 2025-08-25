import os
import time
import json
import random
from dotenv import load_dotenv
import datetime
import base64
import paho.mqtt.client as mqtt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

load_dotenv()
# ===== CONFIG =====
BROKER = os.getenv("MQTT_BROKER", "localhost")
PORT = int(os.getenv("MQTT_PORT", ""))
TOPIC = os.getenv("MQTT_TOPIC", "")

# CHAVE SECRETA (32 bytes = AES-256) -> guardar em variável de ambiente
KEY = os.getenv("AES_KEY", "12345678901234567890123456789012").encode()

client = mqtt.Client(client_id="sensor_temp_aes")

def connect():
    client.connect(BROKER, PORT, keepalive=60)
    client.loop_start()

def encrypt_payload(data: dict) -> str:
    """
    Recebe dict, converte pra JSON, criptografa com AES-GCM e devolve base64.
    """
    aesgcm = AESGCM(KEY)
    nonce = os.urandom(12)  # IV/nonce único por mensagem
    plaintext = json.dumps(data).encode()
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    # junta nonce + ciphertext
    return base64.b64encode(nonce + ciphertext).decode()

def make_data():
    value = round(random.uniform(15.0, 35.0), 2)
    anomaly = (value < 18.0) or (value > 30.0)
    return {
        "device_id": "device01",
        "sensor": "temperature",
        "value": value,
        "unit": "C",
        "anomaly": anomaly,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }

def publish_loop():
    while True:
        data = make_data()
        encrypted = encrypt_payload(data)
        client.publish(TOPIC, encrypted, qos=1)
        print(f"Publicado criptografado: {encrypted[:60]}...")
        time.sleep(5)

if __name__ == "__main__":
    connect()
    try:
        publish_loop()
    except KeyboardInterrupt:
        client.loop_stop()
        client.disconnect()
