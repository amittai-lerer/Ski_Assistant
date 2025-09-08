#!/usr/bin/env python3
"""
Quick test of your Geoapify API key without needing .env file
"""

import asyncio
import httpx

async def test_api_key():
    api_key = "b79d2568b0a242e9965b0397a101b855"

    print("🧪 TESTING YOUR GEOAPIFY API KEY DIRECTLY")
    print("=" * 50)
    print(f"API Key: {api_key}")
    print()

    # Test with different categories to find one that works
    categories_to_test = [
        "activity",
        "sport",
        "tourism",
        "entertainment"
    ]

    for category in categories_to_test:
        print(f"Testing category: '{category}'")

        try:
            async with httpx.AsyncClient() as client:
                r = await client.get("https://api.geoapify.com/v2/places",
                    params={
                        "categories": category,
                        "filter": "circle:6.86933,45.92375,50000",  # Chamonix area
                        "limit": 3,
                        "apiKey": api_key
                    }, timeout=10)

                if r.status_code == 200:
                    data = r.json()
                    features = data.get("features", [])
                    print(f"✅ SUCCESS! Found {len(features)} places in '{category}' category")

                    if features:
                        for i, feature in enumerate(features[:2], 1):
                            props = feature.get("properties", {})
                            name = props.get("name", "Unknown")
                            print(f"   {i}. {name}")

                    print("🎉 This category works! Update your geoapify_resorts.py file.")
                    print(f"   Change 'categories': 'sport.ski_resort' to 'categories': '{category}'")
                    return

                else:
                    print(f"❌ Status {r.status_code}: {r.text[:100]}...")

        except Exception as e:
            print(f"❌ Error: {e}")

        print()

    print("❌ None of the tested categories worked.")
    print("💡 Check Geoapify documentation for correct ski resort category.")

if __name__ == "__main__":
    asyncio.run(test_api_key())
