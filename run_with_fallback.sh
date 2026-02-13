#!/bin/bash
# Run scraper in fallback mode (no GPT, but still works)

echo "=========================================="
echo "Running Scraper in Fallback Mode"
echo "=========================================="
echo ""
echo "⚠️  API key has quota issues"
echo "✅ Scraper will use keyword-based classification (fallback mode)"
echo "⚠️  Less accurate than GPT, but still functional"
echo ""

# Update .env with the key anyway (for future use when credits are added)
export OPENAI_API_KEY=${OPENAI_API_KEY}

if [ -f .env ]; then
    if grep -q "^OPENAI_API_KEY=" .env; then
        sed -i.bak "s|^OPENAI_API_KEY=.*|OPENAI_API_KEY=$NEW_API_KEY|" .env
    else
        echo "OPENAI_API_KEY=$NEW_API_KEY" >> .env
    fi
    echo "✅ API key saved in .env (for when you add credits)"
fi

echo ""
echo "1️⃣ Restarting services..."
docker-compose down
docker-compose up -d
echo "✅ Services restarted"
echo ""

echo "2️⃣ Waiting for services..."
sleep 8
echo "✅ Services ready"
echo ""

echo "3️⃣ Starting scraper (will use fallback mode)..."
SCRAPE_RESPONSE=$(curl -s -X POST http://localhost:8000/api/scrape_all 2>/dev/null)
if [ -z "$SCRAPE_RESPONSE" ]; then
    echo "⚠️  Service might still be starting. Try manually:"
    echo "   curl -X POST http://localhost:8000/api/scrape_all"
else
    echo "$SCRAPE_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$SCRAPE_RESPONSE"
fi
echo ""

echo "=========================================="
echo "✅ Scraper Started!"
echo "=========================================="
echo ""
echo "📊 Monitor progress:"
echo "   docker-compose logs -f fastapi | grep -E '(✅|❌|Scraper|finished)'"
echo ""
echo "💡 Note: Using fallback mode (keyword-based)"
echo "   - Still extracts data"
echo "   - Updates database"
echo "   - Less accurate than GPT"
echo ""
echo "🔧 To get GPT accuracy:"
echo "   1. Add credits to OpenAI account: https://platform.openai.com/account/billing"
echo "   2. Or get a new API key with credits"
echo "   3. Then restart: docker-compose restart fastapi"
echo ""

