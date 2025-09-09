#!/usr/bin/env python3
"""
Test script for SkiAPI integration.

This script tests the SkiAPI integration to ensure it works correctly
with the RapidAPI service and can fetch ski resort information.
"""

import asyncio
import os
from apis.skiapi_resorts import search_resorts, get_ski_resort_details

async def test_skiapi_basic():
    """Test basic SkiAPI functionality."""
    print("🧪 Testing SkiAPI Integration")
    print("=" * 50)

    # Check if RAPIDAPI_KEY is available
    rapidapi_key = os.getenv("RAPIDAPI_KEY", "")
    if not rapidapi_key:
        print("❌ RAPIDAPI_KEY not found in environment variables")
        print("Please add your RapidAPI key to the .env file:")
        print("RAPIDAPI_KEY=your_rapidapi_key_here")
        return

    print("✅ RAPIDAPI_KEY found")

    try:
        # Test 1: Search for resorts
        print("\n🔍 Test 1: Searching for ski resorts...")
        search_result = await search_resorts(query="Lake Tahoe", per_page=5)

        if "error" in search_result:
            print(f"❌ Search failed: {search_result['error']}")
            if search_result['error'] == "missing_rapidapi_key":
                print("Please check your RAPIDAPI_KEY in the .env file")
                return
            elif "403" in str(search_result.get('error', '')):
                print("\n🚨 RAPIDAPI SUBSCRIPTION REQUIRED")
                print("You need to subscribe to SkiAPI on RapidAPI:")
                print("1. Go to: https://rapidapi.com/skapi/api/ski-api")
                print("2. Click 'Subscribe to Test' or choose a paid plan")
                print("3. Your RAPIDAPI_KEY will then work with SkiAPI")
                print("\nNote: SkiAPI offers both free and paid plans.")
                print("The free plan usually has limited requests per month.")
                return
            elif "401" in str(search_result.get('error', '')):
                print("❌ Invalid RAPIDAPI_KEY. Please check your key in the .env file")
                return
        else:
            resorts = search_result.get("resorts", [])
            print(f"✅ Found {len(resorts)} resorts near Lake Tahoe:")
            for i, resort in enumerate(resorts[:3], 1):  # Show first 3
                print(f"  {i}. {resort.get('name', 'Unknown')} - {resort.get('country', '')}")

        # Test 2: Get specific resort details
        if resorts:
            resort = resorts[0]
            resort_name = resort.get("name", "")
            print(f"\n🏔️ Test 2: Getting details for '{resort_name}'...")

            details_result = await get_ski_resort_details(
                resort_name=resort_name,
                country="US",
                include_snow_report=False
            )

            if "error" in details_result:
                print(f"❌ Details fetch failed: {details_result['error']}")
            else:
                print("✅ Resort details retrieved successfully:")
                print(f"  Name: {details_result.get('resort_name', 'Unknown')}")
                print(f"  Country: {details_result.get('country', 'Unknown')}")
                if "location" in details_result:
                    loc = details_result["location"]
                    print(f"  Location: {loc.get('latitude', 'N/A')}, {loc.get('longitude', 'N/A')}")

        # Test 3: Test with a well-known resort
        print("\n🏂 Test 3: Testing with 'Vail'...")
        vail_result = await get_ski_resort_details(
            resort_name="Vail",
            country="US",
            include_snow_report=False
        )

        if "error" in vail_result:
            print(f"❌ Vail details failed: {vail_result['error']}")
        else:
            print("✅ Vail details retrieved successfully:")
            print(f"  Name: {vail_result.get('resort_name', 'Unknown')}")
            print(f"  Country: {vail_result.get('country', 'Unknown')}")

        print("\n🎉 SkiAPI integration test completed!")

    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_skiapi_basic())
