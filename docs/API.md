# API Documentation - Chef Bot
## Documentación completa de todas las APIs del sistema

### 📑 Índice

1. [APIs Internas](#apis-internas)
2. [APIs Externas](#apis-externas)
3. [Ejemplos de Uso](#ejemplos-de-uso)
4. [Códigos de Error](#códigos-de-error)

---

## APIs Internas

### 🚪 API Gateway (Puerto 3000)

**Base URL**: `http://localhost:3000`

#### Endpoints Principales:
- `GET /health` - Health check del gateway
- `GET /api/docs` - Documentación de API
- `/api/recipes/*` → Proxy a Recipe Service
- `/api/users/*` → Proxy a User Service

---

### 🍲 Recipe Service (Puerto 3001)

**Base URL**: `http://localhost:3001`

#### 1. Get Recipe by ID
```http
GET /api/v1/recipes/{recipe_id}
```
Obtiene detalles completos de una receta.

**Response**:
```json
{
  "id": "52940",
  "name": "Brown Stew Chicken",
  "category": "Chicken",
  "area": "Jamaican",
  "instructions": "...",
  "ingredients": [{"name": "Chicken", "measure": "1 whole"}],
  "image_url": "https://..."
}
```

#### 2. Search Recipes
```http
POST /api/v1/recipes/search
Content-Type: application/json
```

**Body**:
```json
{
  "ingredients": ["chicken", "rice"],
  "user_id": "123456",
  "dietary_filter": "none"
}
```

**Response**:
```json
{
  "recipes": [...],
  "total": 5,
  "cached": false
}
```

#### 3. Get Recommendations
```http
GET /api/v1/users/{user_id}/recommendations?limit=5
```

#### 4. Manage Favorites
```http
POST /api/v1/users/{user_id}/favorites/{recipe_id}?recipe_name=...
GET /api/v1/users/{user_id}/favorites
DELETE /api/v1/users/{user_id}/favorites/{recipe_id}
```

#### 5. Update Filter
```http
PUT /api/v1/users/{user_id}/filter?dietary_filter=vegetarian
```

---

### 👥 User Service (Puerto 3002)

**Base URL**: `http://localhost:3002`

#### 1. Register/Update User
```http
POST /api/v1/users
Content-Type: application/json
```

**Body**:
```json
{
  "telegram_id": 1169963879,
  "username": "john_doe",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### 2. Get User Profile
```http
GET /api/v1/users/{telegram_id}
```

#### 3. Update Dietary Filter
```http
PUT /api/v1/users/{telegram_id}/filter
```

**Body**:
```json
{
  "dietary_filter": "vegetarian"
}
```

#### 4. Update Activity
```http
POST /api/v1/users/{telegram_id}/activity
```

#### 5. Validate User
```http
GET /api/v1/users/{telegram_id}/validate
```

#### 6. Get Active Users
```http
GET /api/v1/users-active?days=7
```

---

## APIs Externas

### 🍽 TheMealDB API

**Base URL**: `https://www.themealdb.com/api/json/v1/1`

#### Características:
- ✅ **Gratuita** - No requiere API key
- ✅ **300+ recetas** de diferentes países
- ✅ **Detalles completos** - Ingredientes, instrucciones, imágenes
- ❌ **Limitación** - Solo un ingrediente por búsqueda nativa

#### Endpoints Utilizados:

1. **Search by Ingredient**
```http
GET /filter.php?i={ingredient}
```

2. **Lookup Meal by ID**
```http
GET /lookup.php?i={meal_id}
```

3. **Random Meal**
```http
GET /random.php
```

4. **List Categories**
```http
GET /categories.php
```

#### Ejemplo de Response:
```json
{
  "meals": [
    {
      "idMeal": "52940",
      "strMeal": "Brown Stew Chicken",
      "strCategory": "Chicken",
      "strArea": "Jamaican",
      "strInstructions": "...",
      "strMealThumb": "https://...",
      "strIngredient1": "Chicken",
      "strMeasure1": "1 whole"
    }
  ]
}
```

#### Optimizaciones Implementadas:
- **Cache en Redis**: TTL de 24 horas
- **Rate Limiting**: Máx 5 req/s
- **Búsqueda Multi-ingrediente**: Simulada mediante intersección de resultados
- **Retry Logic**: Con backoff exponencial

---

### 🌶️ Spoonacular API

**Base URL**: `https://api.spoonacular.com`
**API Key**: Configurada en variable de entorno

#### Características:
- ✅ **Búsqueda avanzada** - Multi-ingrediente nativo
- ✅ **Análisis nutricional** - Calorías, macros
- ✅ **Substituciones** - Alternativas de ingredientes
- ❌ **Costo** - 150 requests/día gratis

#### Endpoints Principales:

1. **Complex Search**
```http
GET /recipes/complexSearch?includeIngredients=chicken,rice&diet=vegetarian&apiKey={key}
```

2. **Get Recipe Information**
```http
GET /recipes/{id}/information?includeNutrition=true&apiKey={key}
```

3. **Ingredient Substitutes**
```http
GET /food/ingredients/substitutes?ingredientName=butter&apiKey={key}
```

#### Estado Actual:
- API Key configurada pero **no utilizada activamente**
- Reservada para funcionalidades futuras
- TheMealDB es la API principal

---

### 📱 Telegram Bot API

**Base URL**: `https://api.telegram.org/bot{token}`

#### 1. Set Webhook
```http
POST /setWebhook?url={webhook_url}
```

**Configuración Actual**:
```
URL: https://proaction-jeanice-postcartilaginous.ngrok-free.dev/webhook/chef-bot-webhook
```

#### 2. Send Message
```http
POST /sendMessage
```

**Body**:
```json
{
  "chat_id": 1169963879,
  "text": "¡Hola! Mensaje del bot",
  "parse_mode": "Markdown",
  "reply_markup": {
    "inline_keyboard": [[
      {"text": "🔍 Buscar", "callback_data": "/buscar"}
    ]]
  }
}
```

#### 3. Webhook Payload Recibido:
```json
{
  "update_id": 289781523,
  "message": {
    "message_id": 85,
    "from": {
      "id": 1169963879,
      "first_name": "John",
      "username": "john_doe"
    },
    "chat": {
      "id": 1169963879,
      "type": "private"
    },
    "text": "/start"
  }
}
```

---

## Ejemplos de Uso

### Flujo Completo: Búsqueda de Receta

1. **Usuario envía comando en Telegram**:
```
/buscar chicken rice
```

2. **Telegram envía webhook a n8n**:
```json
{
  "message": {
    "text": "/buscar chicken rice",
    "from": {"id": 1169963879}
  }
}
```

3. **n8n parsea y llama a Recipe Service**:
```http
POST http://recipe-service:3001/api/v1/recipes/search
{
  "ingredients": ["chicken", "rice"],
  "user_id": "1169963879"
}
```

4. **Recipe Service consulta TheMealDB**:
```http
GET https://www.themealdb.com/api/json/v1/1/filter.php?i=chicken
```

5. **Recipe Service retorna resultados**:
```json
{
  "recipes": [
    {"id": "52940", "name": "Brown Stew Chicken"},
    {"id": "52941", "name": "Chicken Rice"}
  ],
  "total": 2
}
```

6. **n8n formatea respuesta y envía a Telegram**:
```http
POST https://api.telegram.org/bot.../sendMessage
{
  "chat_id": 1169963879,
  "text": "🍳 **Recetas encontradas (2)**\n1. Brown Stew Chicken..."
}
```

---

## Códigos de Error

| Código | Significado | Descripción |
|--------|-------------|-------------|
| 200 | OK | Operación exitosa |
| 201 | Created | Recurso creado |
| 400 | Bad Request | Validación fallida |
| 404 | Not Found | Recurso no encontrado |
| 409 | Conflict | Duplicado (ej: favorito existe) |
| 429 | Too Many Requests | Rate limit excedido |
| 500 | Internal Server Error | Error del servidor |
| 503 | Service Unavailable | Servicio no disponible |

### Formato de Error:
```json
{
  "error": "Validation error",
  "detail": "Maximum 3 ingredients allowed",
  "timestamp": "2025-12-08T19:00:00.000Z",
  "path": "/api/v1/recipes/search"
}
```

---

## Rate Limiting

| Servicio | Límite | Header |
|----------|--------|--------|
| API Gateway | 100 req/min | `X-RateLimit-Remaining` |
| TheMealDB | 5 req/s (local) | N/A |
| Spoonacular | 150 req/día | `X-API-Quota-Used` |

---

## Autenticación

### Estado Actual:
- ❌ No requiere autenticación (servicios en red privada)
- ✅ Telegram maneja auth de usuarios

### Recomendación para Producción:
- Implementar JWT para servicios internos
- API Gateway con OAuth2
- Rate limiting por usuario

---

## Monitoreo

### Health Checks:
```bash
curl http://localhost:3000/health  # API Gateway
curl http://localhost:3001/health  # Recipe Service  
curl http://localhost:3002/health  # User Service
```

### Logs:
```bash
docker-compose logs -f recipe-service
docker-compose logs -f user-service
docker-compose logs -f n8n
```

---

## Postman Collection

Descargar colección: [Chef Bot Postman Collection](./postman/chef-bot-collection.json)

Variables de entorno:
- `base_url`: http://localhost:3000
- `recipe_service_url`: http://localhost:3001
- `user_service_url`: http://localhost:3002
- `telegram_token`: {tu_token}

---

## Versionado

**Versión Actual**: v1

Todas las APIs usan versionado en la URL: `/api/v1/...`

Cuando se implementen cambios breaking, se creará v2 manteniendo v1 activa.
