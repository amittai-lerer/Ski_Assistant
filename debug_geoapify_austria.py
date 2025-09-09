#!/usr/bin/env python3
"""
Debug script to test Geoapify API for Austria ski resorts
"""

import asyncio
import os
import httpx
from apis.geoapify_resorts import find_resorts_geoapify, _geocode

async def debug_austria_search():
    """Test different search approaches for Austria."""

    print("🔍 Debugging Geoapify Austria Search")
    print("=" * 50)

    # Test geocoding first
    print("\n1. Testing geocoding for 'austria' -> 'Innsbruck'")
    coords = await _geocode("Innsbruck")
    if coords:
        lat, lon, label = coords
        print(f"✅ Geocoded: {label} at ({lat}, {lon})")
    else:
        print("❌ Geocoding failed")
        return

    # Test current implementation
    print("\n2. Testing current find_resorts_geoapify implementation:")
    result = await find_resorts_geoapify("austria")
    print(f"Result keys: {result.keys()}")
    if "resorts" in result:
        print(f"Found {len(result['resorts'])} resorts:")
        for i, resort in enumerate(result['resorts'][:3], 1):
            print(f"  {i}. {resort.get('name', 'Unknown')} - {resort.get('address', 'No address')}")
    if "error" in result:
        print(f"❌ Error: {result['error']}")

    # Test direct API call with different parameters
    print("\n3. Testing direct API call with optimized parameters:")

    key = os.getenv("GEOAPIFY_API_KEY")
    if not key:
        print("❌ No GEOAPIFY_API_KEY found")
        return

    try:
        async with httpx.AsyncClient() as client:
            # Try with more specific ski resort category
            r = await client.get("https://api.geoapify.com/v2/places",
                params={
                    "categories": "sport.ski_resort",  # More specific category
                    "filter": f"circle:{lon},{lat},{50000}",  # 50km radius
                    "limit": 10,
                    "apiKey": key
                }, timeout=30)

            print(f"API Response Status: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                features = data.get("features", [])
                print(f"Found {len(features)} ski resort features")

                for i, f in enumerate(features[:5], 1):
                    props = f.get("properties", {})
                    name = props.get("name", "Unknown")
                    address = props.get("formatted", "No address")
                    print(f"  {i}. {name} - {address}")
            else:
                print(f"❌ API Error: {r.status_code} - {r.text}")

    except Exception as e:
        print(f"❌ API call failed: {e}")

    # Test with broader search
    print("\n4. Testing with broader search parameters:")

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("https://api.geoapify.com/v2/places",
                params={
                    "categories": "sport",  # Broader sport category
                    "text": "ski resort OR alpine OR snow",  # More specific text search
                    "filter": f"circle:{lon},{lat},{100000}",  # 100km radius
                    "limit": 10,
                    "apiKey": key
                }, timeout=30)

            print(f"Broad search response: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                features = data.get("features", [])
                print(f"Found {len(features)} sport features")

                ski_count = 0
                for f in features:
                    props = f.get("properties", {})
                    name = props.get("name", "Unknown")
                    text_to_check = (name + " " + str(props.get("formatted", ""))).lower()
                    if any(keyword in text_to_check for keyword in ["ski", "alpine", "snow", "resort"]):
                        ski_count += 1
                        print(f"  ✅ {name} - {props.get('formatted', 'No address')}")
                        if ski_count >= 5:
                            break

                print(f"Total ski-related results: {ski_count}")

    except Exception as e:
        print(f"❌ Broad search failed: {e}")

if __name__ == "__main__":
    asyncio.run(debug_austria_search())
