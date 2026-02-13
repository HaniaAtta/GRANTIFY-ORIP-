# from fastapi import FastAPI, Request, Form
# from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
# from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles
# from pydantic import BaseModel
# from urllib.parse import urlparse
# from starlette.middleware.sessions import SessionMiddleware
# from models.db_helper import (
#     add_or_update_grant, 
#     get_grants, 
#     delete_grant_by_id, 
#     url_exists
# )
# from models.init_db import create_tables
# from app.utils.email_sender import send_email
# from scrapers.smart_scraper import smart_scrape
# from app.ai.classifier import classify_grant   # NEW
# import redis
# import traceback

# # === Initialize App ===
# app = FastAPI()

# # Session middleware
# app.add_middleware(SessionMiddleware, secret_key="supersecretkey123")

# # Hardcoded credentials
# VALID_USERNAME = "admin"
# VALID_PASSWORD = "secret123@"

# # === Static + Templates Setup ===
# templates = Jinja2Templates(directory="app/templates")
# app.mount("/image", StaticFiles(directory="app/image"), name="image")

# # === Initialize DB Tables ===
# create_tables()
# print("[INIT] Database tables created or verified.")

# # === Redis Connection ===
# try:
#     redis_client = redis.Redis(host='localhost', port=6379, db=0)
#     redis_client.ping()
#     print("[INFO] Redis connected successfully.")
# except redis.ConnectionError as e:
#     print("[ERROR] Redis connection error:", e)
#     redis_client = None

# # === Pydantic Models ===
# class URLRequest(BaseModel):
#     url: str

# # === Auth ===
# @app.get("/login", response_class=HTMLResponse)
# async def login_page(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request, "error": None})

# @app.post("/login")
# async def login(request: Request, username: str = Form(...), password: str = Form(...)):
#     if username == VALID_USERNAME and password == VALID_PASSWORD:
#         request.session["user"] = username
#         return RedirectResponse(url="/", status_code=302)
#     return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

# @app.get("/logout")
# async def logout(request: Request):
#     request.session.clear()
#     return RedirectResponse(url="/login", status_code=302)

# # === API: Check URL (uses specific scraper) ===
# @app.post("/api/check_url")
# async def check_url(data: URLRequest):
#     url = data.url.strip()
#     domain = urlparse(url).netloc.replace("www.", "")
#     print(f"[INFO] Checking URL: {url} | Domain: {domain}")

#     from scrapers.router import SCRAPER_ROUTER
#     scraper_func = SCRAPER_ROUTER.get(domain)

#     if not scraper_func:
#         return JSONResponse(
#             content={"url": url, "status": "error", "reason": "No scraper found for this domain"},
#             status_code=400
#         )

#     try:
#         scraped_text, landing_page = scraper_func()
#         result = classify_grant(url, scraped_text)
#     except Exception as e:
#         print(f"[ERROR] Scraping/classification failed:\n{traceback.format_exc()}")
#         return JSONResponse(
#             content={"url": url, "status": "error", "reason": str(e)},
#             status_code=500
#         )

#     add_or_update_grant(
#         url=url,
#         status=result["status"],
#         landing_page=landing_page,
#         categories=result.get("categories", [])
#     )

#     if result["status"] == "open":
#         send_email(
#             subject="Grant Open Notification",
#             body=f"Grant is open at: {url}",
#             to_email="attahania193@gmail.com"
#         )

#     return JSONResponse(content=result)

# # === API: Submit New URL (smart scraper, auto-discovery) ===
# @app.post("/api/submit-url")
# async def submit_url(data: URLRequest):
#     url = data.url.strip()

#     if url_exists(url):
#         return JSONResponse({
#             "status": "exists",
#             "message": "URL already exists in the database."
#         })

#     try:
#         scraped_text, landing_page = smart_scrape(url)
#         result = classify_grant(url, scraped_text)
#     except Exception:
#         print(f"[ERROR] smart_scrape/classify failed:\n{traceback.format_exc()}")
#         return JSONResponse({
#             "status": "error",
#             "message": "Scraping or classification failed."
#         })

#     add_or_update_grant(
#         url=url,
#         status=result["status"],
#         landing_page=landing_page,
#         categories=result.get("categories", [])
#     )

