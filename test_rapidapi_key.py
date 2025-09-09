#!/usr/bin/env python3
"""
Quick test for RapidAPI key setup
"""

import os
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
RAPIDAPI_HOST = "ski-resorts-and-conditions.p.rapidapi.com"

def test_rapidapi_key():
    """Test the RapidAPI key with a simple request."""
    print("🔑 Testing RapidAPI Key Setup")
    print("=" * 40)

    if not RAPIDAPI_KEY or RAPIDAPI_KEY == "your_rapidapi_key_here":
        print("❌ RAPIDAPI_KEY not set!")
        print()
        print("📝 Please:")
        print("1. Go to: https://rapidapi.com/skapi/api/ski-resorts-and-conditions")
        print("2. Subscribe to a plan (free or paid)")
        print("3. Copy your API key")
        print("4. Add it to your .env file:")
        print("   RAPIDAPI_KEY=your_actual_api_key_here")
        return False

    print(f"✅ RAPIDAPI_KEY found: {RAPIDAPI_KEY[:8]}...")
    print("🔍 Testing API connection...")

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST,
        "Content-Type": "application/json"
    }

    try:
        response = httpx.get(
            "https://ski-resorts-and-conditions.p.rapidapi.com/v1/resort",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            total = data.get("total", 0)
            print(f"✅ API working! Found {total} ski resorts in database")
            return True
        elif response.status_code == 403:
            print("❌ Subscription required!")
            print("🚨 You need to subscribe to the API on RapidAPI")
            print("   Go to: https://rapidapi.com/skapi/api/ski-resorts-and-conditions")
            return False
        elif response.status_code == 401:
            print("❌ Invalid API key!")
            print("📝 Check your RAPIDAPI_KEY in the .env file")
            return False
        else:
            print(f"❌ API error: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    test_rapidapi_key()
