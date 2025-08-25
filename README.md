# Sensores_Iot
Implementação de sensores Iot para atividade 5 de tópicos avançado em web 2. 

1. Criar um Dockerfile para o backend (FastAPI).
2. (Opcional, mas recomendado) Criar um docker-compose.yml para orquestrar:
    * Backend (FastAPI)
    * Broker MQTT (Mosquitto)
    * Servidor CoAP (já vem no backend)
    * Frontend (Nginx)

backend (FastAPI)
Cria um arquivo chamado Dockerfile :
cria um arquivo requirements.txt com as libs usadas pelo backend
Como rodar no Docker
Dentro da pasta do projeto:

# Build da imagem
docker build -t iot-backend .

# Rodar container
docker run -d -p 8000:8000 iot-backend
docker-compose.yml
Cria este arquivo na raiz do projeto (Sensores_Iot/):