#     return JSONResponse({
#         "status": "success",
#         "url": url,
#         "status_prediction": result["status"],
#         "categories": result.get("categories", []),
#         "landing_page": landing_page
#     })

# # === API: Delete Grant ===
# @app.delete("/api/remove-url/{grant_id}")
# async def remove_url(grant_id: int):
#     try:
#         delete_grant_by_id(grant_id)
#         return JSONResponse({
#             "status": "success",
#             "message": "Grant removed successfully."
#         })
#     except Exception:
#         return JSONResponse(
#             content={"status": "error", "message": "Failed to remove grant."},
#             status_code=500
#         )

# # === UI: Home Dashboard ===
# @app.get("/", response_class=HTMLResponse)
# async def root(request: Request):
#     if "user" not in request.session:
#         return RedirectResponse(url="/login", status_code=302)

#     grants = get_grants()
#     total_grants = len(grants)
#     open_count = sum(1 for g in grants if g.status == "open")
#     closed_count = sum(1 for g in grants if g.status == "closed")

#     return templates.TemplateResponse("index.html", {
#         "request": request,
#         "grants": grants,
#         "total_grants": total_grants,
#         "open_count": open_count,
#         "closed_count": closed_count,
#         "current_year": 2025
#     })



# from fastapi import FastAPI, Request, Form
# from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
# from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles
# from pydantic import BaseModel
# from urllib.parse import urlparse
# from starlette.middleware.sessions import SessionMiddleware
# from models.db_helper import (
#     add_or_update_grant_site,
#     get_grant_sites,
#     delete_grant_site_by_id,
#     url_exists_in_grant_sites
# )
# from models.init_db import create_tables
# from app.utils.email_sender import send_email
# from scrapers.smart_scraper import smart_scrape
# from app.ai.classifier import classify_grant   # NEW
# import redis
# import traceback

# # === Initialize App ===
# app = FastAPI()

# # Session middleware
# app.add_middleware(SessionMiddleware, secret_key="supersecretkey123")

# # Hardcoded credentials
# VALID_USERNAME = "admin"
# VALID_PASSWORD = "secret123@"

# # === Static + Templates Setup ===
# templates = Jinja2Templates(directory="app/templates")
# app.mount("/image", StaticFiles(directory="app/image"), name="image")

# # === Initialize DB Tables ===
# create_tables()
# print("[INIT] Database tables created or verified.")

# # === Redis Connection ===
# try:
#     redis_client = redis.Redis(host='localhost', port=6379, db=0)
#     redis_client.ping()
#     print("[INFO] Redis connected successfully.")
# except redis.ConnectionError as e:
#     print("[ERROR] Redis connection error:", e)
#     redis_client = None

# # === Pydantic Models ===
# class URLRequest(BaseModel):
#     url: str

# # === Auth ===
# @app.get("/login", response_class=HTMLResponse)
# async def login_page(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request, "error": None})

# @app.post("/login")
# async def login(request: Request, username: str = Form(...), password: str = Form(...)):
#     if username == VALID_USERNAME and password == VALID_PASSWORD:
#         request.session["user"] = username
#         return RedirectResponse(url="/", status_code=302)
#     return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

# @app.get("/logout")
# async def logout(request: Request):
#     request.session.clear()
#     return RedirectResponse(url="/login", status_code=302)

# # === API: Check URL (uses specific scraper) ===
# @app.post("/api/check_url")
# async def check_url(data: URLRequest):
#     url = data.url.strip()
#     domain = urlparse(url).netloc.replace("www.", "")
#     print(f"[INFO] Checking URL: {url} | Domain: {domain}")

#     from scrapers.router import SCRAPER_ROUTER
#     scraper_func = SCRAPER_ROUTER.get(domain)

#     if not scraper_func:
#         return JSONResponse(
#             content={"url": url, "status": "error", "reason": "No scraper found for this domain"},
#             status_code=400
#         )

#     try:
#         scraped_text, landing_page = scraper_func()
#         result = classify_grant(url, scraped_text)
#     except Exception as e:
#         print(f"[ERROR] Scraping/classification failed:\n{traceback.format_exc()}")
#         return JSONResponse(
#             content={"url": url, "status": "error", "reason": str(e)},
#             status_code=500
#         )

