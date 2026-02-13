#!/bin/bash
# Update API key and restart everything

export OPENAI_API_KEY=${OPENAI_API_KEY}
echo "=========================================="
echo "Updating API Key and Restarting Services"
echo "=========================================="
echo ""

# 1. Update .env file
echo "1️⃣ Updating .env file..."
if [ ! -f .env ]; then
    echo "Creating .env file..."
    echo "OPENAI_API_KEY=$NEW_API_KEY" > .env
else
    # Update existing .env
    if grep -q "^OPENAI_API_KEY=" .env; then
        # Replace existing key
        sed -i.bak "s|^OPENAI_API_KEY=.*|OPENAI_API_KEY=$NEW_API_KEY|" .env
        echo "✅ Updated existing OPENAI_API_KEY in .env"
    else
        # Add new key
        echo "OPENAI_API_KEY=$NEW_API_KEY" >> .env
        echo "✅ Added OPENAI_API_KEY to .env"
    fi
fi

echo "✅ API key updated in .env"
echo ""

# 2. Verify .env
echo "2️⃣ Verifying .env file..."
if grep -q "^OPENAI_API_KEY=$NEW_API_KEY" .env; then
    echo "✅ API key correctly set in .env"
    echo "   Key: ${NEW_API_KEY:0:15}..."
else
    echo "❌ Failed to update .env file"
    exit 1
fi
echo ""

# 3. Test API key locally
echo "3️⃣ Testing new API key..."
python3 << 'PYTHON_SCRIPT'
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

env_path = Path('.env')
load_dotenv(dotenv_path=env_path)
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    print("❌ Could not load API key")
    sys.exit(1)

print(f"✅ Loaded key: {api_key[:15]}...")

try:
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': 'Say OK'}],
        max_tokens=5
    )
    print(f"✅ API KEY WORKS! Response: {response.choices[0].message.content}")
except Exception as e:
    error_str = str(e)
    if 'quota' in error_str.lower() or '429' in error_str:
        print(f"❌ API QUOTA EXCEEDED: {error_str[:100]}")
        sys.exit(1)
    else:
        print(f"❌ API Error: {error_str[:100]}")
        sys.exit(1)
PYTHON_SCRIPT

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ API key test failed. Stopping."
    exit 1
fi

echo ""

# 4. Restart Docker services
echo "4️⃣ Restarting Docker services..."
docker-compose down
echo "✅ Services stopped"
docker-compose up -d
echo "✅ Services started"
echo ""

# 5. Wait for services
echo "5️⃣ Waiting for services to be ready..."
sleep 8
echo "✅ Services should be ready"
echo ""

# 6. Verify API key in Docker
echo "6️⃣ Verifying API key in Docker..."
DOCKER_KEY=$(docker-compose exec -T fastapi printenv OPENAI_API_KEY 2>/dev/null | head -1 || echo "")
if [ -z "$DOCKER_KEY" ]; then
    echo "⚠️  Could not verify Docker key (service might still be starting)"
else
    if [ "$NEW_API_KEY" = "$DOCKER_KEY" ]; then
        echo "✅ Docker has correct API key"
    else
        echo "⚠️  Docker key doesn't match (might need more time)"
    fi
fi
echo ""

# 7. Check status endpoint
echo "7️⃣ Checking scraper status..."
sleep 2
STATUS=$(curl -s http://localhost:8000/api/scraper-status 2>/dev/null)
if [ -z "$STATUS" ]; then
    echo "⚠️  Status endpoint not responding yet (service might still be starting)"
    echo "   Wait a few more seconds and check manually:"
    echo "   curl http://localhost:8000/api/scraper-status"
else
    echo "$STATUS" | python3 -m json.tool 2>/dev/null || echo "$STATUS"
fi
echo ""

# 8. Run scraper
echo "8️⃣ Starting scraper..."
SCRAPE_RESPONSE=$(curl -s -X POST http://localhost:8000/api/scrape_all 2>/dev/null)
if [ -z "$SCRAPE_RESPONSE" ]; then
    echo "⚠️  Scraper endpoint not responding yet"
    echo "   Try manually: curl -X POST http://localhost:8000/api/scrape_all"
else
    echo "$SCRAPE_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$SCRAPE_RESPONSE"
    echo ""
    echo "✅ Scraper started!"
fi

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Monitor scraping progress:"
echo "  docker-compose logs -f fastapi | grep -E '(✅|❌|Scraper|AI)'"
echo ""
echo "Check status:"
echo "  curl http://localhost:8000/api/scraper-status | python3 -m json.tool"
echo ""

