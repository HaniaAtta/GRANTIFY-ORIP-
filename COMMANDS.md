# Complete Command Guide

This guide provides all commands needed to run the grant dashboard system.

## 🚀 Quick Start (Recommended: Docker)

### Step 1: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# NeonDB Connection (get from https://console.neon.tech)
DATABASE_URL=postgresql://username:password@host.neon.tech/dbname?sslmode=require

# OpenAI API Key (get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=OPENAI_API_KEY_HERE

# Redis URL (for Celery)
REDIS_URL=redis://redis:6379/0
```

### Step 2: Export Data from categories.json to NeonDB

```bash
# First, do a dry run to see what will be exported
python export_json_to_db.py --dry-run

# Export without scraping (fast)
python export_json_to_db.py

# Export and scrape each URL (slower, but gets current status)
python export_json_to_db.py --scrape
```

### Step 3: Start Docker Services

```bash
# Build and start all services (FastAPI + Celery + Redis)
docker-compose up --build

# Or run in background (detached mode)
docker-compose up --build -d
```

### Step 4: Verify Services Are Running

```bash
# Check all containers
docker-compose ps

# View logs
docker-compose logs -f

# Check specific service logs
docker-compose logs fastapi
docker-compose logs celery
docker-compose logs redis
```

### Step 5: Access Dashboard

Open your browser: **http://localhost:8000**

- **Admin**: `admin` / `secret123@`
- **User**: `user` / `user123@`

### Step 6: Trigger Scraping

#### Option A: Via Dashboard (Admin Panel)
1. Login as admin
2. Click "Scrape All" button (if available) or use API endpoint

#### Option B: Via API
```bash
curl -X POST http://localhost:8000/api/scrape_all
```

#### Option C: Via Celery Command (Inside Docker)
```bash
# Execute command in celery container
docker-compose exec celery celery -A celery_worker.celery call tasks.run_scrapers.run_all_scrapers

# Or trigger via Python
docker-compose exec fastapi python -c "from tasks.run_scrapers import run_all_scrapers; run_all_scrapers.delay()"
```

---

## 🔧 Alternative: Run Locally (Without Docker)

### Step 1: Start Redis

```bash
# Install Redis if not installed
# macOS: brew install redis
# Linux: sudo apt-get install redis-server

# Start Redis server
redis-server

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

### Step 2: Initialize Database

```bash
# Create tables in NeonDB
python -c "from models.init_db import create_tables; create_tables()"

# Export data from categories.json
python export_json_to_db.py
```

### Step 3: Start Celery Worker

```bash
# In a separate terminal
celery -A celery_worker.celery worker --loglevel=info

# Or with auto-reload (development)
celery -A celery_worker.celery worker --loglevel=info --reload
```

### Step 4: Start FastAPI Server

```bash
# In another terminal
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or with more workers (production)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Step 5: Trigger Scraping

```bash
# Option 1: Via Python
python -c "from tasks.run_scrapers import run_all_scrapers; run_all_scrapers.delay()"

# Option 2: Via Celery CLI
celery -A celery_worker.celery call tasks.run_scrapers.run_all_scrapers

# Option 3: Via API
curl -X POST http://localhost:8000/api/scrape_all
```

---

## 📊 Data Management Commands

### Export Data to NeonDB

```bash
# Dry run (see what would happen)
python export_json_to_db.py --dry-run

# Export without scraping
python export_json_to_db.py

# Export and scrape each URL
python export_json_to_db.py --scrape
```

### Check Database

```bash
# Connect to NeonDB (replace with your connection string)
psql "your-neondb-connection-string"

# Inside psql:
\dt                    # List all tables
SELECT COUNT(*) FROM grant_sites;  # Count grants
SELECT * FROM grant_sites LIMIT 10;  # View first 10 grants
SELECT url, status, is_user_added FROM grant_sites;  # View specific columns
```

### Verify Setup

```bash
# Run verification script
python verify_setup.py
```

---

## 🐳 Docker Commands Reference

### Basic Commands

```bash
# Build images
docker-compose build

# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild and restart
docker-compose up --build -d
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f fastapi
docker-compose logs -f celery
docker-compose logs -f redis

# Last 100 lines
docker-compose logs --tail=100 fastapi
```

### Execute Commands in Containers

```bash
# Access FastAPI container shell
docker-compose exec fastapi bash

# Access Celery container shell
docker-compose exec celery bash

# Run Python command in FastAPI container
docker-compose exec fastapi python -c "from models.db_helper import get_grant_sites; print(len(get_grant_sites()))"

