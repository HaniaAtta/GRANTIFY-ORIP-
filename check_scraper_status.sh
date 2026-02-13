#!/bin/bash
# Quick status check - shows what's happening right now

echo "=========================================="
echo "📊 Quick Scraper Status Check"
echo "=========================================="
echo ""

# Check services
echo "Services:"
docker-compose ps | grep -E "(fastapi|celery|redis)" | awk '{print "  " $1 ": " $4}'
echo ""

# Check database
echo "Database Status:"
python3 << 'PYTHON_SCRIPT'
from datetime import datetime, timedelta
from models.db_helper import get_grant_sites

try:
    grants = get_grant_sites()
    total = len(grants)
    
    recent = [g for g in grants if g.last_updated and g.last_updated > datetime.utcnow() - timedelta(minutes=30)]
    
    open_count = sum(1 for g in grants if g.status == "open")
    closed_count = sum(1 for g in grants if g.status == "closed")
    
    print(f"  Total Grants: {total}")
    print(f"  Updated (last 30 min): {len(recent)}")
    print(f"  Open: {open_count} | Closed: {closed_count}")
    
    if recent:
        print(f"\n  Last 5 Updates:")
        for g in sorted(recent, key=lambda x: x.last_updated, reverse=True)[:5]:
            url_short = (g.url[:55] + "...") if len(g.url) > 55 else g.url
            time_ago = (datetime.utcnow() - g.last_updated).total_seconds() / 60
            status_icon = "✅" if g.status == "open" else "🔴" if g.status == "closed" else "⚠️"
            print(f"    {status_icon} [{time_ago:.1f}m] {url_short} → {g.status}")
    else:
        print("  ⏳ No recent updates")
except Exception as e:
    print(f"  Error: {e}")
PYTHON_SCRIPT

echo ""

# Check recent logs
echo "Recent Log Activity:"
echo "----------------------------------------"
docker-compose logs fastapi --tail 20 2>/dev/null | grep -iE "(scraper|scraping|grant|ai|finished)" | tail -5 || echo "  No recent scraper activity in logs"
echo ""

# Check if scraper is actually running
echo "Is Scraper Running?"
CELERY_RUNNING=$(docker-compose ps celery 2>/dev/null | grep -q "Up" && echo "yes" || echo "no")
if [ "$CELERY_RUNNING" = "no" ]; then
    echo "  ❌ Celery is not running"
    echo "  💡 Celery container might be restarting"
    echo "  💡 Use direct mode instead: python3 run_scraper_direct.py"
else
    TASK_COUNT=$(docker-compose exec -T celery celery -A celery_worker.celery inspect active 2>/dev/null | grep -c "run_all_scrapers" 2>/dev/null || echo "0")
    if [ "$TASK_COUNT" != "0" ] && [ -n "$TASK_COUNT" ]; then
        echo "  ✅ Yes - scraper task is active in Celery"
    else
        echo "  ⚠️  No active scraper task in Celery"
        echo "  💡 Celery might have issues. Try direct mode: python3 run_scraper_direct.py"
    fi
fi
echo ""

echo "=========================================="

