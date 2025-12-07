# 🚀 INICIAR CHEF BOT - GUÍA RÁPIDA

Tu token ya está configurado. Sigue estos pasos para iniciar el bot:

## 📋 PASOS RÁPIDOS (15 minutos)

### 1️⃣ Iniciar Docker y Servicios (5 min)

```bash
# Asegúrate de estar en la carpeta del proyecto
cd /Users/tagle/Documents/Asistente_cocina

# Inicia todos los servicios con Docker
docker-compose up -d

# Espera 30 segundos a que todo esté listo
sleep 30

# Verifica que todo esté corriendo
docker-compose ps
```

Deberías ver 6 contenedores "Up":
- ✅ chef_postgres
- ✅ chef_redis
- ✅ chef_api_gateway
- ✅ chef_recipe_service
- ✅ chef_user_service
- ✅ chef_n8n

---

### 2️⃣ Configurar n8n (5 min)

1. **Abre n8n en tu navegador:**
   ```
   http://localhost:5678
   ```

2. **Si aparece un formulario de registro, completa:**
   - Email: `admin@chefbot.local`
   - First Name: `Admin`
   - Last Name: `ChefBot`
   - Password: `n8n_admin_123`

   **Si aparece login directo, usa:**
   - Email: `admin@chefbot.local`
   - Password: `Admin_123`

3. **Importar el workflow:**

   **OPCIÓN A - Importar desde archivo (Recomendado):**
   - Presiona `Cmd+O` (Mac) o `Ctrl+O` (Windows/Linux)
   - O busca en la barra lateral un ícono de menú (⋮ o ≡)
   - Selecciona "Import from File" o "Import Workflow"
   - Navega y selecciona: `n8n/workflows/telegram-chef-bot.json`
   - El workflow se importará automáticamente

   **OPCIÓN B - Si la importación no funciona:**

   Por ahora, vamos a crear un workflow simple de prueba:

   1. Haz clic en **"Start from scratch"**
   2. Agrega un nodo "Webhook" desde el menú de nodos
   3. Configura el webhook:
      - **Webhook Path**: `telegram`
      - **HTTP Method**: `POST`
   4. Guarda el workflow con el nombre: "Telegram Chef Bot"
   5. Activa el workflow (toggle en la esquina superior derecha)

   **NOTA:** Este es un workflow básico temporal. Más adelante completaremos la configuración completa.

4. **Configurar credenciales de Telegram:**
   - Busca el nodo "Telegram Trigger" (primer nodo a la izquierda)
   - Haz clic en él
   - En la sección "Credential to connect with", haz clic en "Create New"
   - Nombre: `Telegram Bot API`
   - Access Token: `8490991086:AAGpb9jjfUWpdxbR8n6wfxmYB988KM6I0v0`
   - Haz clic en "Save"

5. **Activar el workflow:**
   - En la esquina superior derecha, activa el toggle "Active" (debe ponerse verde)
   - Guarda el workflow con Ctrl+S o Cmd+S

---

### 3️⃣ Instalar y Configurar ngrok (3 min)

**¿Qué es ngrok?** Es una herramienta que permite que Telegram (que está en internet) pueda enviar mensajes a tu computadora (que está en tu red local).

```bash
# Instalar ngrok (si no lo tienes)
brew install ngrok

# O descarga desde: https://ngrok.com/download

# Iniciar ngrok (DEJA ESTA TERMINAL ABIERTA)
ngrok http 5678
```

Verás algo como:
```
Forwarding    https://abc123xyz.ngrok.io -> http://localhost:5678
```

**COPIA LA URL HTTPS** (ejemplo: `https://abc123xyz.ngrok.io`)

---

### 4️⃣ Configurar el Webhook de Telegram (2 min)

**Reemplaza `<NGROK_URL>` con tu URL de ngrok:**

```bash
curl "https://api.telegram.org/bot8490991086:AAGpb9jjfUWpdxbR8n6wfxmYB988KM6I0v0/setWebhook?url=https://abc123xyz.ngrok.io/webhook/telegram"
```

**Ejemplo real (reemplaza la URL):**
```bash
curl "https://api.telegram.org/bot8490991086:AAGpb9jjfUWpdxbR8n6wfxmYB988KM6I0v0/setWebhook?url=https://1234-56-789.ngrok.io/webhook/telegram"
```

Deberías recibir:
```json
{"ok":true,"result":true,"description":"Webhook was set"}
```

---

### 5️⃣ ¡PROBAR EL BOT! 🎉

1. **Abre Telegram en tu teléfono o computadora**

2. **Busca tu bot:**
   - Haz clic en el ícono de búsqueda
   - Busca el nombre/username que le diste al bot cuando lo creaste con @BotFather

3. **Inicia una conversación:**
   ```
   /start
   ```

4. **Prueba estos comandos:**

   ```
   /ayuda
   → Ver todos los comandos disponibles

   /buscar chicken
   → Buscar recetas con pollo

   /buscar chicken rice
   → Buscar recetas con pollo y arroz

   /recomendar
   → Obtener recomendaciones de recetas

   /favoritos
   → Ver tus recetas favoritas (vacío al inicio)

   /filtro
   → Cambiar filtro dietético (vegetariano, vegano, sin gluten)

   /convertir 2 tazas a ml
   → Convertir medidas de cocina
   ```

