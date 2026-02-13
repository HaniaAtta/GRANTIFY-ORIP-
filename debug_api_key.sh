#!/bin/bash
# Debug script to find out why API key still shows quota error

echo "=========================================="
echo "🔍 Debugging API Key Issue"
echo "=========================================="
echo ""

# 1. Check what's in .env
echo "1️⃣ Checking .env file..."
API_KEY_IN_ENV=$(grep "^OPENAI_API_KEY=" .env | cut -d'=' -f2- | tr -d '"' | tr -d "'" | tr -d ' ')
if [ -z "$API_KEY_IN_ENV" ]; then
    echo "❌ No API key found in .env"
    exit 1
fi
echo "✅ .env has: ${API_KEY_IN_ENV:0:15}..."
echo ""

# 2. Check what Docker sees
echo "2️⃣ Checking what Docker container sees..."
DOCKER_KEY=$(docker-compose exec -T fastapi printenv OPENAI_API_KEY 2>/dev/null | head -1 || echo "")
if [ -z "$DOCKER_KEY" ]; then
    echo "⚠️  Docker container doesn't see API key (might need restart)"
else
    echo "✅ Docker sees: ${DOCKER_KEY:0:15}..."
    if [ "$API_KEY_IN_ENV" != "$DOCKER_KEY" ]; then
        echo "⚠️  MISMATCH! .env and Docker have different keys!"
        echo "   .env: ${API_KEY_IN_ENV:0:15}..."
        echo "   Docker: ${DOCKER_KEY:0:15}..."
    else
        echo "✅ Keys match"
    fi
fi
echo ""

# 3. Test the API key directly (from .env, not Docker)
echo "3️⃣ Testing API key from .env file directly..."
cd "$(dirname "$0")"
python3 << 'PYTHON_SCRIPT'
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load .env
env_path = Path('.env')
load_dotenv(dotenv_path=env_path)
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    print("❌ Could not load API key from .env")
    sys.exit(1)

print(f"✅ Loaded key: {api_key[:15]}...")
print("")

try:
    client = OpenAI(api_key=api_key)
    print("🧪 Testing API call...")
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': 'Say OK'}],
        max_tokens=5
    )
    print(f"✅ API KEY WORKS! Response: {response.choices[0].message.content}")
    print("")
    print("💡 The key works locally, but Docker might be using old key")
    print("   Solution: docker-compose down && docker-compose up -d")
except Exception as e:
    error_str = str(e)
    print(f"❌ API Error: {error_str[:200]}")
    if 'quota' in error_str.lower() or '429' in error_str or 'insufficient_quota' in error_str:
        print("")
        print("⚠️  This API key ALSO has quota issues!")
        print("")
        print("Possible reasons:")
        print("  1. Free tier keys have very limited quota")
        print("  2. The key was already used up")
        print("  3. You need a paid account for more quota")
        print("")
        print("💡 Solutions:")
        print("  - Get a NEW key from a different OpenAI account")
        print("  - Or add credits to your OpenAI account")
        print("  - Or use a paid API key")
    else:
        print(f"   Full error: {error_str}")
PYTHON_SCRIPT

echo ""
echo "=========================================="
echo "4️⃣ Recommendations:"
echo "=========================================="
echo ""

# Check if keys match
if [ ! -z "$DOCKER_KEY" ] && [ "$API_KEY_IN_ENV" != "$DOCKER_KEY" ]; then
    echo "🔧 FIX: Keys don't match! Do full restart:"
    echo "   docker-compose down"
    echo "   docker-compose up -d"
    echo ""
fi

echo "If API key works locally but Docker shows error:"
echo "   → docker-compose down && docker-compose up -d"
echo ""
echo "If API key has quota issues:"
echo "   → Get a NEW key with credits"
echo "   → Or add credits to OpenAI account"
echo ""

