#!/bin/bash

# ==============================================
# CHEF BOT - QUICK START SCRIPT
# Script rápido para iniciar el proyecto
# ==============================================

set -e  # Exit on error

echo "Chef Bot - Quick Start"
echo "=========================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}Archivo .env no encontrado${NC}"
    echo "Copiando .env.example a .env..."
    cp .env.example .env
    echo -e "${YELLOW}Por favor configura tu TELEGRAM_BOT_TOKEN en .env${NC}"
    exit 1
fi

# Check if TELEGRAM_BOT_TOKEN is configured
if grep -q "YOUR_TELEGRAM_BOT_TOKEN_HERE" .env; then
    echo -e "${RED}TELEGRAM_BOT_TOKEN no configurado${NC}"
    echo ""
    echo "Pasos para obtener tu token:"
    echo "1. Abre Telegram y busca @BotFather"
    echo "2. Envía /newbot y sigue las instrucciones"
    echo "3. Copia el token que te da"
    echo "4. Edita .env y reemplaza YOUR_TELEGRAM_BOT_TOKEN_HERE con tu token"
    echo ""
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Docker no está corriendo${NC}"
    echo "Por favor inicia Docker Desktop y vuelve a intentar"
    exit 1
fi

echo -e "${GREEN}Docker está corriendo${NC}"

# Check if docker-compose exists
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}docker-compose no encontrado${NC}"
    echo "Por favor instala docker-compose"
    exit 1
fi

echo -e "${GREEN}docker-compose encontrado${NC}"
echo ""

# Start services
echo "Iniciando servicios..."
echo ""

docker-compose down 2>/dev/null || true
docker-compose up -d

echo ""
echo "Esperando a que los servicios estén listos..."
sleep 10

# Check service health
echo ""
echo "Verificando servicios..."
echo ""

# Check PostgreSQL
if docker-compose ps | grep -q "chef_postgres.*Up"; then
    echo -e "${GREEN}PostgreSQL está corriendo${NC}"
else
    echo -e "${RED}PostgreSQL no está corriendo${NC}"
fi

# Check Redis
if docker-compose ps | grep -q "chef_redis.*Up"; then
    echo -e "${GREEN}Redis está corriendo${NC}"
else
    echo -e "${RED}Redis no está corriendo${NC}"
fi

# Check API Gateway
if docker-compose ps | grep -q "chef_api_gateway.*Up"; then
    echo -e "${GREEN}API Gateway está corriendo${NC}"
else
    echo -e "${RED}API Gateway no está corriendo${NC}"
fi

# Check Recipe Service
if docker-compose ps | grep -q "chef_recipe_service.*Up"; then
    echo -e "${GREEN}Recipe Service está corriendo${NC}"
else
    echo -e "${RED}Recipe Service no está corriendo${NC}"
fi

# Check User Service
if docker-compose ps | grep -q "chef_user_service.*Up"; then
    echo -e "${GREEN}User Service está corriendo${NC}"
else
    echo -e "${RED}User Service no está corriendo${NC}"
fi

# Check n8n
if docker-compose ps | grep -q "chef_n8n.*Up"; then
    echo -e "${GREEN}n8n está corriendo${NC}"
else
    echo -e "${RED}n8n no está corriendo${NC}"
fi

echo ""
echo "================================================"
echo -e "${GREEN}Servicios iniciados!${NC}"
echo "================================================"
echo ""
echo "Próximos pasos:"
echo ""
echo "1. Accede a n8n: http://localhost:5678"
echo "   Usuario: admin"
echo "   Contraseña: n8n_admin_123"
echo ""
echo "2. Importa el workflow:"
echo "   - Menú → Import from File"
echo "   - Selecciona: n8n/workflows/telegram-chef-bot.json"
echo ""
echo "3. Configura las credenciales de Telegram en n8n"
echo ""
echo "4. Activa el workflow (toggle Active = ON)"
echo ""
echo "5. Instala ngrok:"
echo "   brew install ngrok"
echo ""
echo "6. Inicia ngrok:"
echo "   ngrok http 5678"
echo ""
echo "7. Configura el webhook de Telegram:"
echo "   (Reemplaza <TOKEN> y <NGROK_URL>)"
echo '   curl "https://api.telegram.org/bot<TOKEN>/setWebhook?url=<NGROK_URL>/webhook/telegram"'
echo ""
echo "8. Prueba tu bot en Telegram!"
echo ""
echo "================================================"
echo ""
echo "Para ver logs:"
echo "  docker-compose logs -f"
echo ""
echo "Para detener:"
echo "  docker-compose down"
echo ""
echo "Para ayuda completa, lee: SETUP_COMPLETO.md"
echo ""
