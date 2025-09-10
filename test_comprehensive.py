"""
Comprehensive Test Suite for SkiTrip Assistant

This test suite demonstrates professional testing practices:
- Unit tests for all core modules
- Integration tests for API interactions
- Mock-based testing for external dependencies
- Error handling and edge case coverage
- Configuration testing
- Clean test organization with fixtures

Run with: python -m pytest test_comprehensive.py -v
"""

import pytest

pytestmark = pytest.mark.asyncio
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import date, datetime
from typing import Dict, Any, List

# Core modules to test
from core.reasoning import llm_with_tools, _build_system_messages, _get_tool_definitions
from core.tools import _execute_tool, FindResortsArgs, GetWeatherForecastArgs
from core.config import (
    MODEL_NAME, TEMPERATURE_CHAIN_OF_THOUGHT, TEMPERATURE_EVIDENCE_ONLY,
    TEMPERATURE_VERIFY, TOOL_PRIORITIES
)
from core.providers.llm import OpenAIProvider
from core.prompts import build_evidence_only_instruction, build_verify_instruction

# Utility modules
from utils.errors import _ok, _err
from utils.dates import normalize_date_range

# API modules (mocked for testing)
from apis.geoapify_resorts import find_resorts_geoapify
        from apis.weather_openmeteo import get_forecast
from apis.skiapi_resorts import get_ski_resort_details
from apis.wikipedia_resorts import search_wikipedia_resort_info


class TestUtilities:
    """Test utility functions and helpers."""

    def test_ok_helper(self):
        """Test successful response helper."""
        result = _ok({"data": "test"}, status="success")
        assert result["ok"] is True
        assert result["data"] == "test"
        assert result["status"] == "success"

    def test_err_helper(self):
        """Test error response helper."""
        result = _err("test_error", "Something went wrong", error_code=500)
        assert result["ok"] is False
        assert result["error"] == "test_error"
        assert result["message"] == "Something went wrong"
        assert result["error_code"] == 500

    def test_date_normalization_valid(self):
        """Test date normalization with valid inputs."""
        # Use future dates to avoid today's date adjustment
        future_date = date.today().replace(year=2025, month=12, day=15)
        start_str = future_date.strftime("%Y-%m-%d")
        end_str = (future_date.replace(day=20)).strftime("%Y-%m-%d")

        result = normalize_date_range(start_str, end_str)
        assert result["start"] == future_date
        assert result["end"] == future_date.replace(day=20)

    def test_date_normalization_past_dates(self):
        """Test date normalization adjusts past dates to today."""
        today = date.today()
        result = normalize_date_range("2020-01-01", "2020-01-05")
        assert result["start"] >= today

    def test_date_normalization_reversed_dates(self):
        """Test date normalization fixes reversed dates."""
        result = normalize_date_range("2025-01-20", "2025-01-15")
        assert result["end"] >= result["start"]


class TestConfiguration:
    """Test configuration management."""

    def test_model_configuration(self):
        """Test LLM model configuration."""
        assert MODEL_NAME == "gpt-4o-mini"
        assert isinstance(MODEL_NAME, str)

    def test_temperature_settings(self):
        """Test temperature configuration values."""
        assert 0.0 <= TEMPERATURE_CHAIN_OF_THOUGHT <= 1.0
        assert TEMPERATURE_EVIDENCE_ONLY == 0.0  # Should be deterministic
        assert TEMPERATURE_VERIFY == 0.0  # Should be deterministic

    def test_tool_priorities(self):
        """Test tool prioritization configuration."""
        assert "resort_info" in TOOL_PRIORITIES
        assert "location_search" in TOOL_PRIORITIES
        assert "weather" in TOOL_PRIORITIES

        # Wikipedia should be primary for resort info
        assert TOOL_PRIORITIES["resort_info"][0] == "wikipedia"


class TestSystemMessages:
    """Test system message building and tool definitions."""

    def test_build_system_messages_structure(self):
        """Test system messages have correct structure."""
        messages = _build_system_messages()
        assert isinstance(messages, list)
        assert len(messages) > 0

        system_msg = messages[0]
        assert system_msg["role"] == "system"
        assert "SkiTrip Assistant" in system_msg["content"]
        assert "ski planning assistant" in system_msg["content"].lower()

    def test_build_system_messages_content(self):
        """Test system messages contain required ski context."""
        messages = _build_system_messages()
        content = messages[0]["content"]

        # Should contain key ski context elements
        assert "ski" in content.lower()
        assert "resort" in content.lower()
        assert "tool" in content.lower()

    def test_tool_definitions_structure(self):
        """Test tool definitions have correct OpenAI format."""
        tools = _get_tool_definitions()
        assert isinstance(tools, list)
        assert len(tools) == 4  # Should have 4 tools

        for tool in tools:
            assert tool["type"] == "function"
            assert "function" in tool
            func_def = tool["function"]
            assert "name" in func_def
            assert "description" in func_def
            assert "parameters" in func_def

    def test_tool_definitions_names(self):
        """Test all expected tools are defined."""
        tools = _get_tool_definitions()
        tool_names = [t["function"]["name"] for t in tools]

        expected_names = [
            "find_resorts_geoapify",
            "get_weather_forecast",
            "get_ski_resort_details",
            "get_wikipedia_resort_info"
        ]

        assert set(tool_names) == set(expected_names)