#     add_or_update_grant(
#         url=url,
#         status=result["status"],
#         landing_page=landing_page,
#         categories=result.get("categories", [])
#     )

#     if result["status"] == "open":
#         send_email(
#             subject="Grant Open Notification",
#             body=f"Grant is open at: {url}",
#             to_email="attahania193@gmail.com"
#         )

#     return JSONResponse(content=result)

# # === API: Submit New URL (smart scraper, auto-discovery) ===
# @app.post("/api/submit-url")
# async def submit_url(data: URLRequest):
#     url = data.url.strip()

#     if url_exists(url):
#         return JSONResponse({
#             "status": "exists",
#             "message": "URL already exists in the database."
#         })

#     try:
#         scraped_text, landing_page = smart_scrape(url)
#         result = classify_grant(url, scraped_text)
#     except Exception:
#         print(f"[ERROR] smart_scrape/classify failed:\n{traceback.format_exc()}")
#         return JSONResponse({
#             "status": "error",
#             "message": "Scraping or classification failed."
#         })

#     add_or_update_grant(
#         url=url,
#         status=result["status"],
#         landing_page=landing_page,
#         categories=result.get("categories", [])
#     )

#     return JSONResponse({
#         "status": "success",
#         "url": url,
#         "status_prediction": result["status"],
#         "categories": result.get("categories", []),
#         "landing_page": landing_page
#     })

# # === API: Delete Grant ===
# @app.delete("/api/remove-url/{grant_id}")
# async def remove_url(grant_id: int):
#     try:
#         delete_grant_by_id(grant_id)
#         return JSONResponse({
#             "status": "success",
#             "message": "Grant removed successfully."
#         })
#     except Exception:
#         return JSONResponse(
#             content={"status": "error", "message": "Failed to remove grant."},
#             status_code=500
#         )

# # === UI: Home Dashboard ===
# @app.get("/", response_class=HTMLResponse)
# async def root(request: Request):
#     if "user" not in request.session:
#         return RedirectResponse(url="/login", status_code=302)

#     grants = get_grant_sites()  # <- use the correct function
#     total_grants = len(grants)
#     open_count = sum(1 for g in grants if g.status == "open")
#     closed_count = sum(1 for g in grants if g.status == "closed")

#     return templates.TemplateResponse("index.html", {
#         "request": request,
#         "grants": grants,
#         "total_grants": total_grants,
#         "open_count": open_count,
#         "closed_count": closed_count,
#         "current_year": 2025
#     })









# from fastapi import FastAPI, Request, Form, BackgroundTasks
# from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
# from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles
# from pydantic import BaseModel
# from urllib.parse import urlparse
# from starlette.middleware.sessions import SessionMiddleware
# from models.db_helper import (
#     add_or_update_grant_site,
#     get_grant_sites,
#     delete_grant_site_by_id,
#     url_exists_in_grant_sites
# )
# from models.init_db import create_tables
# from app.utils.email_sender import send_email
# from scrapers.smart_scraper import smart_scrape
# from app.ai.classifier import classify_grant
# import redis
# import traceback

# # === Initialize App ===
# app = FastAPI()

# # Session middleware
# app.add_middleware(SessionMiddleware, secret_key="supersecretkey123")

# # Hardcoded credentials
# VALID_USERNAME = "admin"
# VALID_PASSWORD = "secret123@"

# # === Static + Templates Setup ===
# templates = Jinja2Templates(directory="app/templates")
# app.mount("/image", StaticFiles(directory="app/image"), name="image")

# # === Initialize DB Tables ===
# create_tables()
# print("[INIT] Database tables created or verified.")

# # === Redis Connection ===
# try:
#     redis_client = redis.Redis(host='localhost', port=6379, db=0)
#     redis_client.ping()
#     print("[INFO] Redis connected successfully.")
# except redis.ConnectionError as e:
#     print("[ERROR] Redis connection error:", e)
#     redis_client = None

# # === Pydantic Models ===
# class URLRequest(BaseModel):
#     url: str

