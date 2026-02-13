#!/bin/bash
# Live scraper monitoring - shows real-time progress

echo "=========================================="
echo "📊 Live Scraper Monitor"
echo "=========================================="
echo ""

# Function to get current progress
get_progress() {
    python3 << 'PYTHON_SCRIPT'
from datetime import datetime, timedelta
from models.db_helper import get_grant_sites

try:
    grants = get_grant_sites()
    total = len(grants)
    
    # Get recently updated (last 10 minutes)
    recent = [g for g in grants if g.last_updated and g.last_updated > datetime.utcnow() - timedelta(minutes=10)]
    updated_count = len(recent)
    
    # Count by status
    open_count = sum(1 for g in grants if g.status == "open")
    closed_count = sum(1 for g in grants if g.status == "closed")
    unknown_count = sum(1 for g in grants if g.status == "unknown")
    
    print(f"📊 Total Grants: {total}")
    print(f"🔄 Updated (last 10 min): {updated_count}")
    print(f"✅ Open: {open_count} | 🔴 Closed: {closed_count} | ⚠️  Unknown: {unknown_count}")
    
    if recent:
        print(f"\n📝 Recently Updated:")
        for g in sorted(recent, key=lambda x: x.last_updated, reverse=True)[:10]:
            url_short = (g.url[:55] + "...") if len(g.url) > 55 else g.url
            time_ago = (datetime.utcnow() - g.last_updated).total_seconds() / 60
            status_icon = "✅" if g.status == "open" else "🔴" if g.status == "closed" else "⚠️"
            print(f"  {status_icon} [{time_ago:.1f}m] {url_short} → {g.status}")
except Exception as e:
    print(f"Error: {e}")
PYTHON_SCRIPT
}

# Watch logs with formatted output
docker-compose logs -f fastapi 2>/dev/null | while IFS= read -r line; do
    # Clear line and show progress every 5 seconds
    current_sec=$(date +%S)
    if [ "$((current_sec % 5))" -eq 0 ]; then
        clear
        echo "=========================================="
        echo "📊 Live Scraper Monitor - $(date '+%H:%M:%S')"
        echo "=========================================="
        echo ""
        get_progress
        echo ""
        echo "📋 Recent Log Activity:"
        echo "----------------------------------------"
    fi
    
    # Show relevant log lines
    if echo "$line" | grep -qE "(Scraper|scraping|AI|finished|Error)"; then
        # Format the line
        timestamp=$(echo "$line" | grep -oP '\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}' | head -1 || echo "")
        
        if echo "$line" | grep -q "Starting scraper"; then
            url=$(echo "$line" | grep -oP 'http[s]?://[^\s]+' | head -1)
            if [ ! -z "$url" ]; then
                echo "🔄 [$timestamp] Scraping: ${url:0:70}..."
            fi
        elif echo "$line" | grep -q "Scraper finished"; then
            url=$(echo "$line" | grep -oP 'http[s]?://[^\s]+' | head -1)
            if [ ! -z "$url" ]; then
                echo "✅ [$timestamp] Completed: ${url:0:70}..."
            fi
        elif echo "$line" | grep -q "AI classification successful"; then
            echo "   🤖 GPT: Success"
        elif echo "$line" | grep -q "AI classification failed"; then
            echo "   ⚠️  GPT: Failed (fallback mode)"
        elif echo "$line" | grep -q "Error scraping"; then
            url=$(echo "$line" | grep -oP 'http[s]?://[^\s]+' | head -1)
            if [ ! -z "$url" ]; then
                echo "❌ [$timestamp] Error: ${url:0:70}..."
            fi
        fi
    fi
done

