# ✅ Final API Key Fix Steps

## Current Status:
- ✅ .env file has new API key (OPENAI_API_KEY_HERE)
- ✅ Docker sees the new API key
- ⚠️ Need to verify if the key works and restart service

## Step 1: Test API Key

```bash
# Test the API key directly
python3 test_api_key_simple.py
```

This will tell you if:
- ✅ API key works (has credits)
- ❌ API key has quota issues (needs credits)

---

## Step 2: Restart FastAPI Service

Even though Docker sees the new key, FastAPI might be caching the old one. Do a full restart:

```bash
# Full restart to ensure new key is loaded
docker-compose down
docker-compose up -d

# Wait for services
sleep 5
```

---

## Step 3: Verify Status

```bash
# Check if API key is working now
curl http://localhost:8000/api/scraper-status | python3 -m json.tool
```

**Should show:**
```json
{
  "api_key_working": true,
  "api_test_response": "OK"
}
```

---

## Step 4: Run Scraper

Once API key is working:

```bash
# Run scraper
curl -X POST http://localhost:8000/api/scrape_all

# Monitor progress
docker-compose logs -f fastapi | grep -E "(✅|❌|AI|Scraper)"
```

---

## If API Key Still Has Quota Issues

If `test_api_key_simple.py` shows quota error, then:

1. **The new API key also has no credits**
2. **You need a key with available credits**

**Solutions:**
- Get a different API key from: https://platform.openai.com/api-keys
- Make sure it has credits/quota
- Or add credits: https://platform.openai.com/account/billing

**Note:** Scraper will still work in fallback mode (keyword-based), but GPT will be more accurate.

---

## Quick Commands Summary

```bash
# 1. Test API key
python3 test_api_key_simple.py

# 2. Full restart
docker-compose down && docker-compose up -d

# 3. Wait
sleep 5

# 4. Verify
curl http://localhost:8000/api/scraper-status | python3 -m json.tool

# 5. Run scraper (if API key works)
curl -X POST http://localhost:8000/api/scrape_all
```

---

## ✅ Success Indicators

After these steps, you should see:
- `"api_key_working": true` in status endpoint
- `"AI classification successful"` in logs
- Scraper uses GPT for accurate results

If API key has quota issues, scraper will use fallback mode (still works, but less accurate).