# # === Auth ===
# @app.get("/login", response_class=HTMLResponse)
# async def login_page(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request, "error": None})

# @app.post("/login")
# async def login(request: Request, username: str = Form(...), password: str = Form(...)):
#     if username == VALID_USERNAME and password == VALID_PASSWORD:
#         request.session["user"] = username
#         return RedirectResponse(url="/", status_code=302)
#     return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

# @app.get("/logout")
# async def logout(request: Request):
#     request.session.clear()
#     return RedirectResponse(url="/login", status_code=302)

# # === API: Check URL (uses specific scraper) ===
# @app.post("/api/check_url")
# async def check_url(data: URLRequest):
#     url = data.url.strip()
#     domain = urlparse(url).netloc.replace("www.", "")
#     print(f"[INFO] Checking URL: {url} | Domain: {domain}")

#     from scrapers.router import SCRAPER_ROUTER
#     scraper_func = SCRAPER_ROUTER.get(domain)

#     if not scraper_func:
#         return JSONResponse(
#             content={"url": url, "status": "error", "reason": "No scraper found for this domain"},
#             status_code=400
#         )

#     try:
#         scraped_text, landing_page = scraper_func()
#         result = classify_grant(url, scraped_text)
#     except Exception as e:
#         print(f"[ERROR] Scraping/classification failed:\n{traceback.format_exc()}")
#         return JSONResponse(
#             content={"url": url, "status": "error", "reason": str(e)},
#             status_code=500
#         )

#     add_or_update_grant_site(
#         url=url,
#         status=result["status"],
#         landing_page=landing_page,
#         categories=result.get("categories", [])
#     )

#     if result["status"] == "open":
#         send_email(
#             subject="Grant Open Notification",
#             body=f"Grant is open at: {url}",
#             to_email="attahania193@gmail.com"
#         )

#     return JSONResponse(content=result)

# # === API: Submit New URL (smart scraper, auto-discovery) ===
# @app.post("/api/submit-url")
# async def submit_url(data: URLRequest):
#     url = data.url.strip()

#     if url_exists_in_grant_sites(url):
#         return JSONResponse({
#             "status": "exists",
#             "message": "URL already exists in the database."
#         })

#     try:
#         scraped_text, landing_page = smart_scrape(url)
#         result = classify_grant(url, scraped_text)
#     except Exception:
#         print(f"[ERROR] smart_scrape/classify failed:\n{traceback.format_exc()}")
#         return JSONResponse({
#             "status": "error",
#             "message": "Scraping or classification failed."
#         })

#     add_or_update_grant_site(
#         url=url,
#         status=result["status"],
#         landing_page=landing_page,
#         categories=result.get("categories", [])
#     )

#     return JSONResponse({
#         "status": "success",
#         "url": url,
#         "status_prediction": result["status"],
#         "categories": result.get("categories", []),
#         "landing_page": landing_page
#     })

# # === API: Delete Grant ===
# @app.delete("/api/remove-url/{grant_id}")
# async def remove_url(grant_id: int):
#     try:
#         delete_grant_site_by_id(grant_id)
#         return JSONResponse({
#             "status": "success",
#             "message": "Grant removed successfully."
#         })
#     except Exception:
#         return JSONResponse(
#             content={"status": "error", "message": "Failed to remove grant."},
#             status_code=500
#         )

# # === API: Scrape All Grants in Background ===
# def run_all_scrapers():
#     from scrapers.router import SCRAPER_ROUTER
#     for domain, scraper_func in SCRAPER_ROUTER.items():
#         try:
#             print(f"[INFO] Running scraper for: {domain}")
#             scraped_text, landing_page = scraper_func()
#             result = classify_grant(domain, scraped_text)

#             add_or_update_grant_site(
#                 url=domain,
#                 status=result["status"],
#                 landing_page=landing_page,
#                 categories=result.get("categories", [])
#             )

#             if result["status"] == "open":
#                 send_email(
#                     subject="Grant Open Notification",
#                     body=f"Grant is open at: {domain}",
#                     to_email="attahania193@gmail.com"
#                 )
#         except Exception as e:
#             print(f"[ERROR] Scraper for {domain} failed:\n{traceback.format_exc()}")

