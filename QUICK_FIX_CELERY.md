# 🚀 Quick Fix: Celery Container Restarting

## Problem:
Celery container keeps restarting, so you can't run the scraper via Celery.

## ✅ Solution: Use These Alternatives

### Option 1: Use API Endpoint (EASIEST) ⭐

```bash
# This works even if Celery is down!
curl -X POST http://localhost:8000/api/scrape_all
```

**This is the easiest way!** It uses FastAPI directly and doesn't need Celery.

---

### Option 2: Run Scraper Directly (No Celery)

```bash
# Activate virtual environment
source HandM/bin/activate

# Run scraper directly
python3 run_scraper_direct.py
```

This bypasses Celery entirely and runs the scraper directly.

---

### Option 3: Check Celery Logs

```bash
# See what's wrong
docker-compose logs celery --tail 100
```

Common issues:
- Missing environment variables
- Import errors
- Redis connection issues

---

### Option 4: Restart Celery

```bash
# Stop and restart
docker-compose restart celery

# Or rebuild
docker-compose up -d --build celery
```

---

## 🎯 Recommended: Use API Endpoint

**Just run this:**

```bash
curl -X POST http://localhost:8000/api/scrape_all
```

This will:
- ✅ Work even if Celery is down
- ✅ Trigger scraping via FastAPI
- ✅ Update database correctly
- ✅ Use GPT API properly

---

## Complete Commands

```bash
# 1. Check what's wrong
docker-compose logs celery --tail 50

# 2. Use API endpoint (easiest)
curl -X POST http://localhost:8000/api/scrape_all

# 3. Or run directly
source HandM/bin/activate
python3 run_scraper_direct.py

# 4. Monitor progress
docker-compose logs -f fastapi
```

---

## ✅ Summary

**Best option:** Use the API endpoint - it's the simplest and works even when Celery has issues!

```bash
curl -X POST http://localhost:8000/api/scrape_all
```

That's it! 🚀

