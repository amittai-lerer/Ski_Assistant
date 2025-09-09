#!/usr/bin/env python3
"""
Comprehensive API Testing Script for SkiTrip Assistant.

Tests all three APIs:
1. Geoapify (resort search)
2. Open-Meteo (weather)
3. SkiAPI (detailed resort info)

Provides clear setup instructions and detailed test results.
"""

import asyncio
import os
from apis.geoapify_resorts import find_resorts_geoapify
from apis.weather_openmeteo import get_forecast
from apis.skiapi_resorts import search_resorts, get_ski_resort_details
from config.settings import RAPIDAPI_KEY, GEOAPIFY_API_KEY, OPENAI_API_KEY

async def test_geoapify():
    """Test Geoapify API for resort search."""
    print("\n🏔️ Testing Geoapify API (Resort Search)")
    print("=" * 50)

    if not GEOAPIFY_API_KEY or GEOAPIFY_API_KEY == "your_geoapify_api_key_here":
        print("❌ GEOAPIFY_API_KEY not set in .env file")
        print("📝 Add to .env: GEOAPIFY_API_KEY=your_actual_key_here")
        return False

    try:
        result = await find_resorts_geoapify("Chamonix", lat=None, lon=None, radius_km=30, limit=3)
        if result.get("error"):
            print(f"❌ Geoapify Error: {result['error']}")
            return False
        else:
            resorts = result.get("resorts", [])
            print(f"✅ Found {len(resorts)} resorts near Chamonix:")
            for i, resort in enumerate(resorts, 1):
                print(f"  {i}. {resort.get('name', 'Unknown')}")
            return True
    except Exception as e:
        print(f"❌ Geoapify Exception: {e}")
        return False

async def test_open_meteo():
    """Test Open-Meteo API for weather."""
    print("\n🌤️ Testing Open-Meteo API (Weather)")
    print("=" * 50)

    try:
        # Test with a ski location
        from datetime import date
        forecast = await get_forecast(
            latitude=39.1911,  # Lake Tahoe
            longitude=-120.2356,
            start_date=date.today(),
            end_date=date.today().replace(day=date.today().day + 6)
        )

        if not forecast:
            print("❌ No weather data returned")
            return False
        else:
            print(f"✅ Weather forecast retrieved ({len(forecast)} days)")
            if forecast:
                first_day = forecast[0]
                temp = first_day.temperature_2m_max
                snow = first_day.snowfall_sum
                print(f"    Temperature: {temp:.1f}°C")
                print(f"    Snowfall: {snow:.1f}mm")
            return True
    except Exception as e:
        print(f"❌ Open-Meteo Exception: {e}")
        return False

async def test_skiapi():
    """Test SkiAPI for detailed resort information."""
    print("\n🎿 Testing SkiAPI (Detailed Resort Info)")
    print("=" * 50)

    if not RAPIDAPI_KEY or RAPIDAPI_KEY == "your_rapidapi_key_here":
        print("❌ RAPIDAPI_KEY not set in .env file")
        print("📝 Add to .env: RAPIDAPI_KEY=your_actual_key_here")
        print("\n🚨 Also need to subscribe to SkiAPI:")
        print("1. Go to: https://rapidapi.com/skapi/api/ski-api")
        print("2. Click 'Subscribe to Test' or choose a paid plan")
        return False

    try:
        # Test resort search
        search_result = await search_resorts(query="Vail", per_page=3)
        if search_result.get("error"):
            error = search_result["error"]
            if "403" in str(error):
                print("❌ SkiAPI Subscription Required")
                print("🚨 You need to subscribe to SkiAPI on RapidAPI:")
                print("1. Go to: https://rapidapi.com/skapi/api/ski-api")
                print("2. Click 'Subscribe to Test' or choose a paid plan")
                return False
            elif "401" in str(error):
                print("❌ Invalid RAPIDAPI_KEY")
                print("📝 Check your RAPIDAPI_KEY in .env file")
                return False
            else:
                print(f"❌ SkiAPI Error: {error}")
                return False
        else:
            resorts = search_result.get("resorts", [])
            print(f"✅ Found {len(resorts)} resorts matching 'Vail':")
            for i, resort in enumerate(resorts, 1):
                print(f"  {i}. {resort.get('name', 'Unknown')} - {resort.get('country', '')}")

            if resorts:
                # Test detailed resort info
                resort = resorts[0]
                details = await get_ski_resort_details(
                    resort_name=resort.get("name", ""),
                    country="US",
                    include_snow_report=False
                )

                if details.get("error"):
                    print(f"❌ Resort details error: {details['error']}")
                else:
                    print(f"✅ Detailed info retrieved for {details.get('resort_name', 'Unknown')}")

            return True
    except Exception as e:
        print(f"❌ SkiAPI Exception: {e}")
        return False

async def test_openai():
    """Test OpenAI API key."""
    print("\n🤖 Testing OpenAI API")
    print("=" * 50)

    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
        print("❌ OPENAI_API_KEY not set in .env file")
        print("📝 Add to .env: OPENAI_API_KEY=your_actual_key_here")
        return False

    try:
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)

        # Simple test request
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'API test successful'"}],
            max_tokens=10
        )

        if response.choices and response.choices[0].message.content:
            print("✅ OpenAI API working correctly")
            return True
        else:
            print("❌ OpenAI API returned empty response")
            return False
    except openai.AuthenticationError:
        print("❌ Invalid OpenAI API key")
        return False
    except openai.RateLimitError:
        print("❌ OpenAI rate limit exceeded - check your quota")
        return False
    except Exception as e:
        print(f"❌ OpenAI Exception: {e}")
        return False

async def main():
    """Run all API tests."""
    print("🧪 COMPREHENSIVE API TESTING FOR SKI ASSISTANT")
    print("=" * 60)

    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ No .env file found!")
        print("📝 Please create a .env file in the project root with:")
        print("OPENAI_API_KEY=your_openai_key")
        print("GEOAPIFY_API_KEY=your_geoapify_key")
        print("RAPIDAPI_KEY=your_rapidapi_key")
        print()
        return

    # Run all tests
    results = []

    # Test OpenAI first (needed for the assistant)
    results.append(await test_openai())

    # Test Geoapify
    results.append(await test_geoapify())

    # Test Open-Meteo
    results.append(await test_open_meteo())

    # Test SkiAPI
    results.append(await test_skiapi())

    # Summary
    print("\n🎯 TEST SUMMARY")
    print("=" * 60)

    apis = ["OpenAI", "Geoapify", "Open-Meteo", "SkiAPI"]
    working_count = sum(results)

    for i, (api, working) in enumerate(zip(apis, results), 1):
        status = "✅ WORKING" if working else "❌ FAILED"
        print(f"{i}. {api}: {status}")

    print(f"\n📊 Result: {working_count}/{len(results)} APIs working")

    if working_count == len(results):
        print("🎉 ALL APIs WORKING! Your Ski Assistant is ready! 🎿❄️")
    else:
        print("⚠️  Some APIs need setup. Check the messages above.")

    print("\n🚀 Next steps:")
    if not results[0]:  # OpenAI
        print("- Get OpenAI API key from: https://platform.openai.com/api-keys")
    if not results[1]:  # Geoapify
        print("- Get Geoapify API key from: https://myprojects.geoapify.com/")
    if not results[2]:  # Open-Meteo
        print("- Open-Meteo is free, no key needed")
    if not results[3]:  # SkiAPI
        print("- Subscribe to SkiAPI at: https://rapidapi.com/skapi/api/ski-api")

if __name__ == "__main__":
    asyncio.run(main())
