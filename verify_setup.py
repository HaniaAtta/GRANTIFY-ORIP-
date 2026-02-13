#!/usr/bin/env python3
"""
Quick verification script to check if the setup is correct.
Run this after setting up your environment variables.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def check_env_vars():
    """Check if required environment variables are set."""
    print("🔍 Checking environment variables...")
    
    required_vars = ["DATABASE_URL", "OPENAI_API_KEY", "REDIS_URL"]
    missing = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
            print(f"  ❌ {var}: Not set")
        else:
            # Mask sensitive values
            if "password" in var.lower() or "key" in var.lower():
                masked = value[:10] + "..." + value[-5:] if len(value) > 15 else "***"
                print(f"  ✅ {var}: {masked}")
            else:
                print(f"  ✅ {var}: {value[:50]}...")
    
    if missing:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing)}")
        print("   Please set them in your .env file")
        return False
    return True

def check_database():
    """Check database connection."""
    print("\n🔍 Checking database connection...")
    try:
        from models.db_helper import engine, GrantSite
        from sqlalchemy import inspect
        
        # Test connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        
        # Check if table exists and has required columns
        inspector = inspect(engine)
        if "grant_sites" in inspector.get_table_names():
            columns = [col["name"] for col in inspector.get_columns("grant_sites")]
            required_columns = ["id", "url", "status", "is_user_added"]
            
            missing_cols = [col for col in required_columns if col not in columns]
            if missing_cols:
                print(f"  ⚠️  Missing columns: {', '.join(missing_cols)}")
                print("   Run: python -c 'from models.init_db import create_tables; create_tables()'")
                return False
            else:
                print("  ✅ Database connected and tables are correct")
                return True
        else:
            print("  ⚠️  Table 'grant_sites' not found")
            print("   Run: python -c 'from models.init_db import create_tables; create_tables()'")
            return False
            
    except Exception as e:
        print(f"  ❌ Database connection failed: {str(e)}")
        return False

def check_redis():
    """Check Redis connection."""
    print("\n🔍 Checking Redis connection...")
    try:
        import redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        client = redis.from_url(redis_url)
        client.ping()
        print("  ✅ Redis connected")
        return True
    except Exception as e:
        print(f"  ⚠️  Redis connection failed: {str(e)}")
        print("   Make sure Redis is running: redis-server")
        return False

def check_openai():
    """Check OpenAI API key."""
    print("\n🔍 Checking OpenAI API key...")
    try:
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("  ❌ OPENAI_API_KEY not set")
            return False
        
        client = OpenAI(api_key=api_key)
        # Try a simple API call
        client.models.list()
        print("  ✅ OpenAI API key is valid")
        return True
    except Exception as e:
        print(f"  ⚠️  OpenAI API check failed: {str(e)}")
        return False

def check_imports():
    """Check if all required modules can be imported."""
    print("\n🔍 Checking Python imports...")
    modules = [
        "fastapi",
        "sqlalchemy",
        "celery",
        "redis",
        "beautifulsoup4",
        "selenium",
        "openai",
    ]
    
    failed = []
    for module in modules:
        try:
            __import__(module.replace("-", "_"))
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module}: Not installed")
            failed.append(module)
    
    if failed:
        print(f"\n⚠️  Missing packages: {', '.join(failed)}")
        print("   Run: pip install -r requirements.txt")
        return False
    return True

def main():
    print("=" * 60)
    print("Grant Dashboard Setup Verification")
    print("=" * 60)
    
    results = []
    results.append(("Environment Variables", check_env_vars()))
    results.append(("Python Imports", check_imports()))
    results.append(("Database", check_database()))
    results.append(("Redis", check_redis()))
    results.append(("OpenAI", check_openai()))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All checks passed! Your setup is ready.")
        print("\nNext steps:")
        print("  1. Start the app: uvicorn app.main:app --reload")
        print("  2. Or use Docker: docker-compose up")
        print("  3. Access dashboard: http://localhost:8000")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()