# @app.post("/api/scrape_all")
# async def scrape_all(background_tasks: BackgroundTasks):
#     background_tasks.add_task(run_all_scrapers)
#     return {"message": "Scraping started in background"}

# # === UI: Home Dashboard ===
# @app.get("/", response_class=HTMLResponse)
# async def root(request: Request):
#     if "user" not in request.session:
#         return RedirectResponse(url="/login", status_code=302)

#     grants = get_grant_sites()
#     total_grants = len(grants)
#     open_count = sum(1 for g in grants if g.status == "open")
#     closed_count = sum(1 for g in grants if g.status == "closed")

#     return templates.TemplateResponse("index.html", {
#         "request": request,
#         "grants": grants,
#         "total_grants": total_grants,
#         "open_count": open_count,
#         "closed_count": closed_count,
#         "current_year": 2025
#     })













# import traceback
# from datetime import datetime
# from urllib.parse import urlparse

# import redis
# from fastapi import FastAPI, Request, Form, BackgroundTasks
# from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from pydantic import BaseModel
# from starlette.middleware.sessions import SessionMiddleware

# from models.db_helper import (
#     add_or_update_grant_site,
#     get_grant_sites,
#     delete_grant_site_by_id,
#     url_exists_in_grant_sites,
# )
# from models.init_db import create_tables
# from app.utils.email_sender import send_email
# from scrapers.smart_scraper import smart_scrape
# from app.ai.classifier import classify_grant

# # === Initialize App ===
# app = FastAPI()

# # Session middleware
# app.add_middleware(SessionMiddleware, secret_key="supersecretkey123")

# # Hardcoded credentials (⚠️ move to env vars later)
# VALID_USERNAME = "admin"
# VALID_PASSWORD = "secret123@"

# # === Static + Templates Setup ===
# templates = Jinja2Templates(directory="app/templates")
# app.mount("/image", StaticFiles(directory="app/image"), name="image")

# # === Initialize DB Tables ===
# create_tables()
# print("[INIT] Database tables created or verified.")

# # === Redis Connection ===
# try:
#     redis_client = redis.Redis(host="localhost", port=6379, db=0)
#     redis_client.ping()
#     print("[INFO] Redis connected successfully.")
# except redis.ConnectionError as e:
#     print("[ERROR] Redis connection error:", e)
#     redis_client = None


# # === Pydantic Models ===
# class URLRequest(BaseModel):
#     url: str


# # === Auth ===
# @app.get("/login", response_class=HTMLResponse)
# async def login_page(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request, "error": None})


# @app.post("/login")
# async def login(request: Request, username: str = Form(...), password: str = Form(...)):
#     if username == VALID_USERNAME and password == VALID_PASSWORD:
#         request.session["user"] = username
#         return RedirectResponse(url="/", status_code=302)
#     return templates.TemplateResponse(
#         "login.html", {"request": request, "error": "Invalid credentials"}
#     )


# @app.get("/logout")
# async def logout(request: Request):
#     request.session.clear()
#     return RedirectResponse(url="/login", status_code=302)


# # === API: Check URL (uses specific scraper) ===
# @app.post("/api/check_url")
# async def check_url(data: URLRequest):
#     url = data.url.strip()
#     domain = urlparse(url).netloc.replace("www.", "")
#     print(f"[INFO] Checking URL: {url} | Domain: {domain}")

#     from scrapers.router import SCRAPER_ROUTER

#     scraper_func = SCRAPER_ROUTER.get(domain)

#     if not scraper_func:
#         return JSONResponse(
#             content={"url": url, "status": "error", "reason": "No scraper found for this domain"},
#             status_code=400,
#         )

#     try:
#         scraped_text, landing_page = scraper_func()
#         result = classify_grant(url, scraped_text)
#     except Exception as e:
#         print(f"[ERROR] Scraping/classification failed:\n{traceback.format_exc()}")
#         return JSONResponse(
#             content={"url": url, "status": "error", "reason": str(e)},
#             status_code=500,
#         )

#     add_or_update_grant_site(
#         url=url,
#         status=result["status"],
#         landing_page=landing_page,
#         categories=result.get("categories", []),
#     )