---

## 🔍 VERIFICAR QUE TODO FUNCIONA

### Ver las ejecuciones en n8n:

1. Ve a n8n: http://localhost:5678
2. Abre el workflow "Chef Bot - Telegram Workflow Completo"
3. En la esquina superior derecha verás "Executions"
4. Cada vez que envíes un mensaje al bot, verás una nueva ejecución

### Ver logs de los servicios:

```bash
# Ver todos los logs
docker-compose logs -f

# Ver solo n8n
docker-compose logs -f n8n

# Ver solo recipe-service
docker-compose logs -f recipe-service
```

### Probar la API directamente:

```bash
# Health check de Recipe Service
curl http://localhost:3001/health

# Buscar recetas
curl -X POST http://localhost:3001/api/v1/recipes/search \
  -H "Content-Type: application/json" \
  -d '{"ingredients": ["chicken"]}'
```

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### El bot no responde:

1. **Verifica que ngrok esté corriendo:**
   ```bash
   # En la terminal donde ejecutaste ngrok, debe seguir activo
   ```

2. **Verifica el webhook:**
   ```bash
   curl "https://api.telegram.org/bot8490991086:AAGpb9jjfUWpdxbR8n6wfxmYB988KM6I0v0/getWebhookInfo"
   ```
   Debe mostrar tu URL de ngrok

3. **Verifica que el workflow esté activo en n8n:**
   - Ve a http://localhost:5678
   - El workflow debe tener el toggle "Active" en verde

### Error en los servicios:

```bash
# Ver logs del servicio problemático
docker-compose logs recipe-service
docker-compose logs user-service
docker-compose logs n8n

# Reiniciar un servicio específico
docker-compose restart recipe-service

# Reiniciar todo
docker-compose restart
```

### Base de datos no responde:

```bash
# Reiniciar PostgreSQL
docker-compose restart postgres

# Ver logs
docker-compose logs postgres
```

---

## 🛑 DETENER TODO

Cuando quieras parar el bot:

```bash
# Detener todos los servicios
docker-compose down

# Detener ngrok (Ctrl+C en la terminal donde está corriendo)
```

---

## 🔄 REINICIAR EL BOT

La próxima vez que quieras usar el bot:

```bash
# 1. Iniciar servicios
docker-compose up -d

# 2. Iniciar ngrok (en otra terminal)
ngrok http 5678

# 3. Configurar webhook con la NUEVA URL de ngrok
curl "https://api.telegram.org/bot8490991086:AAGpb9jjfUWpdxbR8n6wfxmYB988KM6I0v0/setWebhook?url=https://NUEVA-URL.ngrok.io/webhook/telegram"

# 4. ¡Listo! Usa el bot en Telegram
```

**NOTA:** Cada vez que reinicies ngrok, la URL cambia, así que tienes que volver a configurar el webhook.

---

## 📊 MONITOREO

### Dashboard de servicios:

- **n8n:** http://localhost:5678
- **API Gateway:** http://localhost:3000/health
- **Recipe Service:** http://localhost:3001/health
- **User Service:** http://localhost:3002/health

### Base de datos (opcional):

```bash
# Conectarse a PostgreSQL
docker exec -it chef_postgres psql -U chef_user -d chef_db

# Ver usuarios registrados
SELECT * FROM users;

# Ver favoritos
SELECT * FROM favorites;

# Salir
\q
```

---

## ✅ CHECKLIST DE VERIFICACIÓN

Antes de probar el bot, verifica:

- [ ] Docker Desktop está corriendo
- [ ] `docker-compose ps` muestra 6 contenedores "Up"
- [ ] n8n accesible en http://localhost:5678
- [ ] Workflow importado y activo en n8n
- [ ] Credenciales de Telegram configuradas en n8n
- [ ] ngrok está corriendo y muestra una URL HTTPS
- [ ] Webhook configurado con la URL de ngrok
- [ ] Bot responde a `/start` en Telegram

---

## 🎯 COMANDOS ÚTILES

```bash
# Estado de contenedores
docker-compose ps

# Logs en tiempo real
docker-compose logs -f

# Reiniciar todo
docker-compose restart

# Limpiar y empezar de nuevo
docker-compose down
docker-compose up -d

# Ver uso de recursos
docker stats
```

---

## 📞 ¿NECESITAS AYUDA?

Si algo no funciona:

1. Revisa los logs: `docker-compose logs -f`
2. Verifica el webhook: `curl "https://api.telegram.org/bot8490991086:AAGpb9jjfUWpdxbR8n6wfxmYB988KM6I0v0/getWebhookInfo"`
3. Lee la guía completa: `SETUP_COMPLETO.md`
4. Revisa las ejecuciones en n8n: http://localhost:5678

---

**¡Tu Chef Bot está listo para cocinar! 👨‍🍳🍳**