# Run Celery command in Celery container
docker-compose exec celery celery -A celery_worker.celery inspect active
```

### Check Container Status

```bash
# List running containers
docker-compose ps

# Check resource usage
docker stats

# View container details
docker-compose config
```

---

## 🔄 Scraping Commands

### Scrape All Grants (from categories.json)

```bash
# Via Docker
docker-compose exec celery celery -A celery_worker.celery call tasks.run_scrapers.run_all_scrapers

# Via Python (Docker)
docker-compose exec fastapi python -c "from tasks.run_scrapers import run_all_scrapers; run_all_scrapers.delay()"

# Via Python (Local)
python -c "from tasks.run_scrapers import run_all_scrapers; run_all_scrapers.delay()"

# Via API
curl -X POST http://localhost:8000/api/scrape_all
```

### Check Scraping Status

```bash
# Check Celery tasks
docker-compose exec celery celery -A celery_worker.celery inspect active

# Check scheduled tasks
docker-compose exec celery celery -A celery_worker.celery inspect scheduled

# View task results
docker-compose exec celery celery -A celery_worker.celery inspect stats
```

### Scrape Single URL

```bash
# Via Python
python -c "from scrapers.bs_scrapper.scraper import scrape_page; print(scrape_page('https://example.com'))"
```

---

## 🔍 Troubleshooting Commands

### Check Database Connection

```bash
# Test connection
python -c "from models.db_helper import engine; from sqlalchemy import inspect; print('Tables:', inspect(engine).get_table_names())"

# Check if tables exist
python -c "from models.db_helper import get_db, GrantSite; db = next(get_db()); print('Grants:', db.query(GrantSite).count())"
```

### Check Redis Connection

```bash
# Test Redis
redis-cli ping

# Check Redis info
redis-cli info

# View Redis keys
redis-cli keys "*"
```

### Check Environment Variables

```bash
# View .env file (be careful with sensitive data)
cat .env

# Test environment loading
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('DATABASE_URL:', os.getenv('DATABASE_URL')[:50])"
```

### View Application Logs

```bash
# Docker logs
docker-compose logs -f fastapi | grep ERROR
docker-compose logs -f celery | grep ERROR

# Local logs (if running uvicorn)
# Logs appear in terminal where uvicorn is running
```

---

## 📝 Complete Workflow Example

### First Time Setup

```bash
# 1. Clone/navigate to project
cd /Users/ali/Desktop/BeautifulSoup/gtw

# 2. Create .env file with your credentials
nano .env  # or use your favorite editor

# 3. Install dependencies (if not using Docker)
pip install -r requirements.txt

# 4. Verify setup
python verify_setup.py

# 5. Initialize database
python -c "from models.init_db import create_tables; create_tables()"

# 6. Export data from categories.json
python export_json_to_db.py

# 7. Start Docker services
docker-compose up --build -d

# 8. Check services are running
docker-compose ps

# 9. Access dashboard
open http://localhost:8000
```

### Daily Usage

```bash
# 1. Start services (if not already running)
docker-compose up -d

# 2. Trigger scraping
docker-compose exec celery celery -A celery_worker.celery call tasks.run_scrapers.run_all_scrapers

# 3. Monitor progress
docker-compose logs -f celery

# 4. Access dashboard
open http://localhost:8000
```

### Update Data

```bash
# Re-export from categories.json (updates existing records)
python export_json_to_db.py

# Re-scrape all grants
docker-compose exec celery celery -A celery_worker.celery call tasks.run_scrapers.run_all_scrapers
```

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Start all services | `docker-compose up -d` |
| Stop all services | `docker-compose down` |
| View logs | `docker-compose logs -f` |
| Export JSON to DB | `python export_json_to_db.py` |
| Scrape all grants | `docker-compose exec celery celery -A celery_worker.celery call tasks.run_scrapers.run_all_scrapers` |
| Check database | `python -c "from models.db_helper import get_grant_sites; print(len(get_grant_sites()))"` |
| Verify setup | `python verify_setup.py` |

---

## ⚠️ Important Notes

1. **Always check `.env` file exists** before running commands
2. **NeonDB connection string** must be in `.env` as `DATABASE_URL`
3. **Redis must be running** before starting Celery
4. **Docker services** need to be started before accessing dashboard
5. **Scraping takes time** - monitor logs to see progress

---

## 🆘 Need Help?

1. Run `python verify_setup.py` to diagnose issues
2. Check `SETUP.md` for detailed setup instructions
3. Check `CHANGES.md` for recent changes
4. View logs: `docker-compose logs -f`

