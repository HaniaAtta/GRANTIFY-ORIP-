# 📊 How to Monitor Scraper & Verify API Key

## ✅ Quick Verification Commands

### 1. Check Scraper Status & API Key

```bash
# Check if API key is working and scraper status
curl http://localhost:8000/api/scraper-status | python3 -m json.tool
```

This shows:
- ✅ API key configured
- ✅ API key working (tests OpenAI connection)
- ✅ Database connected
- ✅ Number of grants
- ✅ Recent updates (last 24 hours)

---

### 2. Check FastAPI Logs

```bash
# Watch logs in real-time
docker-compose logs -f fastapi

# Or check last 100 lines
docker-compose logs fastapi --tail 100
```

**Look for:**
- ✅ `"Scraping started via Celery"` or `"Scraping completed directly"`
- ✅ `"AI classification successful"`
- ✅ `"Scraper finished for [URL]"`
- ❌ `"AI classification failed"` - API key issue
- ❌ `"Error scraping"` - Scraping issue

---

### 3. Check Database Updates

```bash
# Count grants
python3 -c "
from models.db_helper import get_grant_sites
from datetime import datetime, timedelta
grants = get_grant_sites()
recent = [g for g in grants if g.last_updated and g.last_updated > datetime.utcnow() - timedelta(hours=1)]
print(f'Total grants: {len(grants)}')
print(f'Updated in last hour: {len(recent)}')
"
```

---

### 4. Test API Key Directly

```bash
# Test OpenAI API key
python3 -c "
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    print('❌ API key not set in .env')
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
        print(f'❌ API key error: {e}')
"
```

---

## 🔍 What to Look For

### ✅ Success Indicators:

1. **API Endpoint Response:**
   ```json
   {
     "message": "Scraping started in background",
     "method": "celery" or "direct"
   }
   ```

2. **Status Endpoint Shows:**
   ```json
   {
     "api_key_configured": true,
     "api_key_working": true,
     "database_connected": true,
     "grants_count": 158,
     "recent_updates": 5
   }
   ```

3. **Logs Show:**
   ```
   ✅ AI classification successful for [URL]
   ✅ Scraper finished for [URL]
   ✅ Scraping completed successfully
   ```

4. **Database Updates:**
   - `last_updated` timestamps are recent
   - Status, dates, regions are updated
   - New data appears in dashboard

---

### ❌ Error Indicators:

1. **API Key Issues:**
   ```
   ❌ AI classification failed: Invalid API key
   ❌ Missing OPENAI_API_KEY
   ❌ API key error: insufficient_quota
   ```

2. **Scraping Issues:**
   ```
   ❌ Error scraping [URL]: Connection timeout
   ❌ Both requests & Selenium failed
   ```

3. **Database Issues:**
   ```
   ❌ Database connection error
   ❌ Error updating grant
   ```

---

## 🚀 Complete Monitoring Workflow

```bash
# 1. Check status
curl http://localhost:8000/api/scraper-status

# 2. Run scraper
curl -X POST http://localhost:8000/api/scrape_all

# 3. Monitor logs
docker-compose logs -f fastapi | grep -E "(✅|❌|AI|Scraper|Error)"

# 4. Check database after 5 minutes
python3 -c "
from models.db_helper import get_grant_sites
from datetime import datetime, timedelta
grants = get_grant_sites()
recent = [g for g in grants if g.last_updated and g.last_updated > datetime.utcnow() - timedelta(minutes=5)]
print(f'Updated in last 5 min: {len(recent)}')
for g in recent[:5]:
    print(f'  - {g.url}: {g.status}')
"
```

---

## 📋 Quick Checklist

After running scraper, verify:

- [ ] Status endpoint shows `api_key_working: true`
- [ ] Logs show `"AI classification successful"`
- [ ] No `"API key error"` messages
- [ ] Database shows recent `last_updated` timestamps
- [ ] Dashboard shows updated grant data
- [ ] No `"Error scraping"` messages in logs

---

## 🎯 One-Command Check

```bash
# Check everything at once
echo "=== Scraper Status ===" && \
curl -s http://localhost:8000/api/scraper-status | python3 -m json.tool && \
echo -e "\n=== Recent Logs ===" && \
docker-compose logs fastapi --tail 20 | grep -E "(✅|❌|AI|Scraper)"
```

This gives you a complete status overview! 🚀

