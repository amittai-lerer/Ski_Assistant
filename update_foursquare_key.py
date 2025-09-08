#!/usr/bin/env python3
"""
Foursquare API Key Update Helper
Helps you update your Foursquare API key in the .env file
"""

import os
import re

def validate_foursquare_key(key):
    """Validate Foursquare API key format"""
    if not key:
        return False, "API key cannot be empty"

    # Remove any Bearer prefix if present
    key = key.replace('Bearer ', '').strip()

    # Check for modern fsq3 format
    if key.startswith('fsq3'):
        return True, "Valid modern Foursquare API key format"

    # Check for older formats (might still work)
    if len(key) >= 40 and re.match(r'^[A-Z0-9]+$', key):
        return True, "Valid API key format (might be older version)"

    return False, "Invalid API key format. Should start with 'fsq3' or be alphanumeric"

def update_env_file(new_key):
    """Update the .env file with new Foursquare API key"""
    env_file = '.env'

    if not os.path.exists(env_file):
        print("❌ .env file not found!")
        return False

    try:
        with open(env_file, 'r') as f:
            lines = f.readlines()

        # Find and update FOURSQUARE_API_KEY line
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('FOURSQUARE_API_KEY='):
                lines[i] = f'FOURSQUARE_API_KEY={new_key}\n'
                updated = True
                break

        # If not found, add it
        if not updated:
            lines.append(f'\nFOURSQUARE_API_KEY={new_key}\n')

        with open(env_file, 'w') as f:
            f.writelines(lines)

        print("✅ .env file updated successfully!")
        return True

    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False

def test_new_key(new_key):
    """Test the new API key"""
    import httpx
    import asyncio

    async def test():
        url = 'https://api.foursquare.com/v3/places/search'
        headers = {
            'Authorization': new_key,
            'Accept': 'application/json'
        }
        params = {
            'query': 'ski resort',
            'near': 'Lake Tahoe',
            'limit': 1
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])
                    print(f"✅ SUCCESS! Found {len(results)} results")
                    if results:
                        place = results[0]
                        print(f"🏔️ Test result: {place.get('name', 'Unknown')}")
                    return True
                else:
                    print(f"❌ Still failing with status: {response.status_code}")
                    return False

            except Exception as e:
                print(f"❌ Test failed: {e}")
                return False

    return asyncio.run(test())

def main():
    """Main update script"""
    print("🔄 FOURSQUARE API KEY UPDATE HELPER")
    print("=" * 50)
    print()
    print("📋 INSTRUCTIONS:")
    print("1. Go to https://developer.foursquare.com/")
    print("2. Get your API key (should start with 'fsq3')")
    print("3. Paste it below")
    print("4. We'll update your .env file and test it")
    print()

    while True:
        new_key = input("Enter your new Foursquare API key: ").strip()

        if not new_key:
            print("❌ No key entered. Try again or press Ctrl+C to exit.")
            continue

        # Validate format
        is_valid, message = validate_foursquare_key(new_key)
        print(f"🔍 Validation: {message}")

        if is_valid:
            # Update .env file
            if update_env_file(new_key):
                print("\n🧪 Testing new API key...")
                if test_new_key(new_key):
                    print("\n🎉 SUCCESS! Your Foursquare API is now working!")
                    print("🚀 You can now run: python test_apis.py")
                    break
                else:
                    print("\n❌ Test failed. The key might still be invalid.")
                    choice = input("Try a different key? (y/n): ").lower()
                    if choice != 'y':
                        break
            else:
                break
        else:
            print("❌ Invalid format. Please check your API key.")
            choice = input("Try again? (y/n): ").lower()
            if choice != 'y':
                break

if __name__ == "__main__":
    main()
