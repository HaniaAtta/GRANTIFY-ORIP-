#!/bin/bash
# Install dependencies in virtual environment

echo "=========================================="
echo "Installing Dependencies"
echo "=========================================="
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated"
    echo "Activating HandM virtual environment..."
    source HandM/bin/activate
fi

echo "✅ Virtual environment: $VIRTUAL_ENV"
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found!"
    exit 1
fi

echo "Using: $PYTHON_CMD"
$PYTHON_CMD --version
echo ""

# Check pip
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo "⚠️  pip not found, trying python3 -m pip..."
    PIP_CMD="$PYTHON_CMD -m pip"
fi

echo "Using: $PIP_CMD"
$PIP_CMD --version
echo ""

# Upgrade pip first
echo "📦 Upgrading pip..."
$PIP_CMD install --upgrade pip
echo ""

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "📦 Installing requirements from requirements.txt..."
    $PIP_CMD install -r requirements.txt
    echo ""
    echo "✅ Dependencies installed!"
else
    echo "❌ requirements.txt not found!"
    exit 1
fi

echo ""
echo "=========================================="
echo "Verification"
echo "=========================================="
echo ""

# Test imports
echo "Testing key imports..."
$PYTHON_CMD -c "import sqlalchemy; print('✅ sqlalchemy')" 2>/dev/null || echo "❌ sqlalchemy"
$PYTHON_CMD -c "import fastapi; print('✅ fastapi')" 2>/dev/null || echo "❌ fastapi"
$PYTHON_CMD -c "import celery; print('✅ celery')" 2>/dev/null || echo "❌ celery"
$PYTHON_CMD -c "import redis; print('✅ redis')" 2>/dev/null || echo "❌ redis"
$PYTHON_CMD -c "import bs4; print('✅ beautifulsoup4')" 2>/dev/null || echo "❌ beautifulsoup4"
$PYTHON_CMD -c "import selenium; print('✅ selenium')" 2>/dev/null || echo "❌ selenium"
$PYTHON_CMD -c "import openai; print('✅ openai')" 2>/dev/null || echo "❌ openai"

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. python3 export_json_to_db.py"
echo "  2. python3 -c 'from models.init_db import create_tables; create_tables()'"

