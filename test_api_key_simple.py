#!/usr/bin/env python3
"""Simple script to test OpenAI API key"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from openai import OpenAI

# Load .env from current directory
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    print("❌ API key not found in .env")
    sys.exit(1)

print(f"✅ API key loaded: {api_key[:10]}...")
print("")

try:
    client = OpenAI(api_key=api_key)
    print("Testing API key...")
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': 'Say OK'}],
        max_tokens=5
    )
    print(f"✅ API key is WORKING!")
    print(f"   Response: {response.choices[0].message.content}")
    print("")
    print("✅ You can now run the scraper!")
except Exception as e:
    error_str = str(e)
    if 'quota' in error_str.lower() or '429' in error_str or 'insufficient_quota' in error_str:
        print("❌ API QUOTA EXCEEDED")
        print("")
        print("The API key has no credits/quota available.")
        print("")
        print("💡 Solutions:")
        print("  1. Get a new API key with credits from: https://platform.openai.com/api-keys")
        print("  2. Or add credits to your OpenAI account: https://platform.openai.com/account/billing")
        print("")
        print("⚠️  Note: Scraper will still work in fallback mode (less accurate)")
    else:
        print(f"❌ API Error: {error_str}")

