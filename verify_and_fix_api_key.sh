#!/bin/bash
# Script to verify and fix API key loading

echo "=========================================="
echo "Verifying API Key Configuration"
echo "=========================================="
echo ""

# 1. Check .env file
echo "1. Checking .env file..."
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    exit 1
fi

echo "✅ .env file exists"
API_KEY_IN_FILE=$(grep "^OPENAI_API_KEY=" .env | cut -d'=' -f2- | tr -d '"' | tr -d "'")
if [ -z "$API_KEY_IN_FILE" ]; then
    echo "❌ OPENAI_API_KEY not found in .env"
    exit 1
fi

echo "✅ API key found in .env: ${API_KEY_IN_FILE:0:10}..."
echo ""

# 2. Check what Docker sees
echo "2. Checking what Docker container sees..."
DOCKER_KEY=$(docker-compose exec -T fastapi env 2>/dev/null | grep OPENAI_API_KEY | cut -d'=' -f2- || echo "NOT_FOUND")
if [ "$DOCKER_KEY" = "NOT_FOUND" ] || [ -z "$DOCKER_KEY" ]; then
    echo "⚠️  Docker container doesn't see API key"
    echo "   This might be because container needs full restart"
else
    echo "✅ Docker sees API key: ${DOCKER_KEY:0:10}..."
    if [ "$API_KEY_IN_FILE" != "$DOCKER_KEY" ]; then
        echo "⚠️  WARNING: .env key differs from Docker key!"
        echo "   .env: ${API_KEY_IN_FILE:0:10}..."
        echo "   Docker: ${DOCKER_KEY:0:10}..."
    fi
fi
echo ""

# 3. Test API key directly
echo "3. Testing API key from .env file..."
cd "$(dirname "$0")"  # Change to script directory
python3 << EOF
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Load from current directory
load_dotenv(dotenv_path='.env')
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    print("❌ API key not loaded from .env")
    exit(1)

print(f"✅ API key loaded: {api_key[:10]}...")

try:
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': 'Say OK'}],
        max_tokens=5
    )
    print(f"✅ API key is WORKING!")
    print(f"   Response: {response.choices[0].message.content}")
except Exception as e:
    error_str = str(e)
    if 'quota' in error_str.lower() or '429' in error_str or 'insufficient_quota' in error_str:
        print("❌ API QUOTA EXCEEDED")
        print("   The new API key also has quota issues")
        print("   Please get a different API key with available credits")
    else:
        print(f"❌ API Error: {error_str}")
EOF

echo ""
echo "=========================================="
echo "Recommendations:"
echo "=========================================="
echo ""
echo "If API key works locally but Docker shows old key:"
echo "  1. docker-compose down"
echo "  2. docker-compose up -d"
echo ""
echo "If API key has quota issues:"
echo "  1. Get a new API key from: https://platform.openai.com/api-keys"
echo "  2. Make sure it has credits/quota"
echo "  3. Update .env file"
echo "  4. docker-compose down && docker-compose up -d"
echo ""

