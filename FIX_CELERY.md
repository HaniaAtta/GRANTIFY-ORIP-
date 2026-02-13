# 🔧 Fix Celery Restart Issue

## Problem:
Celery container is restarting continuously, which means there's an error preventing it from starting.

## Quick Fixes:

### Option 1: Check Logs First
```bash
# See what's causing the restart
docker-compose logs celery --tail 100

# Check all services
docker-compose logs --tail 50
```

### Option 2: Restart Celery Service
```bash
# Stop and restart
docker-compose restart celery

# Or rebuild
docker-compose up -d --build celery
```

### Option 3: Run Scraper Without Docker Celery

**Run locally (bypass Docker Celery):**

```bash
# Activate virtual environment
source HandM/bin/activate

# Run scraper directly (no Celery needed)
python3 -c "
from tasks.run_scrapers import run_all_scrapers
run_all_scrapers()
"
```

### Option 4: Use API Endpoint (Easiest)

```bash
# Trigger scraping via API (works even if Celery is down)
curl -X POST http://localhost:8000/api/scrape_all
```

### Option 5: Fix Celery Configuration

The issue might be:
1. Missing `celery_worker.py` module
2. Import errors
3. Redis connection issues

**Check if celery_worker exists:**
```bash
ls -la celery_worker.py
```

**Test Celery locally:**
```bash
source HandM/bin/activate
celery -A celery_worker.celery worker --loglevel=info
```

---

## Recommended: Use API Endpoint

The easiest way to run the scraper is via the API endpoint:

```bash
# This works even if Celery container is restarting
curl -X POST http://localhost:8000/api/scrape_all
```

This will:
- Use the FastAPI service (which should be running)
- Trigger scraping in the background
- Work even if Celery has issues

---

## Alternative: Run Scraper Script Directly

Create a simple script to run scraper without Celery:

```bash
# Create run_scraper_direct.py
cat > run_scraper_direct.py << 'EOF'
from tasks.run_scrapers import run_all_scrapers
if __name__ == "__main__":
    run_all_scrapers()
EOF

# Run it
python3 run_scraper_direct.py
```

---

## Check What's Wrong

```bash
# 1. Check Celery logs
docker-compose logs celery

# 2. Check if Redis is running
docker-compose ps redis

# 3. Check if FastAPI is running
docker-compose ps fastapi

# 4. Test Redis connection
docker-compose exec redis redis-cli ping
```

---

## Quick Solution

**Just use the API endpoint - it's the easiest:**

```bash
curl -X POST http://localhost:8000/api/scrape_all
```

This bypasses Celery entirely and works through FastAPI! 🚀

