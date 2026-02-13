# 📊 Scraper Monitoring Commands

## Option 1: Live Real-Time Monitor (Best for Watching Progress)

Shows live updates as websites are being scraped:

```bash
./watch_scraper_live.sh
```

**Shows:**
- ✅ Total grants
- ✅ Recently updated grants
- ✅ Status breakdown (open/closed/unknown)
- ✅ Real-time scraping activity
- ✅ Which URLs are being scraped
- ✅ Success/failure status
- ✅ Updates every 5 seconds

**Press Ctrl+C to stop**

---

## Option 2: Simple Log Monitor

Watch logs with formatted output:

```bash
./monitor_scraper.sh
```

**Shows:**
- 🔄 When scraping starts
- ✅ When scraping completes
- 🤖 GPT analysis status
- ❌ Errors
- 📊 Database updates every 30 seconds

---

## Option 3: Show Results Summary

See which websites were scraped and their results:

```bash
# Show results once
python3 show_scraper_results.py

# Or watch it update every 10 seconds
watch -n 10 python3 show_scraper_results.py
```

**Shows:**
- 📊 Total grants
- 🔄 Recently updated (last hour)
- ✅ Status breakdown
- 📝 List of scraped websites with:
  - Status (open/closed/unknown)
  - Categories
  - Dates
  - Regions
  - Pakistan applicability

---

## Option 4: Quick Status Check

```bash
# Check status endpoint
curl http://localhost:8000/api/scraper-status | python3 -m json.tool

# Check recent database updates
python3 -c "
from models.db_helper import get_grant_sites
from datetime import datetime, timedelta
grants = get_grant_sites()
recent = [g for g in grants if g.last_updated and g.last_updated > datetime.utcnow() - timedelta(minutes=10)]
print(f'Updated in last 10 min: {len(recent)}')
for g in recent[:5]:
    print(f'  - {g.url[:60]}... → {g.status}')
"
```

---

## Option 5: Watch Docker Logs Directly

```bash
# Watch all logs
docker-compose logs -f fastapi

# Watch only scraper-related logs
docker-compose logs -f fastapi | grep -E "(Scraper|scraping|AI|finished|Error)"

# Watch with timestamps
docker-compose logs -f fastapi --timestamps
```

---

## Recommended: Use Live Monitor

**Best option for real-time monitoring:**

```bash
./watch_scraper_live.sh
```

This gives you:
- ✅ Live progress updates
- ✅ Which websites are being scraped
- ✅ Results as they come in
- ✅ Status breakdown
- ✅ Clean, formatted output

---

## Quick Reference

| Command | What It Does |
|---------|-------------|
| `./watch_scraper_live.sh` | **Best** - Live real-time monitor |
| `./monitor_scraper.sh` | Simple log monitor |
| `python3 show_scraper_results.py` | Show results summary |
| `watch -n 10 python3 show_scraper_results.py` | Auto-refresh results every 10s |
| `docker-compose logs -f fastapi` | Raw Docker logs |

---

## Example Output

When you run `./watch_scraper_live.sh`, you'll see:

```
==========================================
📊 Live Scraper Monitor - 14:30:25
==========================================

📊 Total Grants: 156
🔄 Updated (last 10 min): 5
✅ Open: 45 | 🔴 Closed: 78 | ⚠️  Unknown: 33

📝 Recently Updated:
  ✅ [2.3m] https://example.com/grants → open
  🔴 [5.1m] https://another.com/funding → closed
  ✅ [8.7m] https://grant.org/apply → open

📋 Recent Log Activity:
----------------------------------------
🔄 [14:30:20] Scraping: https://newgrant.com...
✅ [14:30:25] Completed: https://newgrant.com...
   🤖 GPT: Success
```

---

## 🚀 Start Monitoring Now

```bash
# Best option - live monitor
./watch_scraper_live.sh
```

This will show you everything in real-time! 📊

