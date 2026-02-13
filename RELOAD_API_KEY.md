# 🔄 Reload New API Key

## Problem:
You updated the API key in `.env`, but the service is still using the old one.

## Solution: Restart Services

The Docker container needs to be restarted to pick up the new `.env` file.

### Step 1: Restart FastAPI

```bash
# Restart FastAPI to load new API key
docker-compose restart fastapi

# Or rebuild if needed
docker-compose up -d --build fastapi
```

### Step 2: Wait a Few Seconds

```bash
sleep 5
```

### Step 3: Verify New API Key

```bash
# Check if new API key is working
curl http://localhost:8000/api/scraper-status | python3 -m json.tool
```

**Should now show:**
```json
{
  "api_key_working": true,  // ✅ Should be true now!
  "api_test_response": "OK"
}
```

---

## Alternative: Check .env File Location

If restart doesn't work, verify:

1. **Check if .env is in the right place:**
   ```bash
   ls -la .env
   ```

2. **Check if Docker is reading it:**
   ```bash
   docker-compose exec fastapi env | grep OPENAI_API_KEY
   ```

3. **If Docker isn't reading it, restart all services:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

---

## Quick Fix Commands

```bash
# 1. Restart FastAPI
docker-compose restart fastapi

# 2. Wait
sleep 5

# 3. Verify
curl http://localhost:8000/api/scraper-status | python3 -m json.tool

# 4. If still not working, restart all
docker-compose restart
```

---

## Verify API Key in .env

```bash
# Check what's in .env
grep OPENAI_API_KEY .env

# Should show your new key
# OPENAI_API_KEY=OPENAI_API_KEY_HERE
```

---

## If Still Not Working

1. **Check Docker logs:**
   ```bash
   docker-compose logs fastapi | grep -i "api\|openai\|key"
   ```

2. **Verify .env is mounted:**
   ```bash
   docker-compose exec fastapi cat /app/.env | grep OPENAI
   ```

3. **Full restart:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

---

## ✅ Success Indicators

After restart, you should see:
- `"api_key_working": true`
- `"api_test_response": "OK"` or similar
- No `"api_error"` field

Then you can run the scraper and it will use GPT properly! 🚀

