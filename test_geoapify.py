#!/usr/bin/env python3
"""
Test Geoapify ski resort search implementation
"""

import asyncio
import os
from apis.geoapify_resorts import find_resorts_geoapify

async def test_geoapify():
    print("🧪 TESTING GEOAPIFY SKI RESORT SEARCH")
    print("=" * 50)

    # Check if API key is set
    api_key = os.getenv("GEOAPIFY_API_KEY")
    if not api_key or api_key == "your_geoapify_api_key_here":
        print("❌ GEOAPIFY_API_KEY not set or using placeholder")
        print()
        print("📋 TO GET A GEOAPIFY API KEY:")
        print("1. Go to: https://www.geoapify.com/")
        print("2. Sign up for a free account")
        print("3. Go to Projects/My Projects")
        print("4. Create a new project or use existing")
        print("5. Copy the API key")
        print("6. Add to your .env file:")
        print("   GEOAPIFY_API_KEY=your_actual_api_key_here")
        print()
        print("💡 Geoapify offers 3000 free requests per day!")
        return

    print(f"✅ API Key configured: {api_key[:10]}...")
    print()

    # Test different locations
    test_locations = [
        ("Chamonix", None, None),
        ("Lake Tahoe", None, None),
        ("Zermatt", None, None),
    ]

    for location, lat, lon in test_locations:
        print(f"🏔️  Testing: {location}")
        print("-" * 30)

        try:
            if lat and lon:
                result = await find_resorts_geoapify(city=location, lat=lat, lon=lon, radius_km=50, limit=5)
            else:
                result = await find_resorts_geoapify(city=location, radius_km=50, limit=5)

            # Handle different result types
            if "error" in result:
                print(f"❌ Error: {result['error']}")
                if "missing_geoapify_key" in result["error"]:
                    print("💡 Solution: Set GEOAPIFY_API_KEY in .env file")
                elif "could_not_geocode" in result["error"]:
                    print(f"💡 Could not find coordinates for: {result.get('city', location)}")
                    print("💡 Try a different city name")
                elif "geoapify_unauthorized" in result["error"]:
                    print("💡 API key is invalid or expired")
                    print("💡 Get a new key from https://www.geoapify.com/")
                else:
                    print(f"💡 Details: {result}")

            elif "resorts" in result:
                resorts = result["resorts"]
                area = result.get("area", location)

                print(f"✅ Found {len(resorts)} ski resorts near {area}")
                print()

                if resorts:
                    for i, resort in enumerate(resorts[:3], 1):
                        name = resort.get("name", "Unknown")
                        address = resort.get("address", "No address")
                        lat = resort.get("lat")
                        lon = resort.get("lon")
                        website = resort.get("datasource")

                        print(f"🏂 {i}. {name}")
                        if address and address != "No address":
                            print(f"   📍 {address}")
                        if lat and lon:
                            print(f"   📌 Lat: {lat:.4f}, Lng: {lon:.4f}")
                        if website:
                            print(f"   🌐 {website}")
                        print()

                else:
                    print("⚠️  No ski resorts found in this area")
                    print("💡 Try a larger city or increase the search radius")

            else:
                print(f"❌ Unexpected result format: {result}")

        except Exception as e:
            print(f"❌ Exception: {e}")

        print()

if __name__ == "__main__":
    asyncio.run(test_geoapify())