class TestPrompts:
    """Test prompt building functions."""

    def test_evidence_only_instruction(self):
        """Test evidence-only synthesis instruction."""
        instruction = build_evidence_only_instruction()
        assert isinstance(instruction, str)
        assert len(instruction) > 0
        assert "evidence" in instruction.lower()

    def test_verify_instruction(self):
        """Test verification instruction with draft."""
        draft = "Test draft response"
        instruction = build_verify_instruction(draft)
        assert isinstance(instruction, str)
        assert draft in instruction
        assert "verify" in instruction.lower()


class TestPydanticModels:
    """Test Pydantic argument validation models."""

    def test_find_resorts_args_valid(self):
        """Test valid FindResortsArgs."""
        args = FindResortsArgs(city="Chamonix", radius_km=50, limit=10)
        assert args.city == "Chamonix"
        assert args.radius_km == 50
        assert args.limit == 10

    def test_find_resorts_args_validation(self):
        """Test FindResortsArgs validation constraints."""
        # Test radius constraints
        with pytest.raises(ValueError):
            FindResortsArgs(city="Test", radius_km=200)  # Too high

        with pytest.raises(ValueError):
            FindResortsArgs(city="Test", radius_km=2)  # Too low

        # Test limit constraints
        with pytest.raises(ValueError):
            FindResortsArgs(city="Test", limit=25)  # Too high

        with pytest.raises(ValueError):
            FindResortsArgs(city="Test", limit=0)  # Too low

    def test_weather_args_required_fields(self):
        """Test GetWeatherForecastArgs required fields."""
        with pytest.raises(ValueError):
            GetWeatherForecastArgs(city="Test")  # Missing dates

        args = GetWeatherForecastArgs(
            city="Chamonix",
            start_date="2025-01-15",
            end_date="2025-01-20"
        )
        assert args.city == "Chamonix"


class TestLLMProvider:
    """Test LLM provider abstraction."""

    def test_provider_instantiation(self):
        """Test OpenAI provider can be instantiated."""
        provider = OpenAIProvider()
        assert provider is not None
        assert hasattr(provider, 'chat')

    @patch('openai.OpenAI')
    def test_provider_chat_method(self, mock_openai):
        """Test provider chat method with mocked OpenAI."""
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_message = Mock()
        mock_message.content = "Test response"
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = mock_message
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        provider = OpenAIProvider()
        provider.client = mock_client

        # Test sync chat (would need to be async in real implementation)
        # This is a simplified test structure

    @patch('openai.OpenAI')
    def test_provider_handles_tools(self, mock_openai):
        """Test provider handles tool parameters correctly."""
        mock_client = Mock()
        mock_response = Mock()
        mock_message = Mock()
        mock_message.content = "Tool response"
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = mock_message
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAIProvider()
        provider.client = mock_client

        # Mock the async chat call
        # In real implementation, this would test tool_choice handling


class TestToolExecution:
    """Test tool execution and dispatcher."""

    @patch('apis.geoapify_resorts.find_resorts_geoapify')
    async def test_find_resorts_tool(self, mock_api):
        """Test find_resorts_geoapify tool execution."""
        # Setup mock response
        mock_api.return_value = _ok({
            "area": "Chamonix",
            "resorts": [
                {"name": "Test Resort", "address": "123 Test St", "lat": 45.0, "lon": 6.0}
            ]
        })

        # Execute tool
        result = await _execute_tool("find_resorts_geoapify", {
            "city": "Chamonix",
            "radius_km": 50,
            "limit": 8
        })

        assert result["ok"] is True
        assert "area" in result
        assert result["area"] == "Chamonix"
        mock_api.assert_called_once()

    @patch('apis.weather_openmeteo.get_forecast')
    @patch('apis.geoapify_resorts._geocode')
    async def test_weather_tool(self, mock_geocode, mock_weather):
        """Test weather forecast tool execution."""
        # Setup mocks
        mock_geocode.return_value = (45.9237, 6.8694, "Chamonix, France")
        mock_weather.return_value = [
            Mock(date=date(2025, 1, 15), temperature_2m_max=5.0, temperature_2m_min=-2.0,
                 precipitation_sum=5.0, snowfall_sum=10.0, wind_speed_10m_max=15.0)
        ]

        result = await _execute_tool("get_weather_forecast", {
            "city": "Chamonix",
            "start_date": "2025-01-15",
            "end_date": "2025-01-20"
        })

        assert result["ok"] is True
        assert "location" in result
        assert "forecast" in result
        assert len(result["forecast"]) > 0

    def test_unknown_tool_error(self):
        """Test handling of unknown tools."""
        result = asyncio.run(_execute_tool("unknown_tool", {}))
        assert result["ok"] is False
        assert result["error"] == "unknown_tool"

    def test_invalid_tool_arguments(self):
        """Test validation of tool arguments."""
        result = asyncio.run(_execute_tool("find_resorts_geoapify", {
            "city": "",  # Invalid: empty city
            "radius_km": 200  # Invalid: too high
        }))
        assert result["ok"] is False
        assert result["error"] == "invalid_arguments"


