# ReadMe — Arquitectura de Microservicios

## Descripción del proyecto

**ReadMe** es una plataforma de intercambio y venta de libros físicos entre usuarios, tipo marketplace peer-to-peer. Los usuarios publican los libros que tienen disponibles, otros usuarios pueden enviar solicitudes para comprar o intercambiar, y coordinan la entrega entre ellos a través de un hilo de mensajes privado dentro de la solicitud.

La plataforma no maneja dinero ni entregas. Solo conecta personas y facilita el acuerdo. El pago y la entrega se coordinan por fuera (en persona, por courier, como los usuarios prefieran).

---

## Flujo principal

1. Un usuario se registra y arma su "estantería virtual" publicando libros con foto, descripción y precio opcional.
2. Otro usuario explora el catálogo, encuentra un libro que le interesa y envía una solicitud con un mensaje inicial ("Hola, me interesa tu libro, lo intercambiamos?").
3. Se crea un hilo de mensajes privado dentro de esa solicitud. Ambos conversan para ponerse de acuerdo (precio, intercambio, punto de encuentro, envío, etc.).
4. El vendedor decide: **acepta** o **rechaza** la solicitud.
5. Si acepta: se registra la transacción, el libro se marca como no disponible, y cualquier otra solicitud pendiente para ese mismo libro se rechaza automáticamente. Ambos usuarios pueden dejar una review del otro.
6. Si rechaza: se notifica al comprador por correo. El hilo de mensajes sigue abierto por si el vendedor quiere explicar por qué.
7. El comprador puede **cancelar** su solicitud en cualquier momento mientras esté pendiente (antes de que el vendedor responda).

Los hilos de mensajes nunca se cierran, independientemente del estado de la solicitud.

---

## Estados de una solicitud

| Estado | Quién lo activa | Qué pasa |
|---|---|---|
| **Pendiente** | Comprador (al crear solicitud) | Vendedor recibe correo. Ambos pueden enviarse mensajes |
| **Aceptada** | Vendedor | Se registra transacción, libro queda no disponible, solicitudes pendientes del mismo libro se rechazan automáticamente. Se habilitan reviews. Estado terminal |
| **Rechazada** | Vendedor | Se notifica al comprador. Estado terminal |
| **Cancelada** | Comprador (solo si está pendiente) | Se cancela la solicitud. Estado terminal |

---

## Microservicios

### MS1 — Usuarios (Go/Gin + PostgreSQL) — Puerto 8001

**Tabla `zones`** (seed data, solo lectura):
- `id` SERIAL PRIMARY KEY
- `name` VARCHAR(100) NOT NULL

Zonas seed: Miraflores, San Isidro, Barranco, San Miguel, Surco, La Molina, Jesús María, Magdalena, Pueblo Libre, Lince, San Borja, Breña, Otros.

**Tabla `users`**:
- `id` SERIAL PRIMARY KEY
- `name` VARCHAR(100) NOT NULL
- `email` VARCHAR(150) UNIQUE NOT NULL
- `password_hash` VARCHAR(255) NOT NULL
- `zone_id` INTEGER REFERENCES zones(id) — **nullable, opcional**
- `photo_url` TEXT
- `created_at` TIMESTAMP DEFAULT NOW()

| Método | Endpoint | Descripción | Auth |
|---|---|---|---|
| POST | `/api/users` | Registro. Body: name, email, password, zone_id (opcional), photo_url (opcional) | No |
| POST | `/api/users/login` | Login. Retorna JWT con user_id y email | No |
| GET | `/api/users/:id` | Perfil de un usuario (sin password_hash). También lo llama MS4 para validar | Sí |
| PUT | `/api/users/:id` | Editar perfil. Solo el dueño (user_id del JWT == :id) | Sí |
| GET | `/api/zones` | Listar zonas para dropdown del frontend | Sí |

---

### MS2 — Libros y transacciones (Java/Spring Boot + MySQL) — Puerto 8002

**Tabla `categories`** (seed data, solo lectura):
- `id` INT PRIMARY KEY AUTO_INCREMENT
- `name` VARCHAR(100) NOT NULL

**Tabla `books`**:
- `id` INT PRIMARY KEY AUTO_INCREMENT
- `user_id` INT NOT NULL
- `title` VARCHAR(255) NOT NULL
- `author` VARCHAR(255) NOT NULL
- `category_id` INT REFERENCES categories(id)
- `description` TEXT
- `photo_url` TEXT
- `price` DECIMAL(10,2) — nullable, opcional. Si tiene precio es venta, si no, es intercambio o a convenir
- `available` BOOLEAN DEFAULT TRUE — si está disponible para solicitudes
- `active` BOOLEAN DEFAULT TRUE — soft delete
- `created_at` TIMESTAMP DEFAULT NOW()

**Tabla `transactions`**:
- `id` INT PRIMARY KEY AUTO_INCREMENT
- `book_id` INT REFERENCES books(id)
- `buyer_id` INT NOT NULL
- `seller_id` INT NOT NULL
- `created_at` TIMESTAMP DEFAULT NOW()

