# 🔧 Fix OpenAI API Quota Exceeded

## ❌ Problem:
Your OpenAI API key has exceeded its quota. The error shows:
```
Error code: 429 - insufficient_quota
You exceeded your current quota, please check your plan and billing details.
```

## ✅ Solutions:

### Option 1: Update API Key (Recommended)

1. **Get a new OpenAI API key:**
   - Go to: https://platform.openai.com/api-keys
   - Create a new API key
   - Make sure it has credits/quota available

2. **Update .env file:**
   ```bash
   # Edit .env file
   nano .env
   # Or
   open .env
   ```

3. **Replace the API key:**
   ```env
   OPENAI_API_KEY=OPENAI_API_KEY_HERE
   ```

4. **Restart services:**
   ```bash
   docker-compose restart fastapi
   ```

5. **Verify:**
   ```bash
   curl http://localhost:8000/api/scraper-status
   ```

---

### Option 2: Add Credits to Existing Key

1. **Go to OpenAI Dashboard:**
   - https://platform.openai.com/account/billing
   - Add credits to your account

2. **Wait a few minutes** for quota to refresh

3. **Verify:**
   ```bash
   curl http://localhost:8000/api/scraper-status
   ```

---

### Option 3: Use Fallback Mode (Temporary)

The scraper will automatically use keyword-based fallback when API quota is exceeded. This works but is less accurate than GPT.

**Current behavior:**
- ✅ Scraper still works (uses keyword fallback)
- ⚠️ Less accurate classification
- ⚠️ May have more false positives/negatives

---

## 🔍 Verify Fix

### Check API Key Status:
```bash
curl http://localhost:8000/api/scraper-status | python3 -m json.tool
```

**Should show:**
```json
{
  "api_key_configured": true,
  "api_key_working": true,  // ✅ Should be true after fix
  "api_test_response": "OK",
  "database_connected": true,
  "grants_count": 156
}
```

### Test API Key Directly:
```bash
python3 -c "
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    print('❌ API key not set')
else:
    print(f'✅ API key found: {api_key[:10]}...')
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{'role': 'user', 'content': 'Say OK'}],
            max_tokens=5
        )
        print(f'✅ API key working! Response: {response.choices[0].message.content}')
    except Exception as e:
        if 'quota' in str(e).lower() or '429' in str(e):
            print('❌ API quota exceeded. Please update API key or add credits.')
        else:
            print(f'❌ API error: {e}')
"
```

---

## 📋 Quick Fix Steps

```bash
# 1. Update .env file with new API key
nano .env
# Change: OPENAI_API_KEY=OPENAI_API_KEY_HERE

# 2. Restart FastAPI
docker-compose restart fastapi

# 3. Wait a few seconds
sleep 5

# 4. Verify
curl http://localhost:8000/api/scraper-status | python3 -m json.tool

# 5. Test scraper
curl -X POST http://localhost:8000/api/scrape_all
```

---

## ⚠️ Important Notes

1. **Free tier limits:**
   - OpenAI free tier has very limited quota
   - Consider upgrading to paid plan for production use

2. **API key security:**
   - Never commit API keys to git
   - Keep .env file in .gitignore
   - Rotate keys regularly

3. **Fallback mode:**
   - Scraper will still work without API (keyword-based)
   - But accuracy will be lower
   - Best to fix API key for production use

---

## 🎯 Summary

**Problem:** API quota exceeded  
**Solution:** Update OPENAI_API_KEY in .env file  
**Verify:** Check status endpoint shows `api_key_working: true`

The scraper will work in fallback mode, but for best results, update your API key! 🚀

