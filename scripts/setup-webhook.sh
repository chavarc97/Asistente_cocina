#!/bin/bash

# ==============================================
# CHEF BOT - SETUP WEBHOOK SCRIPT
# Configura el webhook de Telegram automáticamente
# ==============================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "Chef Bot - Telegram Webhook Setup"
echo "====================================="
echo ""

# Bot token
TOKEN="8490991086:AAGpb9jjfUWpdxbR8n6wfxmYB988KM6I0v0"

# Ask for ngrok URL
echo -e "${YELLOW}Paso 1: Inicia ngrok en otra terminal:${NC}"
echo "  ngrok http 5678"
echo ""
echo -e "${YELLOW}Paso 2: Copia la URL HTTPS que ngrok te da${NC}"
echo "  Ejemplo: https://abc123xyz.ngrok.io"
echo ""
read -p "Ingresa tu URL de ngrok (sin / al final): " NGROK_URL

# Validate URL
if [[ ! "$NGROK_URL" =~ ^https:// ]]; then
    echo -e "${RED}Error: La URL debe empezar con https://${NC}"
    exit 1
fi

# Remove trailing slash if present
NGROK_URL="${NGROK_URL%/}"

WEBHOOK_URL="${NGROK_URL}/webhook/telegram"

echo ""
echo -e "${BLUE}Configurando webhook...${NC}"
echo "URL: $WEBHOOK_URL"
echo ""

# Set webhook
RESPONSE=$(curl -s "https://api.telegram.org/bot${TOKEN}/setWebhook?url=${WEBHOOK_URL}")

# Check response
if echo "$RESPONSE" | grep -q '"ok":true'; then
    echo -e "${GREEN}Webhook configurado exitosamente!${NC}"
    echo ""
    echo "Detalles:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    echo ""
    echo -e "${GREEN}Todo listo! Ahora puedes usar el bot en Telegram${NC}"
    echo ""
    echo "Prueba enviando estos comandos a tu bot:"
    echo "  /start"
    echo "  /buscar chicken"
    echo "  /ayuda"
else
    echo -e "${RED}Error al configurar webhook${NC}"
    echo ""
    echo "Respuesta:"
    echo "$RESPONSE"
    echo ""
    echo "Posibles causas:"
    echo "1. La URL de ngrok no es correcta"
    echo "2. ngrok no está corriendo"
    echo "3. El puerto 5678 no es accesible"
fi

echo ""
echo "Para verificar el webhook actual:"
echo "  curl \"https://api.telegram.org/bot${TOKEN}/getWebhookInfo\""
echo ""
