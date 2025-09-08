#!/usr/bin/env python3
"""
Foursquare API Only Test Script
Tests only the Foursquare API integration to isolate issues
"""

import httpx
import asyncio
from config.settings import FOURSQUARE_API_KEY

async def test_foursquare_only():
    print('🔍 FOURSQUARE API KEY ONLY TEST')
    print('=' * 50)
    print()

    # Check API key configuration
    print('📋 API KEY CONFIGURATION:')
    print(f'🔑 API Key: {FOURSQUARE_API_KEY}')
    print(f'🔑 Key Length: {len(FOURSQUARE_API_KEY)} characters')
    print(f'🔑 Starts with: {FOURSQUARE_API_KEY[:8]}...')
    print(f'🔑 Format: {"✅ Modern (fsq3_)" if FOURSQUARE_API_KEY.startswith("fsq3_") else "❌ Legacy"}')
    print()

    print('🧪 TESTING FOURSQUARE API CALLS:')
    print('-' * 35)

    # Test different queries
    test_queries = [
        ('ski resort', 'Lake Tahoe'),
        ('mountain resort', 'Aspen'),
        ('ski area', 'Vail'),
        ('ski lodge', 'Park City')
    ]

    all_failed = True

    for query, location in test_queries:
        print(f'\n🔎 Testing: "{query}" in {location}')

        url = 'https://api.foursquare.com/v3/places/search'
        headers = {
            'Authorization': FOURSQUARE_API_KEY,
            'Accept': 'application/json'
        }
        params = {
            'query': query,
            'near': location,
            'limit': 3
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])
                    print(f'   ✅ SUCCESS: Found {len(results)} results')

                    if results:
                        for i, place in enumerate(results[:2], 1):
                            name = place.get('name', 'Unknown')
                            category = place.get('categories', [{}])[0].get('name', 'Unknown') if place.get('categories') else 'Unknown'
                            print(f'      {i}. {name} ({category})')

                    all_failed = False

                elif response.status_code == 401:
                    print(f'   ❌ FAILED: 401 Unauthorized')
                    print('   💡 API key is invalid or expired')

                elif response.status_code == 403:
                    print(f'   ❌ FAILED: 403 Forbidden')
                    print('   💡 API key lacks permissions')

                else:
                    print(f'   ❌ FAILED: HTTP {response.status_code}')
                    print(f'      Response: {response.text[:100]}...')

        except Exception as e:
            print(f'   ❌ ERROR: {e}')

        await asyncio.sleep(1)  # Rate limiting

    return not all_failed

async def test_with_mock_fallback():
    print('\n🧪 TESTING MOCK FALLBACK:')
    print('-' * 30)

    try:
        from apis.places_foursquare import search_resorts
        resorts = await search_resorts('Lake Tahoe')
        print(f'✅ Mock fallback working: Found {len(resorts)} resorts')

        for resort in resorts:
            print(f'   • {resort.name} - {resort.location}')
            print(f'     📍 Lat: {resort.latitude:.4f}, Lng: {resort.longitude:.4f}')
            print(f'     ⭐ Rating: {resort.rating}')

        return True

    except Exception as e:
        print(f'❌ Mock fallback failed: {e}')
        return False

async def main():
    print('⏳ Testing real Foursquare API...')
    real_api_works = await test_foursquare_only()

    print('\n⏳ Testing mock fallback...')
    mock_works = await test_with_mock_fallback()

    print('\n' + '=' * 50)
    print('🎯 FOURSQUARE API TEST RESULTS:')
    print('=' * 50)

    if real_api_works:
        print('✅ REAL API: WORKING - You have a valid Foursquare API key!')
    else:
        print('❌ REAL API: FAILED - API key is invalid or expired')

    if mock_works:
        print('✅ MOCK FALLBACK: WORKING - System can run without real API')
    else:
        print('❌ MOCK FALLBACK: FAILED - System cannot run at all')

    print('\n💡 NEXT STEPS:')
    if not real_api_works:
        print('1. Get new API key from: https://developer.foursquare.com/')
        print('2. Make sure it starts with "fsq3_"')
        print('3. Update FOURSQUARE_API_KEY in .env file')
        print('4. Run: python test_foursquare_only.py')

    if mock_works:
        print('✓ You can use the system with mock data: python -m app.cli')

if __name__ == "__main__":
    asyncio.run(main())
