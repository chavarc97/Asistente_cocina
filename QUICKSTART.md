# 🚀 Quick Start Guide - Chef Bot

## Prerequisites

Before starting, ensure you have:

- ✅ Docker & Docker Compose installed
- ✅ Telegram account
- ✅ Bot token from @BotFather
- ✅ ngrok (for local development)

## 🎯 Step-by-Step Setup

### 1. Configure Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your Telegram bot token
nano .env
```

**Important variables to update:**
```bash
TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
```

### 2. Start the Services

```bash
# Start all services with Docker Compose
docker-compose up -d

# Check services are running
docker-compose ps
```

**Expected services:**
- ✅ postgres (port 5432)
- ✅ redis (port 6379)
- ✅ api-gateway (port 3000)
- ✅ recipe-service (port 3001)
- ✅ n8n (port 5678)

### 3. Initialize Database

The database will be automatically initialized with the schema from `database/init.sql` on first startup.

**Verify database:**
```bash
docker-compose exec postgres psql -U chef_user -d chef_db -c "\dt"
```

### 4. Setup ngrok for Telegram Webhook (Development)

```bash
# In a new terminal, start ngrok
ngrok http 5678

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

### 5. Configure n8n

1. Open n8n in browser: `http://localhost:5678`
2. Create admin account (first time only)
3. Import workflow:
   - Go to Workflows → Import from File
   - Select `n8n/workflows/telegram-chef-bot.json`
4. Configure Telegram credentials:
   - Add your bot token in Telegram node
   - Update webhook URL with your ngrok URL

### 6. Set Telegram Webhook

```bash
# Replace with your ngrok URL and bot token
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=<YOUR_NGROK_URL>/webhook/telegram"

# Verify webhook is set
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

### 7. Test Your Bot

Open Telegram and:
1. Search for your bot
2. Send `/start`
3. Try `/buscar pollo tomate`

## 📊 Service Endpoints

### API Gateway
- Health: `http://localhost:3000/health`
- API Docs: `http://localhost:3000/docs`

### Recipe Service
- Health: `http://localhost:3001/health`
- API Docs: `http://localhost:3001/docs`
- Search: `POST http://localhost:3001/api/v1/recipes/search`

### n8n
- Dashboard: `http://localhost:5678`

## 🔍 Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs -f

# Restart specific service
docker-compose restart recipe-service
```

### Database connection errors
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection
docker-compose exec postgres psql -U chef_user -d chef_db
```

### Redis connection errors
```bash
# Check Redis is running
docker-compose exec redis redis-cli ping
# Should return: PONG
```

### Telegram webhook not working
```bash
# Check ngrok is running
curl https://your-ngrok-url.ngrok.io

# Verify webhook status
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
```

## 🧪 Testing Endpoints Manually

### Search Recipes
```bash
curl -X POST http://localhost:3001/api/v1/recipes/search \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": ["chicken", "tomato"],
    "dietary_filter": "none"
  }'
```

### Get Recipe Details
```bash
curl http://localhost:3001/api/v1/recipes/52940
```

### Get Random Recipe
```bash
curl http://localhost:3001/api/v1/recipes/random
```

## 📝 Development Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f recipe-service
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific
docker-compose restart recipe-service api-gateway
```

### Stop Services
```bash
docker-compose down

# Stop and remove volumes (cleans database)
docker-compose down -v
```

### Rebuild Services
```bash
# Rebuild all
docker-compose build

# Rebuild specific
docker-compose build recipe-service
```

## 🎨 Bot Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Initialize bot | `/start` |
| `/buscar [ingredients]` | Search recipes | `/buscar pollo arroz` |
| `/favoritos` | View favorites | `/favoritos` |
| `/filtro` | Change dietary filter | `/filtro` |
| `/recomendar` | Get recommendations | `/recomendar` |
| `/ayuda` | Show help | `/ayuda` |

## 🔐 Security Notes

⚠️ **Before production:**

1. Change database passwords in `.env`
2. Update `JWT_SECRET` with secure random string
3. Update n8n admin credentials
4. Set proper `ALLOWED_ORIGINS` for CORS
5. Use HTTPS for all endpoints
6. Never commit `.env` file to git

## 📚 Next Steps

1. ✅ Complete n8n workflow implementation
2. ✅ Add more conversation flows
3. ✅ Implement advanced recommendations
4. ✅ Add user analytics
5. ✅ Deploy to production (Railway, Render, etc.)

## 🆘 Need Help?

Check the documentation:
- 📖 [README.md](README.md)
- 📋 [API Documentation](docs/API.md)
- 🏗️ [Architecture Design](docs/diseno-sw-bot-telegram.md)

---

**Happy Cooking! 🍳**
