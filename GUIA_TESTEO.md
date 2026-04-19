# Guía de Testeo y Ejecución — MS3 (Reviews y Solicitudes)

Este documento detalla los pasos necesarios para levantar el microservicio y validar su funcionamiento.

## 1. Requisitos Previos
* **Python 3.12+** instalado localmente.
* **MongoDB** corriendo (localmente o vía Docker).
* Un archivo `.env` en la raíz del proyecto con el siguiente formato:
  ```env
  MONGO_URL=mongodb://localhost:27017/reviews_db
  JWT_SECRET=tu_clave_secreta_aqui
  ```

---

## 2. Ejecución Local

### Paso A: Crear entorno virtual e instalar dependencias
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows)
venv\Scripts\activate
# Activar entorno (macOS/Linux)
source venv/bin/activate

# Instalar librerías
pip install -r requirements.txt
```

### Paso B: Iniciar el servidor
```bash
uvicorn main:app --reload --port 8003
```
El servidor estará disponible en: `http://localhost:8003`



---

## 3. ¿Cómo Testear los Endpoints?

### Opción 1: Documentación Interactiva (Swagger UI) — RECOMENDADO
FastAPI genera automáticamente una interfaz para probar los endpoints.
1. Abre tu navegador en: `http://localhost:8003/docs`
2. Verás todos los endpoints de **Reviews** y **Solicitudes**.
3. **Nota sobre Seguridad**: Para los endpoints que requieren candado (Auth), deberás presionar el botón **Authorize** e ingresar un JWT válido.

### Opción 2: Generación de Token para Pruebas
Si necesitas un token para probar, puedes usar el script incluido:
```bash
python generar_token.py
```
Copia el token resultante y úsalo en Swagger o Postman como `Bearer Token`.

---

## Estructura de Datos (MongoDB)
* **Base de datos**: `reviews_db`
* **Colecciones**: 
    - `reviews`: Almacena las reseñas entre usuarios.
    - `solicitudes`: Almacena los hilos de mensajes y estados de compra.
