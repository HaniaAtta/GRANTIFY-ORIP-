# 🚀 Quick Start Guide - Run Dashboard & Test Panels

## Step 1: Start All Services

### Option A: Using Docker (Recommended)

```bash
# Start all services (FastAPI + Celery + Redis)
docker-compose up --build -d

# Check if services are running
docker-compose ps

# View logs (to see what's happening)
docker-compose logs -f
```

### Option B: Run Locally (Without Docker)

**Terminal 1 - Start FastAPI:**
```bash
source HandM/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Start Redis:**
```bash
redis-server
```

**Terminal 3 - Start Celery:**
```bash
source HandM/bin/activate
celery -A celery_worker.celery worker --loglevel=info
```

---

## Step 2: Access Dashboard

Open your browser and go to:
```
http://localhost:8000
```

You'll see the login page.

---

## Step 3: Test Admin Panel

### Login as Admin:
- **Username**: `admin`
- **Password**: `secret123@`

### Admin Features (What you can do):
1. ✅ **View all grants** - See all grants in the database
2. ✅ **Add new grant URL** - Form at the top to add URLs
3. ✅ **Delete grants** - "Remove" button on each grant
4. ✅ **Search grants** - Search bar to filter grants
5. ✅ **Filter by category** - Click category tags
6. ✅ **Trigger scraping** - Can run batch scraping

### Test Admin Functions:

1. **Add a new grant:**
   - Enter a URL in the form (e.g., `https://example.com/grants`)
   - Select categories
   - Click "Check & Add URL"
   - Should see success message

2. **Delete a grant:**
   - Find a grant in the table
   - Click "Remove" button
   - Confirm deletion
   - Grant should disappear

3. **Search grants:**
   - Type in search bar
   - Table should filter in real-time

---

## Step 4: Test User Panel

### Logout and Login as Normal User:
1. Click "Logout" button
2. Login with:
   - **Username**: `user`
   - **Password**: `user123@`

### User Features (What you can do):
1. ✅ **View all grants** - See all grants
2. ✅ **Search grants** - Search bar works
3. ✅ **Filter by category** - Category tags work
4. ❌ **Cannot add grants** - No form visible
5. ❌ **Cannot delete grants** - No "Remove" button

### Test User Functions:

1. **Try to add grant:**
   - Should NOT see the "Add URL" form
   - Should see message: "Welcome! You are viewing grants in read-only mode"

2. **Try to delete:**
   - Should NOT see "Remove" buttons
   - Only viewing capabilities

---

## Step 5: Test Scraping

### Option 1: Via Dashboard (Admin only)
```bash
# Login as admin first, then:
# Use the API endpoint or trigger via dashboard
```

### Option 2: Via Command Line
```bash
# If using Docker
docker-compose exec celery celery -A celery_worker.celery call tasks.run_scrapers.run_all_scrapers

# If running locally
python3 -c "from tasks.run_scrapers import run_all_scrapers; run_all_scrapers.delay()"
```

### Option 3: Via API
```bash
curl -X POST http://localhost:8000/api/scrape_all
```

---

## Complete Test Workflow

### 1. Start Services:
```bash
docker-compose up --build -d
```

### 2. Wait for services to start (5-10 seconds):
```bash
docker-compose ps
# Should show all 3 services running
```

### 3. Open Dashboard:
```bash
open http://localhost:8000
# Or manually: http://localhost:8000
```

### 4. Test Admin Panel:
```
Login: admin / secret123@
- Add a grant URL
- Delete a grant
- Search grants
- Filter by category
```

### 5. Test User Panel:
```
Logout → Login: user / user123@
- View grants (read-only)
- Search grants
- Filter by category
- Verify: No add/delete options
```

### 6. Test Scraping:
```bash
# Run scraper on all grants in database
docker-compose exec celery celery -A celery_worker.celery call tasks.run_scrapers.run_all_scrapers

# Monitor progress
docker-compose logs -f celery
```

---

## Quick Commands Reference

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Restart services
docker-compose restart

# Rebuild and restart
docker-compose up --build -d
```

---

## Troubleshooting

### Dashboard not loading?
```bash
# Check if FastAPI is running
docker-compose logs fastapi

# Check port 8000
lsof -i :8000
```

### Can't login?
- Make sure you're using correct credentials
- Admin: `admin` / `secret123@`
- User: `user` / `user123@`

### Scraping not working?
```bash
# Check Celery logs
docker-compose logs celery

# Check Redis is running
docker-compose ps redis
```

---

## Expected Results

### Admin Panel Should Show:
- ✅ URL input form at top
- ✅ "Remove" button on each grant
- ✅ Full CRUD capabilities
- ✅ All grants visible

### User Panel Should Show:
- ✅ Read-only message
- ✅ No URL input form
- ✅ No "Remove" buttons
- ✅ All grants visible (view only)

---

## 🎯 Quick Test Checklist

- [ ] Services started (`docker-compose ps`)
- [ ] Dashboard accessible (`http://localhost:8000`)
- [ ] Admin login works
- [ ] Admin can add grants
- [ ] Admin can delete grants
- [ ] User login works
- [ ] User cannot add/delete (read-only)
- [ ] Search works for both
- [ ] Category filter works
- [ ] Scraping can be triggered

---

## ✅ All Set!

Your dashboard is ready to use. Both admin and user panels are working with their respective features!

