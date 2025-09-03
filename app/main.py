from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from urllib.parse import urlparse
from models.db_helper import (
    add_or_update_grant, 
    get_grants, 
    delete_grant_by_id, 
    url_exists
)
from models.init_db import create_tables
from app.utils.email_sender import send_email
from scrapers.smart_scraper import smart_scrape
import redis
import traceback


# === Initialize App ===
app = FastAPI()

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

# Secret key (change this!)
app.add_middleware(SessionMiddleware, secret_key="supersecretkey123")

# Hardcoded credentials
VALID_USERNAME = "admin"
VALID_PASSWORD = "secret123@"

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == VALID_USERNAME and password == VALID_PASSWORD:
        request.session["user"] = username
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)

# === Static + Templates Setup ===
templates = Jinja2Templates(directory="app/templates")
app.mount("/image", StaticFiles(directory="app/image"), name="image")

# === Initialize DB Tables ===
create_tables()
print("[INIT] Database tables created or verified.")

# === Redis Connection ===
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    redis_client.ping()
    print("[INFO] Redis connected successfully.")
except redis.ConnectionError as e:
    print("[ERROR] Redis connection error:", e)
    redis_client = None

# === Pydantic Models ===
class URLRequest(BaseModel):
    url: str

# === API: Check URL ===
@app.post("/api/check_url")
async def check_url(data: URLRequest):
    url = data.url.strip()
    domain = urlparse(url).netloc.replace("www.", "")
    print(f"[INFO] Checking URL: {url} | Domain: {domain}")

    from scrapers.router import SCRAPER_ROUTER
    scraper_func = SCRAPER_ROUTER.get(domain)

    if not scraper_func:
        return JSONResponse(
            content={"url": url, "status": "error", "reason": "No scraper found for this domain"},
            status_code=400
        )

    try:
        result = scraper_func()
    except Exception as e:
        print(f"[ERROR] Scraping failed:\n{traceback.format_exc()}")
        return JSONResponse(
            content={"url": url, "status": "error", "reason": str(e)},
            status_code=500
        )

    if result["status"] == "open":
        send_email(
            subject="Grant Open Notification",
            body=f"Grant is open at: {url}",
            to_email="attahania193@gmail.com"
        )
        add_or_update_grant(url, result["status"])

    return JSONResponse(content=result)

# === API: Scrape All with Celery ===
@app.post("/api/scrape_all")
async def scrape_all():
    try:
        from tasks.run_scrapers import run_all_scrapers
        run_all_scrapers.delay()
        return {"message": "Scraping started in background"}
    except Exception:
        print(f"[ERROR] Celery scraping task failed:\n{traceback.format_exc()}")
        return JSONResponse(
            content={"status": "error", "message": "Failed to start scraping task"},
            status_code=500
        )

# === API: Submit New URL ===
@app.post("/api/submit-url")
async def submit_url(data: URLRequest):
    url = data.url.strip()

    if url_exists(url):
        return JSONResponse({
            "status": "exists",
            "message": "URL already exists in the database."
        })

    try:
        result = smart_scrape(url)
    except Exception:
        print(f"[ERROR] smart_scrape failed:\n{traceback.format_exc()}")
        return JSONResponse({
            "status": "error",
            "message": "Scraping failed with exception."
        })

    if result["status"] == "error":
        return JSONResponse({
            "status": "error",
            "message": result.get("error", "Scraping failed")
        })

    add_or_update_grant(url, result["status"])

    return JSONResponse({
        "status": "success",
        "message": f"URL scraped and added with status: {result['status']}",
        "url": url,
        "scrape_status": result["status"]
    })

# === API: Delete Grant ===
@app.delete("/api/remove-url/{grant_id}")
async def remove_url(grant_id: int):
    try:
        delete_grant_by_id(grant_id)
        return JSONResponse({
            "status": "success",
            "message": "Grant removed successfully."
        })
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": "Failed to remove grant."},
            status_code=500
        )

# === UI: Home Dashboard ===
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    if "user" not in request.session:
        return RedirectResponse(url="/login", status_code=302)

    grants = get_grants()
    total_grants = len(grants)
    open_count = sum(1 for g in grants if g.status == "open")
    closed_count = sum(1 for g in grants if g.status == "closed")

    return templates.TemplateResponse("index.html", {
        "request": request,
        "grants": grants,
        "total_grants": total_grants,
        "open_count": open_count,
        "closed_count": closed_count,
        "current_year": 2025
    })