#     if result["status"] == "open":
#         send_email(
#             subject="Grant Open Notification",
#             body=f"Grant is open at: {url}",
#             to_email="attahania193@gmail.com",
#         )

#     return JSONResponse(content=result)


# # === API: Submit New URL (smart scraper, auto-discovery) ===
# @app.post("/api/submit-url")
# async def submit_url(data: URLRequest):
#     url = data.url.strip()

#     if url_exists_in_grant_sites(url):
#         return JSONResponse(
#             {"status": "exists", "message": "URL already exists in the database."}
#         )

#     try:
#         scraped_text, landing_page = smart_scrape(url)
#         result = classify_grant(url, scraped_text)
#     except Exception:
#         print(f"[ERROR] smart_scrape/classify failed:\n{traceback.format_exc()}")
#         return JSONResponse({"status": "error", "message": "Scraping or classification failed."})

#     add_or_update_grant_site(
#         url=url,
#         status=result["status"],
#         landing_page=landing_page,
#         categories=result.get("categories", []),
#     )

#     return JSONResponse(
#         {
#             "status": "success",
#             "url": url,
#             "status_prediction": result["status"],
#             "categories": result.get("categories", []),
#             "landing_page": landing_page,
#         }
#     )


# # === API: Delete Grant ===
# @app.delete("/api/remove-url/{grant_id}")
# async def remove_url(grant_id: int):
#     try:
#         delete_grant_site_by_id(grant_id)
#         return JSONResponse({"status": "success", "message": "Grant removed successfully."})
#     except Exception:
#         return JSONResponse(
#             content={"status": "error", "message": "Failed to remove grant."}, status_code=500
#         )


# === API: Scrape All Grants in Background ===
# def run_all_scrapers():
#     from scrapers.router import SCRAPER_ROUTER

#     for domain, scraper_func in SCRAPER_ROUTER.items():
#         try:
#             print(f"[INFO] Running scraper for: {domain}")
#             scraped_text, landing_page = scraper_func()
#             result = classify_grant(domain, scraped_text)

#             add_or_update_grant_site(
#                 url=domain,
#                 status=result["status"],
#                 landing_page=landing_page,
#                 categories=result.get("categories", []),
#             )

#             if result["status"] == "open":
#                 send_email(
#                     subject="Grant Open Notification",
#                     body=f"Grant is open at: {domain}",
#                     to_email="attahania193@gmail.com",
#                 )
#         except Exception as e:
#             print(f"[ERROR] Scraper for {domain} failed:\n{traceback.format_exc()}")


# from tasks.run_scrapers import run_all_scrapers as celery_scrape


# @app.post("/api/scrape_all")
# async def scrape_all():
#     # Trigger Celery task asynchronously
#     celery_scrape.delay()
#     return {"message": "Scraping started in background via Celery"}

# # === UI: Home Dashboard ===
# @app.get("/", response_class=HTMLResponse)
# async def root(request: Request):
#     if "user" not in request.session:
#         return RedirectResponse(url="/login", status_code=302)

#     grants = get_grant_sites()
#     total_grants = len(grants)
#     open_count = sum(1 for g in grants if g.status == "open")
#     closed_count = sum(1 for g in grants if g.status == "closed")

#     # ✅ Category counts for stats cards
#     category_counts = {
#         "Climate": sum(1 for g in grants if any("climate" in c.lower() for c in g.categories)),
#         "Women": sum(1 for g in grants if any("women" in c.lower() for c in g.categories)),
#         "Development": sum(
#             1 for g in grants if any("development" in c.lower() for c in g.categories)
#         ),
#         "Education": sum(1 for g in grants if any("education" in c.lower() for c in g.categories)),
#         "Other": sum(
#             1
#             for g in grants
#             if not any(
#                 kw in " ".join(c.lower() for c in g.categories)
#                 for kw in ["climate", "women", "development", "education"]
#             )
#         ),
#     }

#     return templates.TemplateResponse(
#         "index.html",
#         {
#             "request": request,
#             "grants": grants,
#             "total_grants": total_grants,
#             "open_count": open_count,
#             "closed_count": closed_count,
#             "category_counts": category_counts,
#             "current_year": datetime.now().year,
#         },
#     )


