#!/usr/bin/env python3
"""
Test scraper on just a few websites to verify:
1. Scraper logic is working
2. OpenAI API is being used
3. Data extraction is accurate
4. Updates are saved to NeonDB
"""

import os
import sys
from dotenv import load_dotenv
from models.db_helper import get_grant_sites, add_or_update_grant_site, SessionLocal, GrantSite
from scrapers.bs_scrapper.scraper import scrape_page
from datetime import datetime

load_dotenv()

def test_scraper_on_few(num_websites=5):
    """
    Test scraper on first N websites from database.
    
    Args:
        num_websites: Number of websites to test (default: 5)
    """
    print("=" * 60)
    print(f"Testing Scraper on {num_websites} Websites")
    print("=" * 60)
    print()
    
    # Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-openai-api-key-here":
        print("❌ ERROR: OPENAI_API_KEY not set or invalid!")
        print("   Please set OPENAI_API_KEY in your .env file")
        return False
    else:
        print(f"✅ OpenAI API Key found: {api_key[:10]}...{api_key[-5:]}")
    
    print()
    
    # Get grants from NeonDB
    print("📊 Loading grants from NeonDB...")
    all_grants = get_grant_sites()
    
    if not all_grants:
        print("❌ No grants found in database!")
        print("   Run: python3 export_json_to_db.py first")
        return False
    
    print(f"✅ Found {len(all_grants)} grants in database")
    print()
    
    # Select first N grants for testing
    test_grants = all_grants[:num_websites]
    
    print(f"🔍 Testing scraper on {len(test_grants)} websites:")
    for i, grant in enumerate(test_grants, 1):
        print(f"   {i}. {grant.url} (ID: {grant.id})")
    print()
    print("-" * 60)
    print()
    
    results = []
    
    for i, grant in enumerate(test_grants, 1):
        url = grant.url
        grant_id = grant.id
        
        print(f"[{i}/{len(test_grants)}] Testing: {url}")
        print(f"   Grant ID: {grant_id}")
        print(f"   Current Status: {grant.status}")
        print(f"   Current Categories: {grant.categories}")
        print()
        
        try:
            # Scrape the URL
            print("   🔍 Scraping...")
            result = scrape_page(url)
            
            print(f"   ✅ Scraping completed!")
            print(f"   📊 Results:")
            print(f"      - Status: {result.get('status', 'N/A')}")
            print(f"      - Landing Page: {result.get('landing_page', 'N/A')}")
            print(f"      - Categories: {result.get('categories', [])}")
            print(f"      - Regions: {result.get('regions', [])}")
            print(f"      - Open Date: {result.get('open_date', 'N/A')}")
            print(f"      - Close Date: {result.get('close_date', 'N/A')}")
            print(f"      - Eligibility: {result.get('eligibility', 'N/A')[:50]}...")
            print(f"      - Applicable to Pakistan: {result.get('applicable_to_pakistan', False)}")
            print()
            
            # Check if data was actually scraped (not hardcoded)
            if result.get('status') == 'unknown' and not result.get('categories'):
                print("   ⚠️  WARNING: Scraper returned minimal data")
                print("      This might indicate the scraper isn't working properly")
            else:
                print("   ✅ Scraper returned detailed data")
            
            # Update in database
            print("   💾 Updating database...")
            updated_grant = add_or_update_grant_site(
                url=result.get("base_url") or url,
                status=result.get("status", "unknown"),
                landing_page=result.get("landing_page", url),
                categories=result.get("categories", []) or grant.categories or [],
                regions=result.get("regions", []) or grant.regions or [],
                applicable_to_pakistan=result.get("applicable_to_pakistan", False),
                open_date=result.get("open_date"),
                close_date=result.get("close_date"),
                eligibility=result.get("eligibility", "") or grant.eligibility or "",
                thematic_areas=result.get("thematic_areas", []) or grant.thematic_areas or [],
                is_user_added=grant.is_user_added,
                preserve_user_flag=True
            )
            
            print(f"   ✅ Database updated!")
            print(f"      - New Status: {updated_grant.status}")
            print(f"      - Last Updated: {updated_grant.last_updated}")
            print()
            
            results.append({
                "id": grant_id,
                "url": url,
                "status": "success",
                "old_status": grant.status,
                "new_status": result.get("status"),
                "has_data": bool(result.get("categories") or result.get("regions"))
            })
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            print()
            results.append({
                "id": grant_id,
                "url": url,
                "status": "error",
                "error": str(e)
            })
        
        print("-" * 60)
        print()
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print()
    
    success = sum(1 for r in results if r["status"] == "success")
    errors = sum(1 for r in results if r["status"] == "error")
    has_data = sum(1 for r in results if r.get("has_data", False))
    
    print(f"✅ Successful: {success}/{len(results)}")
    print(f"❌ Errors: {errors}/{len(results)}")
    print(f"📊 With Data: {has_data}/{len(results)}")
    print()
    
    if has_data < success:
        print("⚠️  WARNING: Some scrapes returned minimal data")
        print("   This might indicate:")
        print("   - OpenAI API not working properly")
        print("   - Scraper not extracting data correctly")
        print("   - Website structure changed")
    else:
        print("✅ All successful scrapes returned data!")
    
    print()
    
    # Show detailed results
    print("Detailed Results:")
    for r in results:
        if r["status"] == "success":
            status_change = f"{r['old_status']} → {r['new_status']}"
            data_status = "✅ Has data" if r.get("has_data") else "⚠️  No data"
            print(f"   ✅ {r['url'][:50]}... | {status_change} | {data_status}")
        else:
            print(f"   ❌ {r['url'][:50]}... | Error: {r.get('error', 'Unknown')}")
    
    print()
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test scraper on a few websites")
    parser.add_argument("-n", "--num", type=int, default=5, help="Number of websites to test (default: 5)")
    
    args = parser.parse_args()
    
    try:
        test_scraper_on_few(num_websites=args.num)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

