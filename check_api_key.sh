#!/bin/bash
# Quick script to check OpenAI API key status

echo "=========================================="
echo "Checking OpenAI API Key Status"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    exit 1
fi

# Load API key
source .env
API_KEY=$OPENAI_API_KEY

if [ -z "$API_KEY" ]; then
    echo "❌ OPENAI_API_KEY not set in .env file"
    exit 1
fi

echo "✅ API key found: ${API_KEY:0:10}..."
echo ""

# Test API key
echo "Testing API key..."
python3 << EOF
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

try:
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': 'Say OK'}],
        max_tokens=5
    )
    print("✅ API key is WORKING!")
    print(f"   Response: {response.choices[0].message.content}")
    print("")
    print("✅ You can run the scraper now!")
except Exception as e:
    error_str = str(e)
    if 'quota' in error_str.lower() or '429' in error_str or 'insufficient_quota' in error_str:
        print("❌ API QUOTA EXCEEDED")
        print("")
        print("💡 Solutions:")
        print("   1. Get a new API key from: https://platform.openai.com/api-keys")
        print("   2. Update OPENAI_API_KEY in .env file")
        print("   3. Or add credits to your OpenAI account")
        print("")
        print("⚠️  Scraper will use fallback mode (less accurate)")
    else:
        print(f"❌ API Error: {error_str}")
EOF

echo ""
echo "=========================================="
echo "Check Status Endpoint:"
echo "curl http://localhost:8000/api/scraper-status"
echo "=========================================="

