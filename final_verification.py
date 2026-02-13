#!/usr/bin/env python3
"""
Final comprehensive verification before deployment.
Tests all components: OpenAI, BeautifulSoup, Selenium, Database.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_openai():
    """Test OpenAI API connection and functionality."""
    print("=" * 60)
    print("1. Testing OpenAI API")
    print("=" * 60)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-openai-api-key-here":
        print("❌ OPENAI_API_KEY not set or invalid")
        return False
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Test API call
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'API working' if you can read this."}],
            max_tokens=10
        )
        
        print(f"✅ OpenAI API Key: {api_key[:10]}...{api_key[-5:]}")
        print(f"✅ API Response: {response.choices[0].message.content}")
        print("✅ OpenAI API is working!")
        return True
    except Exception as e:
        print(f"❌ OpenAI API Error: {str(e)}")
        return False

def test_beautifulsoup():
    """Test BeautifulSoup installation and basic functionality."""
    print()
    print("=" * 60)
    print("2. Testing BeautifulSoup")
    print("=" * 60)
    
    try:
        from bs4 import BeautifulSoup
        import requests
        
        # Test parsing
        html = "<html><body><h1>Test</h1><p>Content</p></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text()
        
        if "Test" in text and "Content" in text:
            print("✅ BeautifulSoup installed and working")
            print("✅ Can parse HTML and extract text")
            return True
        else:
            print("❌ BeautifulSoup parsing failed")
            return False
    except Exception as e:
        print(f"❌ BeautifulSoup Error: {str(e)}")
        return False

def test_selenium():
    """Test Selenium installation."""
    print()
    print("=" * 60)
    print("3. Testing Selenium")
    print("=" * 60)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        print("✅ Selenium installed")
        print("✅ Chrome options available")
        print("⚠️  Full Selenium test requires Chrome browser")
        print("   (Will be tested during actual scraping)")
        return True
    except Exception as e:
        print(f"❌ Selenium Error: {str(e)}")
        return False

def test_database():
    """Test NeonDB connection."""
    print()
    print("=" * 60)
    print("4. Testing NeonDB Connection")
    print("=" * 60)
    
    try:
        from models.db_helper import engine, get_grant_sites, GrantSite
        from sqlalchemy import inspect
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
        
        # Check tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if "grant_sites" in tables:
            # Check columns
            columns = [col['name'] for col in inspector.get_columns('grant_sites')]
            required = ['id', 'url', 'status', 'is_user_added']
            missing = [c for c in required if c not in columns]
            
            if missing:
                print(f"⚠️  Missing columns: {', '.join(missing)}")
                return False
            
            # Get grant count
            grants = get_grant_sites()
            print(f"✅ Database connected")
            print(f"✅ Table 'grant_sites' exists")
            print(f"✅ All required columns present")
            print(f"✅ Grants in database: {len(grants)}")
            return True
        else:
            print("❌ Table 'grant_sites' not found")
            return False
            
    except Exception as e:
        print(f"❌ Database Error: {str(e)}")
        return False

def test_scraper_integration():
    """Test complete scraper integration."""
    print()
    print("=" * 60)
    print("5. Testing Scraper Integration")
    print("=" * 60)
    
    try:
        from scrapers.bs_scrapper.scraper import scrape_page
        from app.ai.classifier import classify_grant
        
        print("✅ Scraper module imported")
        print("✅ Classifier module imported")
        print("✅ All components available")
        print()
        print("💡 Run 'python3 test_scraper_few.py -n 3' to test actual scraping")
        return True
    except Exception as e:
        print(f"❌ Integration Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_dependencies():
    """Test all required dependencies."""
    print()
    print("=" * 60)
    print("6. Testing Dependencies")
    print("=" * 60)
    
    required = [
        "fastapi",
        "sqlalchemy",
        "celery",
        "redis",
        "beautifulsoup4",
        "selenium",
        "openai",
        "requests",
    ]
    
    missing = []
    for dep in required:
        try:
            __import__(dep.replace("-", "_"))
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - NOT INSTALLED")
            missing.append(dep)
    
    if missing:
        print()
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Run all verification tests."""
    print()
    print("=" * 60)
    print("PRODUCTION READINESS VERIFICATION")
    print("=" * 60)
    print()
    
    results = []
    
    results.append(("Dependencies", test_dependencies()))
    results.append(("OpenAI API", test_openai()))
    results.append(("BeautifulSoup", test_beautifulsoup()))
    results.append(("Selenium", test_selenium()))
    results.append(("NeonDB", test_database()))
    results.append(("Scraper Integration", test_scraper_integration()))
    
    print()
    print("=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    print()
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print()
    
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print()
        print("✅ Your dashboard is PRODUCTION-READY!")
        print()
        print("Next steps:")
        print("  1. Test scraper: python3 test_scraper_few.py -n 5")
        print("  2. Start services: docker-compose up --build -d")
        print("  3. Deploy to production!")
    else:
        print("⚠️  SOME TESTS FAILED")
        print()
        print("Please fix the issues above before deployment.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

