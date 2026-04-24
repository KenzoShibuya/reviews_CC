# Guía de Testeo y Ejecución — MS3 (Reviews y Solicitudes)

Este documento detalla los pasos necesarios para levantar el microservicio y validar su funcionamiento con la nueva estructura modular.

## 1. Requisitos Previos
* **Python 3.12+** instalado localmente.
* **Docker y Docker Compose** (para la base de datos).
* Un archivo `.env` en la raíz del proyecto:
  ```env
  MONGO_URL=mongodb://localhost:27017
  JWT_SECRET=tu_clave_secreta_aqui
  INGESTA_API_KEY=tu_api_key_para_ingesta
  ```

---

## 2. Ejecución del Entorno

### Paso A: Levantar la Base de Datos (MongoDB)
Ahora usamos Docker Compose para asegurar que la base de datos esté lista:
```bash
# Iniciar MongoDB en segundo plano
docker-compose up -d
```

### Paso B: Configurar Python e Instalar Dependencias
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno (macOS/Linux)
source venv/bin/activate
# Activar entorno (Windows)
# venv\Scripts\activate

# Instalar librerías
pip install -r requirements.txt
```

### Paso C: Iniciar el Microservicio
```bash
uvicorn main:app --reload --port 8003
```
El servidor estará disponible en: `http://localhost:8003`

---

## 3. ¿Cómo Testear los Endpoints?

### Opción 1: Swagger UI (Recomendado)
Accede a: `http://localhost:8003/docs`
* Verás los endpoints organizados por los tags **Reviews** y **Solicitudes** (gracias a la nueva modularización).
* **Auth**: Usa el botón **Authorize** con un JWT.

### Opción 2: Generación de Token
```bash
python generar_token.py
```
Copia el token generado y úsalo como `Bearer <token>`.

---

## Estructura del Proyecto (Modular)
El código se ha organizado para seguir mejores prácticas de arquitectura:
* `app/api/`: Contiene los **Handlers** (rutas de la API).
* `app/models/`: Esquemas de validación de datos (Pydantic).
* `app/db/`: Configuración y conexión a MongoDB.
* `app/middleware/`: Lógica de seguridad (JWT).
* `app/core/`: Configuración global y variables de entorno.

---