import json
import logging
import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import os
from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.dialects.postgresql import JSON
from models.db_helper import (
    get_db,
    GrantSite,
    get_grant_sites,
    add_or_update_grant_site,
    delete_grant_site_by_id,
)
from scrapers.bs_scrapper.scraper import scrape_page
from tasks.run_scrapers import run_all_scrapers

logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
BASE_DIR = os.path.dirname(__file__)
CATEGORIES_PATH = os.path.join(BASE_DIR, "config", "categories.json")

# === Load categories.json safely ===
try:
    with open(CATEGORIES_PATH, "r") as f:
        raw_data = json.load(f)
except Exception as e:
    print(f"⚠️ Could not load categories.json: {e}")
    raw_data = []

# Flatten into unique categories
categories = sorted({cat for entry in raw_data for cat in entry.get("categories", [])})

# === Session Middleware ===
app.add_middleware(SessionMiddleware, secret_key="supersecretkey123")

# === Auth credentials ===
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "secret123@"
NORMAL_USERNAME = "user"
NORMAL_PASSWORD = "user123@"

# === Thread pool for blocking ops ===
executor = ThreadPoolExecutor(max_workers=5)


# ======================
#   CATEGORY ROUTE
# ======================
@app.get("/category/{cat}", response_class=HTMLResponse)
def category_page(cat: str, request: Request, db: Session = Depends(get_db)):
    grants = db.query(GrantSite).filter(
        GrantSite.categories.op("@>")(f'["{cat}"]')
    ).all()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "grants": grants,
            "categories": categories,
            "selected_category": cat,
        },
    )


# ======================
#   AUTH ROUTES
# ======================
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    # Check admin credentials
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        request.session["user"] = username
        request.session["is_admin"] = True
        return RedirectResponse(url="/", status_code=302)
    # Check normal user credentials
    elif username == NORMAL_USERNAME and password == NORMAL_PASSWORD:
        request.session["user"] = username
        request.session["is_admin"] = False
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": "Invalid credentials"}
    )


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)


# ======================
#   API ROUTES
# ======================
@app.post("/api/submit-url")
async def submit_url(data: dict, request: Request, db: Session = Depends(get_db)):
    from urllib.parse import urlparse

    # Check if user is logged in
    if "user" not in request.session:
        return {"status": "error", "message": "Authentication required"}

    url = data.get("url")
    selected_categories = data.get("categories", [])

    if not url:
        return {"status": "error", "message": "URL is required"}

    if not isinstance(selected_categories, list):
        selected_categories = [selected_categories]

    # Normalize URL
    parsed = urlparse(url)
    normalized_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path.rstrip('/')}"

    # ✅ Check duplicate in DB (base URL or landing page)
    existing = db.query(GrantSite).filter(
        (GrantSite.url == normalized_url) | (GrantSite.landing_page == normalized_url)
    ).first()
    if existing:
        return {"status": "error", "message": "URL or landing page already exists in database"}

    try:
        # Run scraper in executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, scrape_page, normalized_url)

        if result.get("status") == "error":
            return {"status": "error", "message": result.get("error", "Scraping failed")}

        # Ensure dates are Python datetime or None
        open_date = result.get("open_date")
        close_date = result.get("close_date")
        
        # Convert string dates to datetime objects
        if isinstance(open_date, str) and open_date not in ("null", "", "None"):
            try:
                from datetime import datetime
                open_date = datetime.strptime(open_date, "%Y-%m-%d")
            except:
                open_date = None
        elif open_date == "null" or open_date == "":
            open_date = None
            
        if isinstance(close_date, str) and close_date not in ("null", "", "None"):
            try:
                from datetime import datetime
                close_date = datetime.strptime(close_date, "%Y-%m-%d")
            except:
                close_date = None
        elif close_date == "null" or close_date == "":
            close_date = None

        # Decide categories to save
        categories_to_save = selected_categories or result.get("thematic_areas") or ["Other"]

        logger.info(f"Scraper result for {normalized_url}: {result}")

        # ✅ Mark as user-added to preserve it during batch scrapes
        add_or_update_grant_site(
            url=result.get("base_url", normalized_url),
            status=result.get("status", "unknown"),
            landing_page=result.get("landing_page", normalized_url),
            categories=categories_to_save,
            regions=result.get("regions", []),
            applicable_to_pakistan=result.get("applicable_to_pakistan", False),
            open_date=open_date,
            close_date=close_date,
            eligibility=result.get("eligibility", ""),
            thematic_areas=result.get("thematic_areas", []),
            is_user_added=True,  # ✅ Mark as user-added
            preserve_user_flag=False
        )

        return {"status": "success", "message": "Grant added and scraped successfully"}

    except Exception as e:
        logger.error(f"Error adding or scraping grant {url}: {str(e)}")
        return {"status": "error", "message": str(e)}


