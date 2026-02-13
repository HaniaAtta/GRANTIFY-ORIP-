import time
import logging
from datetime import datetime
from config import celery_app
from models.db_helper import add_or_update_grant_site, get_grant_sites
from app.utils.email_sender import send_email
from scrapers.bs_scrapper.scraper import scrape_page

celery = celery_app

# === Configure logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def run_all_scrapers(self):
    """
    Celery task: scrape all grants from NeonDB.
    
    ✅ NOW READS FROM NEONDB ONLY (NO categories.json DEPENDENCY)
    
    Benefits:
    - Deleted websites stay deleted (not in DB, won't be scraped)
    - Updates remain permanent (all operations on NeonDB)
    - No dependency on categories.json file
    - Only scrapes URLs that exist in the database
    - User-added URLs are preserved
    """
    all_results = []
    
    # ✅ Get all grants from NeonDB (not from categories.json)
    logger.info(f"[{datetime.utcnow()}] Loading grants from NeonDB...")
    grants_from_db = get_grant_sites()
    logger.info(f"[{datetime.utcnow()}] Found {len(grants_from_db)} grants in NeonDB to scrape")

    if not grants_from_db:
        logger.warning(f"[{datetime.utcnow()}] ⚠️ No grants found in NeonDB. Nothing to scrape.")
        return []

    for i, grant in enumerate(grants_from_db, 1):
        url = grant.url
        grant_id = grant.id
        is_user_added = grant.is_user_added
        
        # Fix URL if missing scheme
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            logger.info(f"[{datetime.utcnow()}] Fixed URL (added https://): {url}")
        
        logger.info(f"[{datetime.utcnow()}] [{i}/{len(grants_from_db)}] Starting scraper for ID {grant_id}: {url}")

        try:
            # ✅ Scrape the URL
            result = scrape_page(url)

            # Fallbacks - preserve existing data if scraper doesn't provide it
            base_url = result.get("base_url") or url
            landing_page = result.get("landing_page") or url
            status = result.get("status", "unknown")
            
            # Preserve existing categories if scraper doesn't provide new ones
            categories = result.get("categories", []) or grant.categories or []
            regions = result.get("regions", []) or grant.regions or []
            thematic_areas = result.get("thematic_areas", []) or grant.thematic_areas or []
            eligibility = result.get("eligibility", "") or grant.eligibility or ""

            # ✅ Update the existing record in NeonDB
            # ✅ preserve_user_flag=True ensures user-added URLs are not overwritten
            # ✅ This will UPDATE the existing record (not create new one)
            add_or_update_grant_site(
                url=base_url,  # Use existing URL from DB
                status=status,
                landing_page=landing_page,
                categories=categories,
                regions=regions,
                applicable_to_pakistan=result.get("applicable_to_pakistan", False),
                open_date=result.get("open_date"),
                close_date=result.get("close_date"),
                eligibility=eligibility,
                thematic_areas=thematic_areas,
                is_user_added=is_user_added,  # ✅ Preserve user-added flag
                preserve_user_flag=True  # ✅ Don't overwrite user-added URLs
            )

            all_results.append({
                "id": grant_id,
                "url": base_url,
                "landing_page": landing_page,
                "status": status,
                "categories": categories,
            })

            logger.info(f"[{datetime.utcnow()}] ✅ Scraper finished for {url} (ID: {grant_id})")

        except Exception as exc:
            logger.error(f"[{datetime.utcnow()}] ❌ Error scraping {url} (ID: {grant_id}): {exc}", exc_info=True)
            all_results.append({
                "id": grant_id,
                "url": url,
                "status": "error",
                "error": str(exc),
            })
            # Uncomment to retry failed scraping
            # raise self.retry(exc=exc)

        time.sleep(5)  # throttle requests

    # === Send summary email ===
    try:
        success_count = sum(1 for r in all_results if r.get("status") != "error")
        fail_count = len(all_results) - success_count

        send_email(
            subject="Grant Scraper Run Completed (NeonDB)",
            body=f"✅ {success_count} successful, ❌ {fail_count} failed, total {len(all_results)} grants scraped from NeonDB",
            to_email="attahania193@gmail.com",
        )
        logger.info(f"[{datetime.utcnow()}] ✅ Email notification sent")
    except Exception as e:
        logger.warning(f"[{datetime.utcnow()}] ⚠️ Failed to send email: {e}", exc_info=True)

    return all_results
