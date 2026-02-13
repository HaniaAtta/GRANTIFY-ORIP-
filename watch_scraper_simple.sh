#!/bin/bash
# Simple, reliable scraper monitor

echo "=========================================="
echo "📊 Scraper Monitor"
echo "=========================================="
echo ""

# First, check if scraper is running
echo "1️⃣ Checking if scraper is running..."
CELERY_STATUS=$(docker-compose ps celery 2>/dev/null | grep -q "Up" && echo "running" || echo "not running")
echo "   Celery: $CELERY_STATUS"

FASTAPI_STATUS=$(docker-compose ps fastapi 2>/dev/null | grep -q "Up" && echo "running" || echo "not running")
echo "   FastAPI: $FASTAPI_STATUS"
echo ""

# Show current database status
echo "2️⃣ Current Database Status:"
python3 << 'PYTHON_SCRIPT'
from datetime import datetime, timedelta
from models.db_helper import get_grant_sites

try:
    grants = get_grant_sites()
    total = len(grants)
    
    # Get recently updated
    recent = [g for g in grants if g.last_updated and g.last_updated > datetime.utcnow() - timedelta(hours=1)]
    
    open_count = sum(1 for g in grants if g.status == "open")
    closed_count = sum(1 for g in grants if g.status == "closed")
    
    print(f"   Total Grants: {total}")
    print(f"   Updated (last hour): {len(recent)}")
    print(f"   Open: {open_count} | Closed: {closed_count}")
    
    if recent:
        print(f"\n   Recently Updated:")
        for g in sorted(recent, key=lambda x: x.last_updated, reverse=True)[:5]:
            url_short = (g.url[:50] + "...") if len(g.url) > 50 else g.url
            time_ago = (datetime.utcnow() - g.last_updated).total_seconds() / 60
            print(f"     [{time_ago:.1f}m] {url_short} → {g.status}")
except Exception as e:
    print(f"   Error: {e}")
PYTHON_SCRIPT

echo ""
echo "3️⃣ Watching logs (Press Ctrl+C to stop)..."
echo "=========================================="
echo ""

# Watch logs - show everything related to scraping
docker-compose logs -f fastapi 2>&1 | while IFS= read -r line; do
    # Show any line with scraper-related keywords
    if echo "$line" | grep -qiE "(scraper|scraping|grant|ai|classification|finished|error|starting)"; then
        # Extract timestamp if available
        timestamp=$(echo "$line" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' | head -1)
        
        # Format based on content
        if echo "$line" | grep -qi "starting scraper\|scraping"; then
            url=$(echo "$line" | grep -oE 'https?://[^\s<>"]+' | head -1)
            if [ ! -z "$url" ]; then
                echo "🔄 [$timestamp] Scraping: ${url:0:70}..."
            else
                echo "🔄 $line"
            fi
        elif echo "$line" | grep -qi "finished\|completed"; then
            url=$(echo "$line" | grep -oE 'https?://[^\s<>"]+' | head -1)
            if [ ! -z "$url" ]; then
                echo "✅ [$timestamp] Completed: ${url:0:70}..."
            else
                echo "✅ $line"
            fi
        elif echo "$line" | grep -qi "ai classification successful"; then
            echo "   🤖 GPT: Success"
        elif echo "$line" | grep -qi "ai classification failed\|quota"; then
            echo "   ⚠️  GPT: Failed (using fallback)"
        elif echo "$line" | grep -qi "error"; then
            echo "❌ $line"
        else
            # Show other relevant lines
            echo "$line"
        fi
    fi
done