| Método | Endpoint | Descripción | Auth |
|---|---|---|---|
| GET | `/api/categories` | Listar categorías para dropdown | Sí |
| GET | `/api/books` | Explorar libros. Query params: ?category=ficcion&search=dune. Solo retorna available=true y active=true | Sí |
| GET | `/api/books/:id` | Detalle de un libro | Sí |
| GET | `/api/books/user/:userId` | Estantería de un usuario | Sí |
| POST | `/api/books` | Publicar libro. Body: title, author, category_id, description, photo_url, price (opcional) | Sí |
| PUT | `/api/books/:id` | Editar publicación. Solo el dueño | Sí |
| DELETE | `/api/books/:id` | Soft delete: marca active=false. Solo el dueño | Sí |
| PUT | `/api/books/:id/availability` | Cambiar disponibilidad. Lo llama MS4 al aceptar una solicitud | Sí |
| POST | `/api/transactions` | Registrar transacción completada. Lo llama MS4 | Sí |
| GET | `/api/transactions/user/:userId` | Historial de transacciones de un usuario | Sí |

---

### MS3 — Reviews y solicitudes (Node.js/Express + MongoDB) — Puerto 8003

**Colección `reviews`**:
```json
{
  "user_id": 1,
  "target_user_id": 2,
  "transaction_id": "abc123",
  "rating": 4.5,
  "comment": "Buen trato, libro en buen estado",
  "created_at": "2026-04-17T..."
}
```

**Colección `solicitudes`**:
```json
{
  "book_id": 10,
  "buyer_id": 1,
  "seller_id": 2,
  "status": "pendiente",
  "messages": [
    { "from": 1, "text": "Hola, me interesa tu libro", "date": "..." },
    { "from": 2, "text": "Dale, te lo puedo enviar por Olva", "date": "..." }
  ],
  "created_at": "2026-04-17T..."
}
```

| Método | Endpoint | Descripción | Auth |
|---|---|---|---|
| POST | `/api/reviews` | Crear review. Body: target_user_id, transaction_id, rating (1-5), comment. user_id sale del JWT | Sí |
| GET | `/api/reviews/user/:userId` | Reviews que le dejaron a un usuario | Sí |
| GET | `/api/reviews/stats/:userId` | Rating promedio y cantidad total | Sí |
| POST | `/api/solicitudes` | Crear solicitud. Body: book_id, seller_id, message inicial. Lo llama MS4 | Sí |
| GET | `/api/solicitudes/user/:userId` | Mis solicitudes (enviadas y recibidas) | Sí |
| GET | `/api/solicitudes/:id` | Detalle de solicitud con todos los mensajes | Sí |
| POST | `/api/solicitudes/:id/messages` | Agregar mensaje. Body: text. El from sale del JWT | Sí |
| PUT | `/api/solicitudes/:id/status` | Cambiar estado. Lo llama MS4 | Sí |

---

### MS4 — Orquestador (Python/FastAPI, sin BD) — Puerto 8004

No tiene base de datos. Orquesta operaciones entre MS1, MS2 y MS3, y envía correos de notificación.

| Método | Endpoint | Flujo |
|---|---|---|
| POST | `/api/orders/solicitud` | Valida buyer != seller → valida comprador existe (MS1) → verifica libro disponible y activo (MS2) → verifica no hay solicitud pendiente duplicada del mismo buyer para el mismo book (MS3) → crea solicitud con mensaje inicial (MS3) → envía correo al vendedor |
| PUT | `/api/orders/:id/accept` | Valida que quien acepta sea el vendedor → actualiza estado a "aceptada" (MS3) → registra transacción (MS2) → marca libro no disponible (MS2) → rechaza automáticamente todas las demás solicitudes pendientes del mismo book_id (MS3) → envía correo al comprador |
| PUT | `/api/orders/:id/reject` | Valida que quien rechaza sea el vendedor → actualiza estado a "rechazada" (MS3) → envía correo al comprador |
| PUT | `/api/orders/:id/cancel` | Valida que quien cancela sea el comprador → valida que la solicitud esté en "pendiente" → actualiza estado a "cancelada" (MS3) |

---

### MS5 — Analytics (Python + AWS Athena) — Puerto 8005

Consultas analíticas sobre data ingestada en S3 vía Glue y Athena. Endpoints por definir según las consultas requeridas (mínimo 4 consultas SQL con joins y 2 vistas).

Ejemplos de consultas:
- Libros más solicitados por categoría
- Usuarios con más transacciones completadas
- Distribución de precios por categoría
- Rating promedio de usuarios por zona

---

## Autenticación

JWT con clave secreta compartida (`JWT_SECRET` como variable de entorno en todos los MS). MS1 genera el token en login, los demás solo lo validan. Cada MS tiene un middleware que decodifica el JWT del header `Authorization: Bearer <token>`, extrae el `user_id`, y lo inyecta en el contexto del request.

---

## Infraestructura de producción

- **MV Producción 1 y 2**: Docker Compose con los 5 MS containerizados. Réplicas idénticas detrás de un balanceador de carga privado.
- **MV Base de datos**: Docker Compose con PostgreSQL, MySQL y MongoDB. Accesible solo por IP privada.
- **Frontend**: React en AWS Amplify.
- **API Gateway**: AWS API Gateway con HTTPS expuesto públicamente.

---

## Data Science

- **MV Ingesta**: 3 contenedores Docker en Python que extraen datos de MS1, MS2 y MS3 vía API REST, generan CSV/JSON y los cargan en un bucket S3.
- **AWS Glue**: Catálogo de datos para cada archivo en S3.
- **AWS Athena**: Consultas SQL sobre los datos catalogados. Mínimo 4 consultas con joins y 2 vistas.
- **MS5**: API REST que ejecuta las queries de Athena y retorna los resultados.
