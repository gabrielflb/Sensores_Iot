FROM python:3.11-slim

WORKDIR /app

# Copia primeiro o requirements.txt para aproveitar o cache
COPY requirements.txt .

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do backend (inclui o wait-for-mosquitto.sh)
COPY . .

# Dá permissão de execução ao script
RUN chmod +x /app/wait-for-mosquitto.sh

# Expõe as portas (FastAPI/WebSocket e CoAP)
EXPOSE 8000
EXPOSE 5683/udp
