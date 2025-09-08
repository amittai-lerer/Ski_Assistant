#!/usr/bin/env python3
"""
Comprehensive API Testing Script for Ski Assistant
Tests all external APIs and validates their functionality
"""

import asyncio
import httpx
from datetime import date, timedelta
from config.settings import OPENAI_API_KEY, FOURSQUARE_API_KEY, USE_REAL_OPENAI
import openai

async def test_openai_api():
    """Test OpenAI API connectivity and quota"""
    print("🧪 TESTING OPENAI API")
    print("-" * 30)

    if not USE_REAL_OPENAI:
        print("❌ USE_REAL_OPENAI is False - Enable real API calls first")
        return False

    if not OPENAI_API_KEY:
        print("❌ No OpenAI API key configured")
        return False

    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    try:
        # Test 1: List available models
        models_response = client.models.list()
        print("✅ API Key authenticated successfully")

        # Check if gpt-4o-mini is available
        model_ids = [model.id for model in models_response.data]
        if 'gpt-4o-mini' in model_ids:
            print("✅ gpt-4o-mini model available")
        else:
            print("⚠️  gpt-4o-mini not in available models")

        # Test 2: Simple chat completion
        chat_response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{'role': 'user', 'content': 'Hello, test message for ski assistant'}],
            max_tokens=50
        )

        response_text = chat_response.choices[0].message.content.strip()
        print("✅ Chat completion successful")
        print(f"   Response: {response_text[:50]}...")

        return True

    except openai.AuthenticationError as e:
        print("❌ INVALID API KEY")
        print(f"   Error: {e}")
        return False

    except openai.RateLimitError as e:
        print("❌ QUOTA EXCEEDED - Add credits to your OpenAI account")
        print("   Visit: https://platform.openai.com/account/billing")
        print(f"   Error: {e}")
        return False

    except Exception as e:
        print(f"❌ OPENAI API ERROR: {e}")
        return False

async def test_foursquare_api():
    """Test Foursquare Places API"""
    print("\n🧪 TESTING FOURSQUARE API")
    print("-" * 35)

    if not FOURSQUARE_API_KEY:
        print("❌ No Foursquare API key configured")
        return False

    url = 'https://api.foursquare.com/v3/places/search'
    headers = {
        'Authorization': FOURSQUARE_API_KEY,
        'Accept': 'application/json'
    }
    params = {
        'query': 'ski resort',
        'near': 'Lake Tahoe',
        'limit': 3
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])

                print("✅ Foursquare API working!")
                print(f"   Found {len(results)} ski resorts in Lake Tahoe")

                if results:
                    for i, place in enumerate(results[:2], 1):
                        name = place.get('name', 'Unknown')
                        address = place.get('location', {}).get('formatted_address', 'Unknown location')
                        print(f"   {i}. {name} - {address}")

                return True

            elif response.status_code == 401:
                print("❌ INVALID API KEY (401 Unauthorized)")
                print("   Get a valid key from: https://developer.foursquare.com/")
                return False

            elif response.status_code == 403:
                print("❌ API KEY FORBIDDEN (403)")
                print("   Your API key lacks required permissions")
                return False

            else:
                print(f"❌ HTTP ERROR: {response.status_code}")
                print(f"   Response: {response.text[:100]}")
                return False

        except Exception as e:
            print(f"❌ CONNECTION ERROR: {e}")
            return False

async def test_weather_api():
    """Test Open-Meteo Weather API for different date ranges"""
    print("\n🧪 TESTING WEATHER API")
    print("-" * 30)

    # Test 1: Current date (should always work)
    print("📅 Testing current date forecast...")
    today = date.today()
    tomorrow = today + timedelta(days=1)

    url = 'https://api.open-meteo.com/v1/forecast'
    params = {
        'latitude': 39.0968,  # Lake Tahoe
        'longitude': -120.0324,
        'start_date': today.isoformat(),
        'end_date': tomorrow.isoformat(),
        'daily': 'temperature_2m_max,temperature_2m_min,snowfall_sum',
        'timezone': 'auto'
    }

    current_works = False
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                daily = data.get('daily', {})
                temps = daily.get('temperature_2m_max', [])
                snow = daily.get('snowfall_sum', [])

                if temps and snow:
                    print("✅ Current date weather works!")
                    print(f"   Today: {temps[0]}°C, Snow: {snow[0]}mm")
                    current_works = True
                else:
                    print("❌ Weather data incomplete")
            else:
                print(f"❌ Current date failed: {response.status_code}")
                print(f"   {response.text[:100]}")

        except Exception as e:
            print(f"❌ Current date connection error: {e}")

    # Test 2: Near future (next few weeks)
    print("\\n📅 Testing near future forecast...")
    future_start = today + timedelta(days=7)
    future_end = future_start + timedelta(days=2)

    params_future = {
        'latitude': 39.0968,
        'longitude': -120.0324,
        'start_date': future_start.isoformat(),
        'end_date': future_end.isoformat(),
        'daily': 'temperature_2m_max,snowfall_sum',
        'timezone': 'auto'
    }

    future_works = False
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params_future, timeout=10)

            if response.status_code == 200:
                data = response.json()
                daily = data.get('daily', {})
                dates = daily.get('time', [])
                temps = daily.get('temperature_2m_max', [])

                if dates and temps:
                    print("✅ Near future weather works!")
                    print(f"   {dates[0]}: {temps[0]}°C")
                    future_works = True
                else:
                    print("❌ Future weather data incomplete")
            else:
                print(f"❌ Future date failed: {response.status_code}")
                print(f"   This is normal - weather APIs have limited forecast ranges")
                print(f"   Response: {response.text[:100]}")

        except Exception as e:
            print(f"❌ Future date connection error: {e}")

    return current_works

async def main():
    """Run all API tests"""
    print("🚀 SKI ASSISTANT API VALIDATION SUITE")
    print("=" * 50)
    print("Testing all external API connections...")
    print("This ensures your ski assistant will work with real data.")
    print()

    results = []

    # Test OpenAI
    openai_ok = await test_openai_api()
    results.append(("OpenAI API", openai_ok))

    # Test Foursquare
    foursquare_ok = await test_foursquare_api()
    results.append(("Foursquare API", foursquare_ok))

    # Test Weather
    weather_ok = await test_weather_api()
    results.append(("Weather API", weather_ok))

    # Summary
    print("\\n" + "=" * 50)
    print("🎯 API TEST RESULTS SUMMARY")
    print("=" * 50)

    all_pass = True
    for api_name, status in results:
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {api_name}: {'WORKING' if status else 'NEEDS FIXING'}")
        if not status:
            all_pass = False

    print()
    if all_pass:
        print("🎉 ALL APIs ARE WORKING! Your Ski Assistant is ready!")
        print("\\n🚀 You can now run: python -m app.cli")
    else:
        print("⚠️  SOME APIs NEED FIXING:")
        print("\\n🔧 To fix:")
        print("1. OpenAI: Add credits at https://platform.openai.com/account/billing")
        print("2. Foursquare: Get API key at https://developer.foursquare.com/")
        print("3. Weather: Works for current dates, limited for future dates (normal)")

        print("\\n💡 Run this test again after fixing APIs:")
        print("   python test_apis.py")

if __name__ == "__main__":
    asyncio.run(main())
