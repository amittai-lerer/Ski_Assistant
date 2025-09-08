#!/usr/bin/env python3
"""
Quick test to verify Geoapify API key is working with real data
"""

import asyncio
import os
from apis.geoapify_resorts import find_resorts_geoapify

async def test_real_data():
    print("🎿 TESTING SKI ASSISTANT WITH REAL GEOAPIFY DATA")
    print("=" * 55)

    # Check API key
    api_key = os.getenv("GEOAPIFY_API_KEY")
    if not api_key or api_key == "your_geoapify_api_key_here":
        print("❌ GEOAPIFY_API_KEY not set properly!")
        print("💡 Please update your .env file with a real Geoapify API key")
        return

    print(f"✅ API Key configured: {api_key[:10]}...")
    print()

    # Test popular ski destinations
    locations = [
        ("Chamonix", "France"),
        ("Zermatt", "Switzerland"),
        ("Lake Tahoe", "USA"),
        ("Banff", "Canada"),
        ("Queenstown", "New Zealand")
    ]

    for city, country in locations:
        print(f"🏔️  Searching ski resorts near {city}, {country}")
        print("-" * 40)

        try:
            result = await find_resorts_geoapify(city=city, radius_km=50, limit=5)

            if "error" in result:
                print(f"❌ API Error: {result['error']}")
                continue

            if "resorts" in result and result["resorts"]:
                resorts = result["resorts"]
                print(f"✅ Found {len(resorts)} ski resorts near {result.get('area', city)}")
                print()

                for i, resort in enumerate(resorts[:3], 1):
                    name = resort.get("name", "Unknown Resort")
                    address = resort.get("address", "")
                    website = resort.get("datasource", "")

                    print(f"🏂 {i}. {name}")
                    if address:
                        print(f"   📍 {address}")
                    if website:
                        print(f"   🌐 {website}")
                    print()

            else:
                print("⚠️  No ski resorts found in this area")
                print("💡 This could be normal for some locations")

        except Exception as e:
            print(f"❌ Exception: {e}")

        print()

    print("🎉 TEST COMPLETE!")
    print("If you see real ski resort data above, your API key is working!")
    print("You can now run: python -m app.cli")

if __name__ == "__main__":
    asyncio.run(test_real_data())
