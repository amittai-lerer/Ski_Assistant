#!/usr/bin/env python3
"""
Test script to verify Austria ski resort search is working after fixes
"""

import asyncio
import os
from apis.geoapify_resorts import find_resorts_geoapify

async def test_austria_ski_search():
    """Test that Austria ski resorts are now found properly."""

    print("🇦🇹 Testing Austria Ski Resort Search")
    print("=" * 50)

    # Test with different Austrian locations
    test_locations = ["austria", "Austria", "Innsbruck", "Salzburg", "Kitzbühel"]

    for location in test_locations:
        print(f"\n🔍 Searching for ski resorts near: {location}")

        try:
            result = await find_resorts_geoapify(location)

            if "error" in result:
                if result["error"] == "missing_geoapify_key":
                    print("❌ Missing GEOAPIFY_API_KEY in environment variables")
                    print("   Please add your Geoapify API key to the .env file")
                    break
                else:
                    print(f"❌ Error: {result['error']}")
                    continue

            resorts = result.get("resorts", [])
            print(f"✅ Found {len(resorts)} ski resorts/activities")

            if resorts:
                print("Top results:")
                for i, resort in enumerate(resorts[:3], 1):
                    name = resort.get("name", "Unknown")
                    address = resort.get("address", "No address")
                    print(f"  {i}. {name}")
                    print(f"     📍 {address}")
            else:
                print("⚠️  No ski-specific results found")

        except Exception as e:
            print(f"❌ Test failed: {e}")

    print("\n" + "=" * 50)
    print("To fix the Austria ski search issue:")
    print("1. Add your GEOAPIFY_API_KEY to the .env file")
    print("2. Make sure the key is valid and has proper permissions")
    print("3. The improved search should now find Austrian ski resorts!")

if __name__ == "__main__":
    asyncio.run(test_austria_ski_search())