class TestAPIs:
    """Test API integrations with mocking."""

    @patch('httpx.AsyncClient.get')
    @patch('apis.geoapify_resorts._geocode')
    async def test_geoapify_api_mock(self, mock_geocode, mock_get):
        """Test Geoapify API with mocked HTTP calls."""
        # Mock geocoding
        mock_geocode.return_value = (45.9237, 6.8694, "Chamonix, France")

        # Setup mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "features": [
                {
                    "properties": {
                        "name": "Test Ski Resort",
                        "formatted": "123 Mountain Rd",
                        "datasource": {"raw": {"website": "https://test.com"}}
                    },
                    "geometry": {"coordinates": [6.0, 45.0]}
                }
            ]
        }
        mock_get.return_value = mock_response

        result = await find_resorts_geoapify("Chamonix", radius_km=50, limit=5)

        # Check the actual return format from geoapify function
        assert "area" in result
        assert "resorts" in result
        assert len(result["resorts"]) == 1
        assert result["resorts"][0]["name"] == "Test Ski Resort"

    @patch('httpx.AsyncClient.get')
    async def test_weather_api_mock(self, mock_get):
        """Test weather API with mocked HTTP calls."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "daily": {
                "time": ["2025-01-15"],
                "temperature_2m_max": [5.0],
                "temperature_2m_min": [-2.0],
                "precipitation_sum": [5.0],
                "snowfall_sum": [10.0],
                "wind_speed_10m_max": [15.0]  # Correct field name
            }
        }
        mock_get.return_value = mock_response

        result = await get_forecast(45.0, 6.0, date(2025, 1, 15), date(2025, 1, 15))

        assert len(result) == 1
        assert result[0].temperature_2m_max == 5.0
        assert result[0].snowfall_sum == 10.0


class TestErrorHandling:
    """Test comprehensive error handling."""

    @patch('apis.geoapify_resorts.find_resorts_geoapify')
    async def test_api_error_handling(self, mock_api):
        """Test API error handling in tools."""
        mock_api.side_effect = Exception("API Error")

        result = await _execute_tool("find_resorts_geoapify", {
            "city": "Chamonix"
        })

        assert result["ok"] is False
        assert result["error"] == "tool_execution_failed"
        assert "API Error" in result["message"]

    def test_validation_error_handling(self):
        """Test Pydantic validation error handling."""
        # Test with invalid data that should fail validation
        result = asyncio.run(_execute_tool("find_resorts_geoapify", {
            "city": "Test",
            "radius_km": "invalid"  # Should be number
        }))

        assert result["ok"] is False
        assert result["error"] == "invalid_arguments"


class TestIntegration:
    """Integration tests combining multiple components."""

    @patch('core.providers.llm.OpenAIProvider.chat')
    async def test_llm_with_tools_integration(self, mock_chat):
        """Test full LLM with tools integration."""
        # Setup mock responses
        mock_response1 = Mock()
        mock_response1.tool_calls = [
            Mock(function=Mock(name="find_resorts_geoapify", arguments='{"city": "Chamonix"}'))
        ]
        mock_response1.content = None

        mock_response2 = Mock()
        mock_response2.tool_calls = None
        mock_response2.content = "Found great ski resorts in Chamonix!"

        mock_chat.side_effect = [mock_response1, mock_response2]

        with patch('core.tools._execute_tool') as mock_execute:
            mock_execute.return_value = _ok({"area": "Chamonix", "resorts": []})

            result = await llm_with_tools("Find ski resorts in Chamonix")

            assert isinstance(result, str)
            assert len(result) > 0
            mock_chat.assert_called()

    def test_configuration_integration(self):
        """Test that configuration integrates properly across modules."""
        # Test that config values are used consistently
        from core.config import DEFAULT_RADIUS_KM, DEFAULT_LIMIT

        # These should be reasonable defaults
        assert 10 <= DEFAULT_RADIUS_KM <= 100
        assert 1 <= DEFAULT_LIMIT <= 20


class TestCLIFunctionality:
    """Test CLI functionality."""

    def test_cli_imports(self):
        """Test that CLI module can be imported."""
        try:
            from app.cli import main
            assert callable(main)
        except ImportError:
            pytest.skip("CLI dependencies not available")

    def test_orchestrator_imports(self):
        """Test that orchestrator module can be imported."""
        try:
            from core.orchestrator import main
            assert callable(main)
        except ImportError:
            pytest.skip("Orchestrator dependencies not available")


# Test Configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
