# 🚀 Complete Run Commands Guide

## Quick Start (All-in-One)

```bash
# Start everything
./start_dashboard.sh
```

Or manually:
```bash
docker-compose up --build -d
```

---

## Step-by-Step Commands

### 1. Fix Docker Build (If Needed)

```bash
# Rebuild without cache (if build failed)
docker-compose build --no-cache

# Or rebuild specific service
docker-compose build --no-cache fastapi
```

### 2. Start Services

```bash
# Start all services
docker-compose up --build -d

# Check status
docker-compose ps

# Should show:
# - grantly_app (running)
# - grantly_celery (running)  
# - grantly_redis (running)
```

### 3. Access Dashboard

Open browser:
```
http://localhost:8000
```

---

## Test Admin Panel

### Login:
- **URL**: http://localhost:8000
- **Username**: `admin`
- **Password**: `secret123@`

### Test These Features:

1. **Add Grant URL:**
   - See form at top: "Admin Panel - Add New Grant URL"
   - Enter URL: `https://example.com/grants`
   - Select categories
   - Click "Check & Add URL"
   - Should see success message

2. **Delete Grant:**
   - Find any grant in table
   - Click "Remove" button (rightmost column)
   - Confirm deletion
   - Grant disappears

3. **Search:**
   - Type in search bar
   - Table filters in real-time

4. **Filter by Category:**
   - Click category tags above table
   - Table shows only that category

---

## Test User Panel

### Logout and Login:
1. Click "Logout" button (top right)
2. Login with:
   - **Username**: `user`
   - **Password**: `user123@`

### Verify Read-Only Mode:

1. **No Add Form:**
   - Should see: "Welcome! You are viewing grants in read-only mode"
   - NO URL input form

2. **No Delete Buttons:**
   - NO "Remove" buttons in table
   - Only viewing capabilities

3. **Search Works:**
   - Search bar still works
   - Can filter grants

4. **Category Filter Works:**
   - Category tags work
   - Can filter by category

---

## Test Scraping

### Option 1: Via Command Line
```bash
# Scrape all grants from NeonDB
docker-compose exec celery celery -A celery_worker.celery call tasks.run_scrapers.run_all_scrapers
```

### Option 2: Monitor Progress
```bash
# Watch scraping progress
docker-compose logs -f celery
```

### Option 3: Test on Few Websites First
```bash
# Test on 5 websites (outside Docker, in your terminal)
python3 test_scraper_few.py -n 5
```

---

## Complete Test Workflow

```bash
# 1. Start services
docker-compose up --build -d

# 2. Wait for services (5-10 seconds)
sleep 5

# 3. Check services are running
docker-compose ps

# 4. Open dashboard in browser
open http://localhost:8000
# Or: http://localhost:8000

# 5. Test Admin Panel
# Login: admin / secret123@
# - Add a grant
# - Delete a grant
# - Search
# - Filter

# 6. Test User Panel  
# Logout → Login: user / user123@
# - View grants (read-only)
# - Search works
# - Filter works
# - No add/delete

# 7. Test Scraping
docker-compose exec celery celery -A celery_worker.celery call tasks.run_scrapers.run_all_scrapers
```

---

## Troubleshooting Commands

### If Build Fails:
```bash
# Clean rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### If Services Don't Start:
```bash
# Check logs
docker-compose logs fastapi
docker-compose logs celery
docker-compose logs redis

# Check what's wrong
docker-compose ps
```

### If Dashboard Not Loading:
```bash
# Check FastAPI logs
docker-compose logs -f fastapi

# Restart FastAPI
docker-compose restart fastapi
```

### If Scraping Not Working:
```bash
# Check Celery logs
docker-compose logs -f celery

# Check if Celery is running
docker-compose exec celery celery -A celery_worker.celery inspect active
```

---

## Quick Reference

| Task | Command |
|------|---------|
| **Start all** | `docker-compose up --build -d` |
| **Stop all** | `docker-compose down` |
| **View logs** | `docker-compose logs -f` |
| **Check status** | `docker-compose ps` |
| **Restart** | `docker-compose restart` |
| **Rebuild** | `docker-compose build --no-cache` |
| **Run scraper** | `docker-compose exec celery celery -A celery_worker.celery call tasks.run_scrapers.run_all_scrapers` |
| **Access dashboard** | `http://localhost:8000` |

---

## Login Credentials

### Admin Panel:
- Username: `admin`
- Password: `secret123@`
- Features: ✅ Add, ✅ Delete, ✅ Update, ✅ Search, ✅ Filter

### User Panel:
- Username: `user`
- Password: `user123@`
- Features: ✅ View, ✅ Search, ✅ Filter (Read-Only)

---

## Expected Results

### Admin Panel:
- ✅ URL input form visible
- ✅ "Remove" buttons on each grant
- ✅ Full CRUD capabilities
- ✅ Can add/delete grants

### User Panel:
- ✅ Read-only message visible
- ✅ NO URL input form
- ✅ NO "Remove" buttons
- ✅ Can only view/search/filter

---

## 🎯 Ready to Test!

Run these commands:

```bash
# 1. Rebuild (to fix Docker issue)
docker-compose build --no-cache

# 2. Start services
docker-compose up -d

# 3. Check status
docker-compose ps

# 4. Open dashboard
open http://localhost:8000
```

Then test both admin and user panels! 🚀

