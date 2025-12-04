#!/bin/bash

# ==============================================
# BUILD AND START CHEF BOT SERVICES
# ==============================================

set -e

echo "🏗️  Building Chef Bot services..."
echo ""

# Stop any running containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build services
echo ""
echo "🔨 Building Docker images..."
docker-compose build --no-cache

# Start services
echo ""
echo "🚀 Starting services..."
docker-compose up 

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service health
echo ""
echo "🏥 Checking service health..."
echo ""

services=("postgres:5432" "redis:6379" "api-gateway:3000" "recipe-service:3001" "user-service:3002" "n8n:5678")
service_names=("PostgreSQL" "Redis" "API Gateway" "Recipe Service" "User Service" "n8n")

for i in "${!services[@]}"; do
    service="${services[$i]}"
    name="${service_names[$i]}"
    
    if docker-compose ps | grep -q "${service%%:*}"; then
        if docker-compose ps | grep "${service%%:*}" | grep -q "Up"; then
            echo "✅ $name is running"
        else
            echo "❌ $name failed to start"
        fi
    else
        echo "⚠️  $name not found"
    fi
done

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📊 Service URLs:"
echo "  - API Gateway:    http://localhost:3000"
echo "  - Recipe Service: http://localhost:3001"
echo "  - User Service:   http://localhost:3002"
echo "  - n8n:            http://localhost:5678"
echo "  - PostgreSQL:     localhost:5432"
echo "  - Redis:          localhost:6379"
echo ""
echo "💡 Next steps:"
echo "  1. Set up ngrok: ngrok http 5678"
echo "  2. Configure Telegram webhook"
echo "  3. Import n8n workflow from n8n/workflows/"
echo ""
echo "📝 View logs: docker-compose logs -f"
echo "🛑 Stop all:  docker-compose down"
