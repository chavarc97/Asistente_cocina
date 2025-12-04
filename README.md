# Sistema de Asistente de Recetas

# 🍳 Chef Bot - Asistente de Cocina para Telegram

## 📋 Descripción

Chef Bot es un asistente culinario inteligente implementado como bot de Telegram que ayuda a los usuarios a descubrir y cocinar recetas de manera interactiva.

## 🏗️ Arquitectura del Sistema

```
Usuario → Telegram → API Gateway (Node.js) → n8n Workflows → Recipe Service (Python) → TheMealDB API
                                                    ↓
                                              PostgreSQL Database
```

### Componentes Principales


| Componente     | Tecnología     | Puerto | Descripción                                    |
| -------------- | --------------- | ------ | ---------------------------------------------- |
| API Gateway    | Node.js/Express | 3000   | Enrutamiento y validación de requests         |
| Recipe Service | Python/FastAPI  | 3001   | Lógica de negocio y búsqueda de recetas      |
| User Service   | Node.js/Express | 3002   | Gestión de usuarios, perfiles y filtros       |
| n8n            | n8n             | 5678   | Orquestación de workflows                     |
| PostgreSQL     | PostgreSQL 15   | 5432   | Base de datos principal                        |
| Redis          | Redis 7         | 6379   | Caché de recetas y sesiones                   |

## 🎯 Principios SOLID Aplicados

* **S**ingle Responsibility: Cada servicio tiene una única responsabilidad
* **O**pen/Closed: Servicios extensibles sin modificar código existente
* **L**iskov Substitution: Interfaces consistentes entre servicios
* **I**nterface Segregation: APIs específicas por dominio
* **D**ependency Inversion: Inyección de dependencias en todos los servicios

## 🚀 Inicio Rápido

### Prerrequisitos

* Docker y Docker Compose
* Node.js 18+ (para desarrollo local)
* Python 3.11+ (para desarrollo local)
* Token de Bot de Telegram (obtener de @BotFather)
* ngrok (para desarrollo local con webhooks)

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <tu-repo>
   cd chef-bot-telegram
   ```
2. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con tus credenciales
   ```
3. **Iniciar los servicios**
   ```bash
   docker-compose up -d
   ```
4. **Configurar ngrok (desarrollo local)**
   ```bash
   ngrok http 5678
   # Copiar la URL HTTPS generada
   ```
5. **Configurar webhook de Telegram**
   ```bash
   curl "https://api.telegram.org/bot<TU_TOKEN>/setWebhook?url=<NGROK_URL>/webhook/telegram"
   ```
6. **Importar workflow en n8n**
   * Ir a http://localhost:5678
   * Importar `n8n/workflows/telegram-chef-bot.json`
   * Configurar credenciales de Telegram
   * Activar el workflow

## 📁 Estructura del Proyecto

```
chef-bot-telegram/
├── docker-compose.yml          # Orquestación de contenedores
├── .env.example                 # Template de variables de entorno
├── .gitignore                   # Archivos ignorados por git
├── README.md                    # Este archivo
│
├── database/
│   └── init.sql                 # Script de inicialización de BD
│
├── services/
│   ├── api-gateway/             # API Gateway (Node.js)
│   │   ├── Dockerfile
│   │   ├── package.json
│   │   ├── index.js
│   │   ├── middleware/
│   │   │   ├── auth.middleware.js
│   │   │   ├── rate-limiter.js
│   │   │   └── error-handler.js
│   │   ├── services/
│   │   │   ├── service-registry.js
│   │   │   └── health-check.service.js
│   │   └── utils/
│   │       └── logger.js
│   │
│   ├── recipe-service/          # Servicio de Recetas (Python)
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── main.py
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   ├── entities.py
│   │   │   └── value_objects.py
│   │   ├── application/
│   │   │   ├── __init__.py
│   │   │   ├── use_cases.py
│   │   │   └── services.py
│   │   ├── infrastructure/
│   │   │   ├── __init__.py
│   │   │   ├── database.py
│   │   │   ├── repositories.py
│   │   │   ├── themealdb_client.py
│   │   │   └── cache.py
│   │   └── interfaces/
│   │       ├── __init__.py
│   │       └── dto.py
│   │
│   └── user-service/            # Servicio de Usuarios (Node.js)
│       ├── Dockerfile
│       ├── package.json
│       ├── index.js
│       ├── repositories/
│       │   └── user.repository.js
│       ├── services/
│       │   ├── user.service.js
│       │   └── favorites.service.js
│       └── infrastructure/
│           └── database.js
│
├── n8n/
│   ├── README.md
│   └── workflows/
│       └── telegram-chef-bot.json
│
├── scripts/
│   ├── setup.sh                 # Script de configuración inicial
│   ├── verify-setup.sh          # Verificación del sistema
│   └── test-endpoints.sh        # Pruebas de endpoints
│
└── docs/
    ├── API.md                   # Documentación de API
    ├── ARCHITECTURE.md          # Documentación de arquitectura
    └── N8N_SETUP.md             # Guía de configuración de n8n
```

## 🔧 Comandos del Bot


| Comando                  | Descripción                     | Ejemplo                   |
| ------------------------ | -------------------------------- | ------------------------- |
| `/start`                 | Inicia el bot y configura perfil | `/start`                  |
| `/ayuda`                 | Muestra lista de comandos        | `/ayuda`                  |
| `/buscar [ingredientes]` | Busca recetas por ingredientes   | `/buscar pollo arroz`     |
| `/filtro`                | Cambia filtro dietético         | `/filtro`                 |
| `/favoritos`             | Muestra recetas favoritas        | `/favoritos`              |
| `/recomendar`            | Sugiere recetas                  | `/recomendar`             |
| `/convertir`             | Convierte medidas                | `/convertir 2 tazas a ml` |

## 🧪 Desarrollo

### Ejecutar servicios individualmente

```bash
# API Gateway
cd services/api-gateway
npm install
npm run dev

# Recipe Service
cd services/recipe-service
pip install -r requirements.txt
uvicorn main:app --reload --port 3001

# User Service
cd services/user-service
npm install
npm run dev
```

### Ejecutar tests

```bash
# Tests de API Gateway
cd services/api-gateway && npm test

# Tests de Recipe Service
cd services/recipe-service && pytest

# Tests de User Service
cd services/user-service && npm test
```

## 📚 Documentación Adicional

* [Documentación de API](https://claude.ai/chat/docs/API.md)
* [Arquitectura del Sistema](https://claude.ai/chat/docs/ARCHITECTURE.md)
* [Configuración de n8n](https://claude.ai/chat/docs/N8N_SETUP.md)

## 📝 Licencia

Este proyecto es para fines educativos.

## 👥 Equipo

Equipo de Desarrollo - Chef Bot