# @app.post("/api/scrape_all")
# async def scrape_all(request: Request):
#     if "user" not in request.session:
#         return RedirectResponse(url="/login", status_code=302)

#     grants = get_grant_sites()

#     async def process_grant(grant):
#         try:
#             loop = asyncio.get_event_loop()
#             result = await loop.run_in_executor(executor, scrape_page, grant.url)

#             add_or_update_grant_site(
#                 url=result["base_url"],
#                 status=result["status"],
#                 landing_page=result["landing_page"],
#                 categories=result.get("categories", grant.categories or []),
#                 regions=result.get("regions", []),
#                 applicable_to_pakistan=result.get("applicable_to_pakistan", False),
#                 open_date=result.get("open_date"),
#                 close_date=result.get("close_date"),
#                 eligibility=result.get("eligibility", ""),
#                 thematic_areas=result.get("thematic_areas", []),
#             )

#             return {"url": grant.url, "status": "success"}
#         except Exception as e:
#             logger.error(f"Error scraping {grant.url}: {str(e)}")
#             return {"url": grant.url, "status": "error", "error": str(e)}

#     results = []
#     for i in range(0, len(grants), 3):
#         batch = grants[i : i + 3]
#         batch_results = await asyncio.gather(*[process_grant(grant) for grant in batch])
#         results.extend(batch_results)
#         await asyncio.sleep(1)

#     success_count = sum(1 for r in results if r["status"] == "success")

#     return {
#         "status": "success",
#         "message": f"Processed {len(grants)} grants, {success_count} successful",
#         "results": results,
#     }

from tasks.run_scrapers import run_all_scrapers

@app.post("/api/scrape_all")
async def scrape_all(request: Request):
    # if "user" not in request.session:
    #     return RedirectResponse(url="/login", status_code=302)
    
    # Trigger Celery background task
    run_all_scrapers.delay()  # ✅ This runs in the background
    return {"message": "Scraping started in background"}

# ======================
#   DASHBOARD ROUTE
# ======================
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    if "user" not in request.session:
        return RedirectResponse(url="/login", status_code=302)

    grants = db.query(GrantSite).all()
    is_admin = request.session.get("is_admin", False)

    def sort_key(g):
        if g.status and g.status.lower() == "open":
            return (0, g.open_date or datetime.min)
        elif g.status and g.status.lower() == "closed":
            return (1, g.close_date or datetime.min)
        else:
            return (2, datetime.min)

    grants_sorted = sorted(grants, key=sort_key)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "grants": grants_sorted,
            "categories": categories,  # ✅ only category strings
            "total_grants": len(grants),
            "open_count": sum(
                1 for g in grants if g.status and g.status.lower() == "open"
            ),
            "closed_count": sum(
                1 for g in grants if g.status and g.status.lower() == "closed"
            ),
            "current_year": datetime.now().year,
            "is_admin": is_admin,  # ✅ Pass admin flag to template
        },
    )

@app.delete("/api/remove-url/{grant_id}")
async def remove_url(grant_id: int, request: Request, db: Session = Depends(get_db)):
    # ✅ Only admins can delete
    if "user" not in request.session or not request.session.get("is_admin", False):
        return {"status": "error", "message": "Admin access required"}
    
    try:
        deleted = delete_grant_site_by_id(grant_id, db)
        if deleted:
            return {"status": "success", "message": f"Grant ID {grant_id} removed successfully"}
        else:
            return {"status": "error", "message": "Grant not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
