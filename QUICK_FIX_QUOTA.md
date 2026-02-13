# 🔧 Quick Fix: Why API Key Still Shows Quota Error

## Possible Reasons:

### 1. Docker is Using OLD Key (Most Common)
Even though you updated `.env`, Docker container might still have the old key cached.

**Fix:**
```bash
# Complete restart to reload .env
docker-compose down
docker-compose up -d
sleep 5
curl http://localhost:8000/api/scraper-status
```

---

### 2. New API Key ALSO Has Quota Issues
Free tier OpenAI keys have VERY limited quota. If you got another free key, it might also be exhausted.

**Check:**
```bash
# Test the key directly (not through Docker)
python3 test_api_key_simple.py
```

If this also shows quota error, then the new key itself has no credits.

**Fix:**
- Get a key from a **different OpenAI account** (with credits)
- Or add credits to your account: https://platform.openai.com/account/billing
- Or use a paid API key

---

### 3. FastAPI Service Didn't Reload
FastAPI might be caching the old key in memory.

**Fix:**
```bash
# Force restart FastAPI
docker-compose restart fastapi
sleep 5

# Or full restart
docker-compose down
docker-compose up -d
```

---

## 🔍 Debug Steps:

### Step 1: Run Debug Script
```bash
./debug_api_key.sh
```

This will show:
- What's in `.env` file
- What Docker sees
- If keys match
- If the key works locally

---

### Step 2: Compare Keys
```bash
# Check .env
grep OPENAI_API_KEY .env

# Check Docker
docker-compose exec fastapi printenv OPENAI_API_KEY
```

If they're different → Docker needs restart

---

### Step 3: Test Key Directly
```bash
# Test without Docker
python3 test_api_key_simple.py
```

If this works → Docker issue
If this fails → Key has quota issues

---

## ✅ Complete Fix Workflow:

```bash
# 1. Debug first
./debug_api_key.sh

# 2. If keys don't match, full restart
docker-compose down
docker-compose up -d

# 3. Wait
sleep 5

# 4. Verify
curl http://localhost:8000/api/scraper-status | python3 -m json.tool

# 5. If still quota error, test key directly
python3 test_api_key_simple.py
```

---

## 💡 Most Likely Issue:

**Free tier API keys have VERY limited quota** (like $5 worth). If you:
- Used the key before
- Got another free key from same account
- The account has no credits

Then the new key will also show quota errors.

**Solution:** Get a key from an account that has credits, or add credits to your account.

---

## 🚀 Quick Test:

Run this to see what's wrong:
```bash
./debug_api_key.sh
```

This will tell you exactly what's happening! 🔍

