FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias necesarias para compilar algunos paquetes si fuera necesario
# RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8003

# El microservicio fallará al arrancar si no recibe MONGO_URL y JWT_SECRET
# desde el entorno (docker-compose, kubernetes, o docker run -e)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
