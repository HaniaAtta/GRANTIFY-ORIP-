#!/usr/bin/env python3
"""
Export all URLs from categories.json to NeonDB.
This script will add all funders from categories.json to the database.
"""

import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.db_helper import add_or_update_grant_site, get_db, GrantSite
from scrapers.bs_scrapper.scraper import scrape_page
from sqlalchemy.orm import Session

def load_categories_json():
    """Load categories.json file."""
    categories_path = os.path.join(
        os.path.dirname(__file__), 
        "app", 
        "config", 
        "categories.json"
    )
    
    if not os.path.exists(categories_path):
        print(f"❌ Error: {categories_path} not found!")
        sys.exit(1)
    
    with open(categories_path, "r", encoding="utf-8") as f:
        return json.load(f)

def export_to_database(dry_run=False, scrape=False):
    """
    Export all funders from categories.json to NeonDB.
    
    Args:
        dry_run: If True, only print what would be done without actually doing it
        scrape: If True, also scrape each URL to get current status
    """
    print("=" * 60)
    print("Exporting categories.json to NeonDB")
    print("=" * 60)
    
    # Load categories.json
    print("\n📂 Loading categories.json...")
    funders = load_categories_json()
    print(f"✅ Loaded {len(funders)} funders from categories.json")
    
    if dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made to database")
    
    # Get database session
    db = next(get_db())
    
    added_count = 0
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    print(f"\n📊 Processing {len(funders)} funders...")
    print("-" * 60)
    
    for i, funder in enumerate(funders, 1):
        url = funder.get("url", "").strip()
        name = funder.get("name", "Unknown")
        country = funder.get("country", "Unknown")
        categories = funder.get("categories", [])
        thematic_areas = funder.get("thematic_area", [])
        
        if not url:
            print(f"⚠️  [{i}/{len(funders)}] Skipping {name}: No URL provided")
            skipped_count += 1
            continue
        
        print(f"[{i}/{len(funders)}] Processing: {name}")
        print(f"   URL: {url}")
        print(f"   Categories: {', '.join(categories[:3])}...")
        
        # Check if already exists
        existing = db.query(GrantSite).filter(GrantSite.url == url).first()
        
        if existing:
            print(f"   ℹ️  Already exists in database (ID: {existing.id})")
            if not dry_run:
                # Update with latest info from JSON
                existing.categories = categories or existing.categories
                existing.country = country or existing.country
                existing.thematic_areas = thematic_areas or existing.thematic_areas
                db.commit()
                updated_count += 1
            else:
                updated_count += 1
        else:
            if dry_run:
                print(f"   ➕ Would add to database")
                added_count += 1
            else:
                try:
                    # Add to database
                    if scrape:
                        print(f"   🔍 Scraping {url}...")
                        try:
                            result = scrape_page(url)
                            status = result.get("status", "unknown")
                            landing_page = result.get("landing_page", url)
                            regions = result.get("regions", [])
                            applicable_to_pakistan = result.get("applicable_to_pakistan", False)
                            open_date = result.get("open_date")
                            close_date = result.get("close_date")
                            eligibility = result.get("eligibility", "")
                            
                            # Convert string dates to datetime
                            if isinstance(open_date, str) and open_date not in ("null", "", "None"):
                                try:
                                    from datetime import datetime
                                    open_date = datetime.strptime(open_date, "%Y-%m-%d")
                                except:
                                    open_date = None
                            
                            if isinstance(close_date, str) and close_date not in ("null", "", "None"):
                                try:
                                    from datetime import datetime
                                    close_date = datetime.strptime(close_date, "%Y-%m-%d")
                                except:
                                    close_date = None
                            
                            print(f"   ✅ Scraped: Status={status}")
                        except Exception as e:
                            print(f"   ⚠️  Scraping failed: {str(e)}")
                            status = "unknown"
                            landing_page = url
                            regions = []
                            applicable_to_pakistan = False
                            open_date = None
                            close_date = None
                            eligibility = ""
                    else:
                        # Just add without scraping
                        status = "unknown"
                        landing_page = url
                        regions = []
                        applicable_to_pakistan = False
                        open_date = None
                        close_date = None
                        eligibility = ""
                    
                    add_or_update_grant_site(
                        url=url,
                        status=status,
                        landing_page=landing_page,
                        categories=categories,
                        country=country,
                        regions=regions,
                        applicable_to_pakistan=applicable_to_pakistan,
                        open_date=open_date,
                        close_date=close_date,
                        eligibility=eligibility,
                        thematic_areas=thematic_areas,
                        is_user_added=False,  # Auto-scraped from JSON
                        preserve_user_flag=False
                    )
                    print(f"   ✅ Added to database")
                    added_count += 1
                except Exception as e:
                    print(f"   ❌ Error adding to database: {str(e)}")
                    error_count += 1
        
        print()  # Empty line for readability
    
    # Summary
    print("=" * 60)
    print("Export Summary")
    print("=" * 60)
    print(f"✅ Added: {added_count}")
    print(f"🔄 Updated: {updated_count}")
    print(f"⏭️  Skipped: {skipped_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📊 Total processed: {len(funders)}")
    
    if dry_run:
        print("\n💡 This was a dry run. Run without --dry-run to actually export.")
    else:
        print("\n✅ Export completed!")
        print("\nNext steps:")
        print("  1. Verify data: Check your NeonDB dashboard")
        print("  2. Run scraper: python -c 'from tasks.run_scrapers import run_all_scrapers; run_all_scrapers.delay()'")
        print("  3. Or use API: POST /api/scrape_all")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Export categories.json to NeonDB")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode (no database changes)")
    parser.add_argument("--scrape", action="store_true", help="Also scrape each URL to get current status")
    
    args = parser.parse_args()
    
    try:
        export_to_database(dry_run=args.dry_run, scrape=args.scrape)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

