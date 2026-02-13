# Grant Dashboard Setup Guide

This guide will help you set up the grant dashboard with NeonDB PostgreSQL, admin/normal user panels, and proper scraping functionality.

## Prerequisites

- Python 3.10+
- Docker and Docker Compose (for containerized setup)
- NeonDB account (for PostgreSQL database)
- OpenAI API key (for grant classification)
- Redis (for Celery task queue)

## Step 1: Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
# NeonDB PostgreSQL Connection String
# Get this from your NeonDB dashboard: https://console.neon.tech
DATABASE_URL=postgresql://username:password@host.neon.tech/dbname?sslmode=require

# OpenAI API Key (for grant classification)
# Get this from: https://platform.openai.com/api-keys
OPENAI_API_KEY=OPENAI_API_KEY_HERE

# Redis URL (for Celery task queue)
# For local development, use: redis://localhost:6379/0
REDIS_URL=redis://localhost:6379/0
```

## Step 2: Database Setup

### Option A: Using NeonDB (Recommended)

1. Sign up at https://console.neon.tech
2. Create a new project
3. Copy the connection string and add it to your `.env` file as `DATABASE_URL`
4. Run the database initialization:

```bash
python -c "from models.init_db import create_tables; create_tables()"
```

### Option B: Using Local PostgreSQL

1. Install PostgreSQL locally
2. Create a database:
```bash
createdb grants_db
```
3. Set `DATABASE_URL=postgresql://user:password@localhost/grants_db` in `.env`

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Run with Docker (Recommended)

### Build and Start Services

```bash
docker-compose up --build
```

This will start:
- FastAPI app on http://localhost:8000
- Celery worker for background scraping
- Redis for task queue

### Verify Services

```bash
# Check if containers are running
docker-compose ps

# Check FastAPI logs
docker-compose logs fastapi

# Check Celery logs
docker-compose logs celery

# Check Redis logs
docker-compose logs redis
```

### Stop Services

```bash
docker-compose down
```

## Step 5: Run Locally (Without Docker)

### Terminal 1: Start FastAPI

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Start Redis

```bash
redis-server
```

### Terminal 3: Start Celery Worker

```bash
celery -A celery_worker.celery worker --loglevel=info
```

## Step 6: Access the Dashboard

1. Open http://localhost:8000
2. Login with:
   - **Admin**: username=`admin`, password=`secret123@` (full CRUD access)
   - **Normal User**: username=`user`, password=`user123@` (read-only)

## Step 7: Verify Database Connection

```bash
# Test database connection
python -c "from models.db_helper import get_db; next(get_db()); print('✅ Database connected!')"
```

## Step 8: Test Scraping

### Manual Scrape (Admin Panel)

1. Login as admin
2. Enter a grant URL in the form
3. Select categories
4. Click "Check & Add URL"

### Batch Scrape (All Grants from categories.json)

```bash
# Trigger via API (requires admin login)
curl -X POST http://localhost:8000/api/scrape_all \
  -H "Cookie: session=your-session-cookie"
```

Or use the Celery task directly:

```bash
python -c "from tasks.run_scrapers import run_all_scrapers; run_all_scrapers.delay()"
```

## Troubleshooting

### Database Connection Issues

```bash
# Test NeonDB connection
psql "your-neondb-connection-string"

# Check if tables exist
python -c "from models.db_helper import engine; from sqlalchemy import inspect; print(inspect(engine).get_table_names())"
```

### Redis Connection Issues

```bash
# Test Redis
redis-cli ping
# Should return: PONG
```

### Scraper Not Working

1. Check OpenAI API key is valid:
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', os.getenv('OPENAI_API_KEY')[:10] + '...')"
```

2. Check Celery worker is running:
```bash
docker-compose logs celery | tail -20
```

### User-Added URLs Being Lost

The system now preserves user-added URLs. Check:
- `is_user_added` flag in database: `SELECT url, is_user_added FROM grant_sites;`
- Scraper uses `preserve_user_flag=True` when updating

## Docker Commands Reference

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build -d

# Execute command in container
docker-compose exec fastapi bash

# Check container status
docker-compose ps
```

## Features

### Admin Panel
- ✅ Add new grant URLs
- ✅ Delete grants
- ✅ Update grant information
- ✅ Trigger batch scraping
- ✅ Full CRUD operations

### Normal User Panel
- ✅ View all grants
- ✅ Search and filter grants
- ✅ View grant details (dates, regions, eligibility)
- ❌ Cannot add/delete/update grants

### Data Preservation
- ✅ User-added URLs are preserved during batch scrapes
- ✅ Only status and dates are updated for user-added grants
- ✅ Auto-scraped grants can be fully updated

## Next Steps

1. Change default admin/user passwords in `app/main.py`
2. Add more grant URLs to `app/config/categories.json`
3. Customize scraping logic in `scrapers/bs_scrapper/scraper.py`
4. Set up scheduled scraping with Celery Beat (already configured for every 6 hours)

