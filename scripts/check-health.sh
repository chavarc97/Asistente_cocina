#!/bin/bash

# ==============================================
# CHEF BOT - HEALTH CHECK SCRIPT
# Verifica el estado de todos los servicios
# ==============================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Chef Bot - Health Check"
echo "=========================="
echo ""

# Check Docker containers
echo "Docker Containers:"
echo ""
docker-compose ps
echo ""

# Check API Gateway
echo "API Gateway (Port 3000):"
if curl -s http://localhost:3000/health > /dev/null 2>&1; then
    echo -e "${GREEN}API Gateway está respondiendo${NC}"
    curl -s http://localhost:3000/health | python3 -m json.tool 2>/dev/null || echo "Response OK"
else
    echo -e "${RED}API Gateway no responde${NC}"
fi
echo ""

# Check Recipe Service
echo "Recipe Service (Port 3001):"
if curl -s http://localhost:3001/health > /dev/null 2>&1; then
    echo -e "${GREEN}Recipe Service está respondiendo${NC}"
    curl -s http://localhost:3001/health | python3 -m json.tool 2>/dev/null || echo "Response OK"
else
    echo -e "${RED}Recipe Service no responde${NC}"
fi
echo ""

# Check User Service
echo "User Service (Port 3002):"
if curl -s http://localhost:3002/health > /dev/null 2>&1; then
    echo -e "${GREEN}User Service está respondiendo${NC}"
    curl -s http://localhost:3002/health | python3 -m json.tool 2>/dev/null || echo "Response OK"
else
    echo -e "${RED}User Service no responde${NC}"
fi
echo ""

# Check n8n
echo "n8n (Port 5678):"
if curl -s http://localhost:5678 > /dev/null 2>&1; then
    echo -e "${GREEN}n8n está accesible${NC}"
    echo "URL: http://localhost:5678"
else
    echo -e "${RED}n8n no responde${NC}"
fi
echo ""

# Check PostgreSQL
echo "PostgreSQL (Port 5433):"
if docker exec chef_postgres pg_isready -U chef_user -d chef_db > /dev/null 2>&1; then
    echo -e "${GREEN}PostgreSQL está aceptando conexiones${NC}"
else
    echo -e "${RED}PostgreSQL no está listo${NC}"
fi
echo ""

# Check Redis
echo "Redis (Port 6379):"
if docker exec chef_redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}Redis está respondiendo${NC}"
else
    echo -e "${RED}Redis no responde${NC}"
fi
echo ""

# Check Telegram webhook
echo "Telegram Webhook:"
if [ -f .env ]; then
    TOKEN=$(grep TELEGRAM_BOT_TOKEN .env | cut -d '=' -f2)
    if [ "$TOKEN" != "YOUR_TELEGRAM_BOT_TOKEN_HERE" ] && [ -n "$TOKEN" ]; then
        WEBHOOK_INFO=$(curl -s "https://api.telegram.org/bot${TOKEN}/getWebhookInfo")
        if echo "$WEBHOOK_INFO" | grep -q '"ok":true'; then
            WEBHOOK_URL=$(echo "$WEBHOOK_INFO" | grep -o '"url":"[^"]*"' | cut -d'"' -f4)
            if [ -n "$WEBHOOK_URL" ]; then
                echo -e "${GREEN}Webhook configurado: ${WEBHOOK_URL}${NC}"
            else
                echo -e "${YELLOW}Webhook no configurado${NC}"
                echo "Ejecuta el script setup-webhook.sh"
            fi
        else
            echo -e "${RED}Error al verificar webhook${NC}"
        fi
    else
        echo -e "${YELLOW}Token de Telegram no configurado en .env${NC}"
    fi
else
    echo -e "${RED}Archivo .env no encontrado${NC}"
fi
echo ""

echo "================================================"
echo "Para ver logs detallados:"
echo "  docker-compose logs -f [service-name]"
echo ""
echo "Servicios disponibles:"
echo "  - postgres"
echo "  - redis"
echo "  - api-gateway"
echo "  - recipe-service"
echo "  - user-service"
echo "  - n8n"
echo "================================================"
