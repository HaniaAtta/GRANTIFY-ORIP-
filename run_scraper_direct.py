#!/usr/bin/env python3
"""
Run scraper directly without Celery.
Useful when Celery container has issues.
"""

import sys
import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

def run_scraper_direct():
    """Run scraper directly without Celery decorator."""
    print("=" * 60)
    print("Running Scraper Directly (No Celery)")
    print("=" * 60)
    print()
    
    try:
        from models.db_helper import add_or_update_grant_site, get_grant_sites
        from scrapers.bs_scrapper.scraper import scrape_page
        
        print("✅ Imported modules")
        print("🚀 Starting scraping...")
        print()
        
        all_results = []
        
        # Get all grants from NeonDB
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
                # Scrape the URL
                result = scrape_page(url)
                
                # Fallbacks
                base_url = result.get("base_url") or url
                landing_page = result.get("landing_page") or url
                status = result.get("status", "unknown")
                
                # Preserve existing data if scraper doesn't provide it
                categories = result.get("categories", []) or grant.categories or []
                regions = result.get("regions", []) or grant.regions or []
                thematic_areas = result.get("thematic_areas", []) or grant.thematic_areas or []
                eligibility = result.get("eligibility", "") or grant.eligibility or ""
                
                # Update the existing record in NeonDB
                add_or_update_grant_site(
                    url=base_url,
                    status=status,
                    landing_page=landing_page,
                    categories=categories,
                    regions=regions,
                    applicable_to_pakistan=result.get("applicable_to_pakistan", False),
                    open_date=result.get("open_date"),
                    close_date=result.get("close_date"),
                    eligibility=eligibility,
                    thematic_areas=thematic_areas,
                    is_user_added=is_user_added,
                    preserve_user_flag=True
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
            
            time.sleep(5)  # throttle requests
        
        print()
        print("=" * 60)
        print("✅ Scraping Complete!")
        print("=" * 60)
        print()
        success_count = sum(1 for r in all_results if r.get("status") != "error")
        fail_count = len(all_results) - success_count
        print(f"✅ Successful: {success_count}")
        print(f"❌ Failed: {fail_count}")
        print(f"📊 Total: {len(all_results)}")
        
        return all_results
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_scraper_direct()

