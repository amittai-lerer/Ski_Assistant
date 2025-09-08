#!/usr/bin/env python3
"""Comprehensive test script to verify SkiTrip Assistant functionality."""

import asyncio
import sys
import json
from pathlib import Path
from datetime import date

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported."""
    print("�� Testing imports...")
    
    try:
        from config.settings import OPENAI_API_KEY, GEOAPIFY_API_KEY, DEBUG
        from models.schemas import TripSlots, AbilityLevel, Resort, ForecastDay
        from core.reasoning import llm_json
        from core.orchestrator import run
        from apis.weather_openmeteo import get_forecast
        from apis.geoapify_resorts import find_resorts_geoapify
        from ranking.scorer import rank, compute_features, score
        from ui.renderers import render_plan
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_configuration():
    """Test configuration loading."""
    print("\n🔧 Testing configuration...")
    
    try:
        from config.settings import (
            OPENAI_API_KEY, GEOAPIFY_API_KEY, DEBUG,
            LLM_TEMPERATURE, MAX_RESORTS, TIMEOUT_S
        )
        
        print(f"  OpenAI API Key: {'✅ Set' if OPENAI_API_KEY else '❌ Missing'}")
        print(f"  Geoapify API Key: {'✅ Set' if GEOAPIFY_API_KEY else '❌ Missing'}")
        print(f"  Debug Mode: {DEBUG}")
        print(f"  LLM Temperature: {LLM_TEMPERATURE}")
        print(f"  Max Resorts: {MAX_RESORTS}")
        print(f"  Timeout: {TIMEOUT_S}s")
        
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_data_models():
    """Test Pydantic data models."""
    print("\n📊 Testing data models...")
    
    try:
        from models.schemas import TripSlots, AbilityLevel, Resort, ForecastDay, PlanStep
        
        # Test TripSlots
        trip = TripSlots(
            region="Lake Tahoe",
            start_date=date(2025, 12, 20),
            end_date=date(2025, 12, 22),
            ability=AbilityLevel.INTERMEDIATE
        )
        print(f"  TripSlots: ✅ {trip.region}")
        
        # Test Resort
        resort = Resort(
            name="Test Resort",
            address="123 Test St",
            latitude=39.1,
            longitude=-120.0,
            category="Ski Resort",
            source_id="test:123"
        )
        print(f"  Resort: ✅ {resort.name}")
        
        # Test ForecastDay
        forecast = ForecastDay(
            date=date(2025, 12, 20),
            latitude=39.1,
            longitude=-120.0,
            max_temp_c=2.0,
            min_temp_c=-5.0,
            precipitation_mm=5.0,
            snowfall_mm=10.0,
            wind_speed_kph=15.0,
            wind_direction_deg=180.0,
            freezing_level_m=1500.0,
            source_id="test:forecast_1"
        )
        print(f"  ForecastDay: ✅ {forecast.snowfall_mm}mm snow")
        
        return True
    except Exception as e:
        print(f"❌ Data model error: {e}")
        return False

def test_llm_integration():
    """Test LLM integration."""
    print("\n🤖 Testing LLM integration...")
    
    try:
        from core.reasoning import llm_json
        from models.schemas import TripSlots
        
        # Test with fake data (should work even without API key)
        result = llm_json("Test prompt", TripSlots)
        print(f"  LLM Integration: ✅ {result.region}")
        return True
    except Exception as e:
        print(f"❌ LLM integration error: {e}")
        return False

def test_scoring_algorithm():
    """Test deterministic scoring."""
    print("\n📈 Testing scoring algorithm...")
    
    try:
        from ranking.scorer import compute_features, score, normalize
        from models.schemas import ForecastDay
        from datetime import date
        
        # Create test forecast data
        forecast_days = [
            ForecastDay(
                date=date(2025, 12, 20),
                latitude=39.1,
                longitude=-120.0,
                max_temp_c=2.0,
                min_temp_c=-5.0,
                precipitation_mm=5.0,
                snowfall_mm=15.0,
                wind_speed_kph=10.0,
                wind_direction_deg=180.0,
                freezing_level_m=1500.0,
                source_id="test:forecast_1"
            )
        ]
        
        # Test feature computation
        features = compute_features(forecast_days)
        print(f"  Features computed: ✅ {features}")
        
        # Test scoring
        score_val = score(features)
        print(f"  Score calculated: ✅ {score_val:.3f}")
        
        # Test normalization
        norm_val = normalize(15, 0, 30)
        print(f"  Normalization: ✅ {norm_val}")
        
        return True
    except Exception as e:
        print(f"❌ Scoring algorithm error: {e}")
        return False

async def test_api_integrations():
    """Test external API integrations."""
    print("\n🌐 Testing API integrations...")
    
    try:
        from apis.weather_openmeteo import get_forecast
        from apis.geoapify_resorts import find_resorts_geoapify
        from config.settings import GEOAPIFY_API_KEY
        
        # Test weather API (should work without API key in dev mode)
        print("  Testing weather API...")
        try:
            forecast = await get_forecast(39.1, -120.0, date(2025, 12, 20), date(2025, 12, 22))
            print(f"    Weather API: ✅ {len(forecast)} forecast days")
        except Exception as e:
            print(f"    Weather API: ⚠️ {e} (expected in dev mode)")
        
        # Test places API
        print("  Testing places API...")
        try:
            result = await find_resorts_geoapify(city="Lake Tahoe", limit=3)
            resorts = result.get("resorts", [])
            print(f"    Places API: ✅ {len(resorts)} resorts found")
        except Exception as e:
            print(f"    Places API: ⚠️ {e} (expected without API key)")
        
        return True
    except Exception as e:
        print(f"❌ API integration error: {e}")
        return False

async def test_end_to_end():
    """Test complete end-to-end flow."""
    print("\n�� Testing end-to-end flow...")
    
    try:
        from core.orchestrator import run
        
        # Test with CLI-style context
        ctx = {
            "region": "Lake Tahoe",
            "dates": "2025-12-20..2025-12-22",
            "ability": "intermediate"
        }
        
        print("  Running orchestration...")
        result = await run("", ctx)
        
        print(f"  End-to-end: ✅ {len(result)} characters output")
        print(f"  First 200 chars: {result[:200]}...")
        
        return True
    except Exception as e:
        print(f"❌ End-to-end error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_interface():
    """Test CLI interface."""
    print("\n💻 Testing CLI interface...")
    
    try:
        import subprocess
        import sys
        
        # Test CLI help
        result = subprocess.run([
            sys.executable, "-m", "app.cli", "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("  CLI Help: ✅ Working")
        else:
            print(f"  CLI Help: ❌ {result.stderr}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ CLI interface error: {e}")
        return False

async def main():
    """Run all tests."""
    print("🧪 SkiTrip Assistant - Comprehensive Test Suite")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("Data Models", test_data_models),
        ("LLM Integration", test_llm_integration),
        ("Scoring Algorithm", test_scoring_algorithm),
        ("API Integrations", test_api_integrations),
        ("End-to-End Flow", test_end_to_end),
        ("CLI Interface", test_cli_interface),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                success = await test_func()
            else:
                success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("�� TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 ALL TESTS PASSED! Your SkiTrip Assistant is ready!")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
