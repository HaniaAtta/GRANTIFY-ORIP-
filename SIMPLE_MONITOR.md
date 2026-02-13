# 📊 Simple Scraper Monitoring

## Quick Status Check (Shows Everything)

```bash
./check_scraper_status.sh
```

This shows:
- ✅ Service status
- ✅ Database stats
- ✅ Recent updates
- ✅ If scraper is running

---

## Watch Logs (Simple Version)

```bash
./watch_scraper_simple.sh
```

This shows:
- Current database status
- Live log activity
- Which websites are being scraped
- Results as they come in

---

## Even Simpler - Just Watch Logs

```bash
# Watch all logs
docker-compose logs -f fastapi

# Or watch only scraper-related
docker-compose logs -f fastapi | grep -i scraper
```

---

## Check Results Periodically

```bash
# Show results
python3 show_scraper_results.py

# Or auto-refresh every 10 seconds
watch -n 10 python3 show_scraper_results.py
```

---

## One-Liner to See Everything

```bash
# Check status + watch logs
./check_scraper_status.sh && echo "" && echo "Watching logs..." && docker-compose logs -f fastapi | grep -iE "(scraper|scraping|finished|error)"
```

---

## If Nothing Shows Up

1. **Check if scraper is running:**
   ```bash
   ./check_scraper_status.sh
   ```

2. **Start scraper if not running:**
   ```bash
   curl -X POST http://localhost:8000/api/scrape_all
   ```

3. **Then watch logs:**
   ```bash
   docker-compose logs -f fastapi
   ```

---

## Recommended Commands

**For quick check:**
```bash
./check_scraper_status.sh
```

**For watching progress:**
```bash
docker-compose logs -f fastapi | grep -iE "(scraper|scraping|finished)"
```

**For results:**
```bash
watch -n 10 python3 show_scraper_results.py
```

---

## Troubleshooting

If scripts show nothing:

1. **Check if services are running:**
   ```bash
   docker-compose ps
   ```

2. **Check if scraper was started:**
   ```bash
   curl -X POST http://localhost:8000/api/scrape_all
   ```

3. **Check raw logs:**
   ```bash
   docker-compose logs fastapi --tail 50
   ```

4. **Check database directly:**
   ```bash
   python3 show_scraper_results.py
   ```

---

## 🚀 Start Here

```bash
# 1. Check status
./check_scraper_status.sh

# 2. If scraper not running, start it
curl -X POST http://localhost:8000/api/scrape_all

# 3. Watch logs
docker-compose logs -f fastapi
```

This will definitely show you what's happening! 📊

