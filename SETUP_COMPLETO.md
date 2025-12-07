# 🍳 GUÍA COMPLETA DE CONFIGURACIÓN - CHEF BOT

Esta guía te llevará paso a paso para hacer funcionar el bot de Telegram completamente.

## 📋 REQUISITOS PREVIOS

Antes de empezar, asegúrate de tener instalado:

- ✅ Docker Desktop (última versión)
- ✅ Node.js 18+ (para desarrollo local opcional)
- ✅ Python 3.11+ (para desarrollo local opcional)
- ✅ Una cuenta de Telegram

---

## 🚀 PASO 1: CREAR EL BOT DE TELEGRAM

### 1.1 Obtener el Token del Bot

1. Abre Telegram y busca `@BotFather`
2. Envía el comando `/newbot`
3. Sigue las instrucciones:
   - Nombre del bot: `Chef Bot` (o el que prefieras)
   - Username: `tu_chef_bot` (debe terminar en 'bot')
4. **GUARDA EL TOKEN** que te da (algo como: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 1.2 Configurar el Token en el Proyecto

1. Abre el archivo `.env` en la raíz del proyecto
2. Busca la línea:
   ```
   TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
   ```
3. Reemplázala con tu token:
   ```
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

---

## 🐳 PASO 2: INICIAR DOCKER Y LOS SERVICIOS

### 2.1 Verificar Docker

```bash
# Asegúrate de que Docker Desktop esté corriendo
docker --version
docker-compose --version
```

### 2.2 Iniciar todos los servicios

```bash
# En la raíz del proyecto
docker-compose up -d
```

Esto iniciará:
- ✅ PostgreSQL (Base de datos)
- ✅ Redis (Caché)
- ✅ API Gateway (Puerto 3000)
- ✅ Recipe Service (Puerto 3001)
- ✅ User Service (Puerto 3002)
- ✅ n8n (Puerto 5678)

### 2.3 Verificar que todo esté corriendo

```bash
docker-compose ps
```

Deberías ver todos los servicios como "Up" (running).

### 2.4 Ver logs en caso de errores

```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f recipe-service
docker-compose logs -f n8n
```

---

## 🔧 PASO 3: CONFIGURAR N8N

### 3.1 Acceder a n8n

1. Abre tu navegador en: http://localhost:5678
2. **Credenciales por defecto:**
   - Usuario: `admin`
   - Contraseña: `n8n_admin_123`

### 3.2 Importar el Workflow de Telegram

1. En n8n, haz clic en el menú (≡) → "Import from File"
2. Selecciona el archivo: `n8n/workflows/telegram-chef-bot.json`
3. El workflow se importará con todos los nodos configurados

### 3.3 Configurar las Credenciales de Telegram

1. En el workflow, busca el nodo "Telegram Trigger"
2. Haz clic en él
3. En "Credentials", selecciona "Create New"
4. Ingresa:
   - **Name:** Telegram Bot API
   - **Access Token:** Tu token de Telegram (el mismo del `.env`)
5. Guarda las credenciales

### 3.4 Activar el Workflow

1. En la esquina superior derecha, activa el toggle "Active"
2. El workflow debe cambiar a estado "Active"

---

## 🌐 PASO 4: CONFIGURAR NGROK (Para desarrollo local)

Para que Telegram pueda enviar mensajes a tu bot local, necesitas ngrok:

### 4.1 Instalar ngrok

```bash
# macOS con Homebrew
brew install ngrok

# O descarga desde: https://ngrok.com/download
```

### 4.2 Iniciar ngrok

```bash
ngrok http 5678
```

Verás algo como:
```
Forwarding: https://abc123xyz.ngrok.io -> http://localhost:5678
```

**COPIA LA URL HTTPS** (ej: `https://abc123xyz.ngrok.io`)

### 4.3 Actualizar el Webhook URL

1. Actualiza el archivo `.env`:
   ```
   WEBHOOK_URL=https://abc123xyz.ngrok.io/
   NGROK_URL=https://abc123xyz.ngrok.io
   ```

2. Reinicia n8n:
   ```bash
   docker-compose restart n8n
   ```

### 4.4 Configurar el Webhook de Telegram

Ejecuta este comando (reemplaza con TU token y TU url de ngrok):

```bash
curl "https://api.telegram.org/bot<TU_TOKEN>/setWebhook?url=https://abc123xyz.ngrok.io/webhook/telegram"
```

Deberías recibir:
```json
{"ok":true,"result":true,"description":"Webhook was set"}
```

---

## ✅ PASO 5: PROBAR EL BOT

### 5.1 Abrir Telegram

1. Busca tu bot por el username que le diste (ej: `@tu_chef_bot`)
2. Haz clic en "Start" o envía `/start`

### 5.2 Comandos para Probar

```
/start          → Mensaje de bienvenida
/ayuda          → Ver todos los comandos
/buscar chicken → Buscar recetas con pollo
/favoritos      → Ver favoritos (vacío al inicio)
/recomendar     → Obtener recomendaciones
/convertir 2 tazas a ml → Convertir medidas
/filtro         → Cambiar filtro dietético
```

### 5.3 Verificar en n8n

1. Ve a n8n (http://localhost:5678)
2. Abre el workflow "Chef Bot - Telegram Workflow Completo"
3. Verás las ejecuciones en tiempo real cuando envíes mensajes

---

## 🔍 PASO 6: VERIFICAR SERVICIOS

### 6.1 Health Checks

Verifica que todos los servicios respondan:

```bash
# API Gateway
curl http://localhost:3000/health

# Recipe Service
curl http://localhost:3001/health

# User Service
curl http://localhost:3002/health
```

### 6.2 Probar Búsqueda de Recetas

```bash
curl -X POST http://localhost:3001/api/v1/recipes/search \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": ["chicken"],
    "user_id": "12345"
  }'
```

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Problema: "El bot no responde"

**Solución:**
1. Verifica que ngrok esté corriendo
2. Verifica el webhook:
   ```bash
   curl "https://api.telegram.org/bot<TU_TOKEN>/getWebhookInfo"
   ```
3. Asegúrate de que el workflow en n8n esté "Active"

### Problema: "Error de conexión a la base de datos"

**Solución:**
```bash
# Reiniciar PostgreSQL
docker-compose restart postgres

# Ver logs
docker-compose logs postgres
```

### Problema: "TheMealDB API no responde"

**Solución:**
- TheMealDB es gratuita pero tiene rate limits
- Espera 1 minuto y vuelve a intentar
- Verifica: https://www.themealdb.com/api.php

### Problema: "n8n no se conecta"

**Solución:**
```bash
# Limpiar y reiniciar n8n
docker-compose down
docker volume rm asistente_cocina_n8n_data
docker-compose up -d n8n
```

---

## 📊 MONITOREO Y LOGS

### Ver logs en tiempo real

```bash
# Todos los servicios
docker-compose logs -f

# Solo n8n
docker-compose logs -f n8n

# Solo recipe-service
docker-compose logs -f recipe-service
```

### Acceder a la base de datos

```bash
# Conectarse a PostgreSQL
docker exec -it chef_postgres psql -U chef_user -d chef_db

# Ver usuarios
SELECT * FROM users;

# Ver favoritos
SELECT * FROM favorites;

# Salir
\q
```

---

## 🎯 COMANDOS ÚTILES

```bash
# Detener todo
docker-compose down

# Iniciar todo
docker-compose up -d

# Reiniciar un servicio específico
docker-compose restart recipe-service

# Ver estado de contenedores
docker-compose ps

# Limpiar todo (CUIDADO: borra datos)
docker-compose down -v

# Reconstruir servicios (después de cambios en código)
docker-compose up -d --build
```

---

## 📝 CHECKLIST FINAL

Marca cada item cuando lo completes:

- [ ] Docker Desktop instalado y corriendo
- [ ] Token de Telegram obtenido de @BotFather
- [ ] Archivo `.env` configurado con el token
- [ ] Servicios Docker iniciados (`docker-compose up -d`)
- [ ] Todos los contenedores "Up" (`docker-compose ps`)
- [ ] n8n accesible en http://localhost:5678
- [ ] Workflow importado en n8n
- [ ] Credenciales de Telegram configuradas en n8n
- [ ] Workflow activado (toggle "Active" = ON)
- [ ] ngrok instalado y corriendo
- [ ] Webhook de Telegram configurado
- [ ] Bot responde al comando `/start`
- [ ] Búsqueda de recetas funciona (`/buscar chicken`)
- [ ] Favoritos funcionan (`/favoritos`)

---

## 🎉 ¡LISTO!

Si completaste todos los pasos, tu Chef Bot debería estar funcionando perfectamente.

### Próximos Pasos:

1. Personaliza los mensajes del bot editando el workflow en n8n
2. Agrega más comandos personalizados
3. Ajusta los filtros dietéticos
4. Configura un servidor público (en lugar de ngrok) para producción

### ¿Necesitas Ayuda?

- Revisa los logs: `docker-compose logs -f`
- Verifica el README.md principal
- Consulta la documentación de n8n: https://docs.n8n.io
- Revisa la API de Telegram: https://core.telegram.org/bots/api

---

**Creado con ❤️ para Chef Bot**
