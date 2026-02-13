#!/bin/bash
# Real-time scraper monitoring - shows which websites are being scraped and results

echo "=========================================="
echo "🔍 Scraper Progress Monitor"
echo "=========================================="
echo ""
echo "Watching for scraper activity..."
echo "Press Ctrl+C to stop"
echo ""

# Function to show recent database updates
show_recent_updates() {
    python3 << 'PYTHON_SCRIPT'
import sys
from datetime import datetime, timedelta
from models.db_helper import get_grant_sites

try:
    grants = get_grant_sites()
    recent = [g for g in grants if g.last_updated and g.last_updated > datetime.utcnow() - timedelta(minutes=30)]
    
    if recent:
        print(f"\n📊 Recent Updates (Last 30 min): {len(recent)} grants")
        print("=" * 80)
        for g in sorted(recent, key=lambda x: x.last_updated, reverse=True)[:20]:
            url_short = g.url[:60] + "..." if len(g.url) > 60 else g.url
            status_icon = "✅" if g.status == "open" else "🔴" if g.status == "closed" else "⚠️"
            time_ago = (datetime.utcnow() - g.last_updated).total_seconds() / 60
            print(f"{status_icon} [{time_ago:.1f}m ago] {url_short}")
            print(f"   Status: {g.status} | Categories: {', '.join(g.categories[:3]) if g.categories else 'N/A'}")
            if g.open_date or g.close_date:
                print(f"   Dates: Open: {g.open_date or 'N/A'} | Close: {g.close_date or 'N/A'}")
            print()
    else:
        print("\n⏳ No recent updates yet...")
except Exception as e:
    print(f"\n⚠️  Error checking database: {e}")
PYTHON_SCRIPT
}

# Monitor logs and show updates
docker-compose logs -f fastapi 2>/dev/null | while IFS= read -r line; do
    # Show scraper activity
    if echo "$line" | grep -qE "(Scraper|scraping|AI classification|finished for)"; then
        # Extract and format
        if echo "$line" | grep -q "Starting scraper"; then
            url=$(echo "$line" | grep -oP 'http[s]?://[^\s]+' | head -1)
            if [ ! -z "$url" ]; then
                echo ""
                echo "🔄 Scraping: $url"
            fi
        elif echo "$line" | grep -q "Scraper finished"; then
            url=$(echo "$line" | grep -oP 'http[s]?://[^\s]+' | head -1)
            if [ ! -z "$url" ]; then
                echo "✅ Completed: $url"
            fi
        elif echo "$line" | grep -q "AI classification successful"; then
            echo "   🤖 GPT Analysis: Success"
        elif echo "$line" | grep -q "AI classification failed"; then
            echo "   ⚠️  GPT Analysis: Failed (using fallback)"
        elif echo "$line" | grep -q "Error scraping"; then
            url=$(echo "$line" | grep -oP 'http[s]?://[^\s]+' | head -1)
            if [ ! -z "$url" ]; then
                echo "❌ Error: $url"
            fi
        fi
    fi
    
    # Show database updates every 30 seconds
    if echo "$line" | grep -qE "(INFO|ERROR)"; then
        # Check if it's been 30 seconds since last update
        current_time=$(date +%s)
        if [ -z "$last_update_time" ] || [ $((current_time - last_update_time)) -ge 30 ]; then
            show_recent_updates
            last_update_time=$current_time
        fi
    fi
done

