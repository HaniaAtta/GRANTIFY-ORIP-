#!/usr/bin/env python3
"""
Show scraper results - which websites were scraped and their results
"""

import sys
from datetime import datetime, timedelta
from models.db_helper import get_grant_sites

def show_results():
    print("=" * 80)
    print("📊 Scraper Results Summary")
    print("=" * 80)
    print()
    
    try:
        grants = get_grant_sites()
        total = len(grants)
        
        # Get recently updated (last hour)
        recent = [g for g in grants if g.last_updated and g.last_updated > datetime.utcnow() - timedelta(hours=1)]
        updated_count = len(recent)
        
        # Count by status
        open_count = sum(1 for g in grants if g.status == "open")
        closed_count = sum(1 for g in grants if g.status == "closed")
        unknown_count = sum(1 for g in grants if g.status == "unknown")
        error_count = sum(1 for g in grants if g.status == "error")
        
        print(f"📊 Total Grants in Database: {total}")
        print(f"🔄 Updated in Last Hour: {updated_count}")
        print()
        print("Status Breakdown:")
        print(f"  ✅ Open: {open_count}")
        print(f"  🔴 Closed: {closed_count}")
        print(f"  ⚠️  Unknown: {unknown_count}")
        print(f"  ❌ Error: {error_count}")
        print()
        
        if recent:
            print("=" * 80)
            print(f"📝 Recently Scraped Websites (Last Hour): {len(recent)}")
            print("=" * 80)
            print()
            
            for i, g in enumerate(sorted(recent, key=lambda x: x.last_updated, reverse=True), 1):
                url_short = (g.url[:65] + "...") if len(g.url) > 65 else g.url
                time_ago = (datetime.utcnow() - g.last_updated).total_seconds() / 60
                
                # Status icon
                if g.status == "open":
                    status_icon = "✅"
                elif g.status == "closed":
                    status_icon = "🔴"
                elif g.status == "error":
                    status_icon = "❌"
                else:
                    status_icon = "⚠️"
                
                print(f"{i}. {status_icon} [{time_ago:.1f} minutes ago]")
                print(f"   URL: {url_short}")
                print(f"   Status: {g.status.upper()}")
                
                if g.categories:
                    print(f"   Categories: {', '.join(g.categories[:5])}")
                
                if g.open_date or g.close_date:
                    print(f"   Dates: Open: {g.open_date or 'N/A'} | Close: {g.close_date or 'N/A'}")
                
                if g.regions:
                    print(f"   Regions: {', '.join(g.regions[:3])}")
                
                if g.applicable_to_pakistan:
                    print(f"   🇵🇰 Applicable to Pakistan: Yes")
                
                print()
        else:
            print("⏳ No recent updates in the last hour.")
            print("   The scraper might still be running or hasn't started yet.")
            print()
            print("Check logs: docker-compose logs -f fastapi")
        
        print("=" * 80)
        print("💡 Tip: Run this script periodically to see latest results")
        print("   Or use: watch -n 10 python3 show_scraper_results.py")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    show_results()

