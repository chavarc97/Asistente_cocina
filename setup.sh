#!/bin/bash

echo "=================================="
echo "Chef Personal - Setup Script"
echo "=================================="
echo ""

echo "🔍 Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ $PYTHON_VERSION encontrado"
else
    echo "✗ Python 3 no encontrado. Por favor instálalo primero."
    exit 1
fi

echo ""
echo "🔍 Verificando entorno virtual..."
if [ ! -d "venv" ]; then
    echo "⚙️  Creando entorno virtual..."
    python3 -m venv venv
    echo "✓ Entorno virtual creado"
else
    echo "✓ Entorno virtual ya existe"
fi

echo ""
echo "📦 Instalando dependencias..."
./venv/bin/pip install -q --upgrade pip
./venv/bin/pip install -q -r requirements.txt
echo "✓ Dependencias instaladas"

echo ""
echo "🔍 Verificando AWS CLI..."
if command -v aws &> /dev/null; then
    AWS_VERSION=$(aws --version)
    echo "✓ $AWS_VERSION"

    echo ""
    echo "🔐 Verificando credenciales de AWS..."
    if aws sts get-caller-identity &> /dev/null; then
        echo "✓ Credenciales de AWS configuradas correctamente"

        echo ""
        echo "🗄️  ¿Deseas crear las tablas de DynamoDB? (s/n)"
        read -r response
        if [[ "$response" =~ ^[Ss]$ ]]; then
            ./venv/bin/python infrastructure/dynamodb_setup.py
        fi
    else
        echo "⚠️  Credenciales de AWS no configuradas"
        echo ""
        echo "Para configurarlas ejecuta:"
        echo "  aws configure"
        echo ""
        echo "O usa DynamoDB Local para desarrollo:"
        echo "  docker run -p 8000:8000 amazon/dynamodb-local"
    fi
else
    echo "⚠️  AWS CLI no instalado"
    echo ""
    echo "Instálalo con:"
    echo "  brew install awscli  # macOS"
fi

echo ""
echo "📝 Verificando archivo .env..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ Archivo .env creado desde .env.example"
        echo "⚠️  Por favor edita .env y agrega tu SPOONACULAR_API_KEY"
    fi
else
    echo "✓ Archivo .env existe"
fi

echo ""
echo "=================================="
echo "✅ Setup completado!"
echo "=================================="
echo ""
echo "Para activar el entorno virtual:"
echo "  source venv/bin/activate"
echo ""
echo "Consulta GUIA_INSTALACION.md para más detalles"
