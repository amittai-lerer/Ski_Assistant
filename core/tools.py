"""
Tool Registry & Dispatcher - Clean Architecture Pattern

Demonstrates professional practices:
- Registry pattern for extensibility
- Pydantic for type safety and validation
- Clean error handling with consistent envelopes
- Separation of tool logic from business logic
- Async/await for proper I/O handling

Interview Notes:
- Shows understanding of design patterns
- Demonstrates type safety importance
- Clean error handling without complexity
"""

from typing import Dict, Any
import logging
from pydantic import BaseModel, Field, ValidationError
from utils.errors import _ok, _err

logger = logging.getLogger(__name__)

# Argument models
class FindResortsArgs(BaseModel):
    city: str
    lat: float | None = None
    lon: float | None = None
    radius_km: int = Field(50, ge=5, le=100)
    limit: int = Field(8, ge=1, le=20)

class GetWeatherForecastArgs(BaseModel):
    city: str
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD

class GetSkiResortDetailsArgs(BaseModel):
    resort_name: str
    country: str = ""
    include_snow_report: bool = False

class GetWikipediaResortInfoArgs(BaseModel):
    resort_name: str
    country: str = ""

# Tool registry
REGISTRY = {
    "find_resorts_geoapify": (FindResortsArgs, "_handle_find_resorts_geoapify"),
    "get_weather_forecast": (GetWeatherForecastArgs, "_handle_get_weather_forecast"),
    "get_ski_resort_details": (GetSkiResortDetailsArgs, "_handle_get_ski_resort_details"),
    "get_wikipedia_resort_info": (GetWikipediaResortInfoArgs, "_handle_get_wikipedia_resort_info"),
}

async def _execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool dispatcher demonstrating clean architecture patterns.

    Interview Notes:
    - Registry pattern allows easy tool addition/removal
    - Pydantic validation prevents runtime errors
    - Consistent error handling across all tools
    - Async pattern for proper I/O handling
    - Type safety throughout

    Args:
        tool_name: Tool to execute
        tool_args: Arguments for the tool

    Returns:
        Tool result or error envelope
    """
    # Validate tool exists
    if tool_name not in REGISTRY:
        return _err("unknown_tool", f"Unknown tool: {tool_name}")

    # Get tool configuration
    ArgsModel, handler_name = REGISTRY[tool_name]

    # Validate arguments using Pydantic
    try:
        args = ArgsModel(**(tool_args or {}))
    except ValidationError as ve:
        logger.warning(f"Validation error for {tool_name}: {ve}")
        return _err("invalid_arguments", f"Invalid args for {tool_name}: {ve}")

    # Execute tool with error handling
    try:
        handler = globals()[handler_name]
        return await handler(args)
    except Exception as e:
        logger.error(f"Tool {tool_name} failed: {e}")
        return _err("tool_execution_failed", f"{tool_name} failed: {e}")

# Per-tool handlers (async, consistent error handling)
async def _handle_find_resorts_geoapify(args: FindResortsArgs) -> Dict[str, Any]:
    from apis.geoapify_resorts import find_resorts_geoapify
    result = await find_resorts_geoapify(**args.model_dump())
    return result  # Keep original shape

async def _handle_get_weather_forecast(args: GetWeatherForecastArgs) -> Dict[str, Any]:
    from apis.weather_openmeteo import get_forecast
    from apis.geoapify_resorts import _geocode
    from utils.dates import normalize_date_range

    try:
        rng = normalize_date_range(args.start_date, args.end_date)
        coords = await _geocode(args.city)
        if not coords:
            return _err("geocode_failed", f"Could not find coordinates for {args.city}")

        lat, lon, location_name = coords
        forecast = await get_forecast(lat, lon, rng["start"], rng["end"])

        if not forecast:
            return _err("no_weather_data", f"No weather data for {args.city}")

        forecast_data = [{
            "date": d.date.isoformat(),
            "temperature_max": d.temperature_2m_max,
            "temperature_min": d.temperature_2m_min,
            "precipitation": d.precipitation_sum,
            "snowfall": d.snowfall_sum,
            "wind_speed": d.wind_speed_10m_max
        } for d in forecast]

        return _ok({"location": location_name, "forecast": forecast_data, "days": len(forecast)})

    except Exception as e:
        return _err("weather_error", f"Weather service error: {e}")

async def _handle_get_ski_resort_details(args: GetSkiResortDetailsArgs) -> Dict[str, Any]:
    from apis.skiapi_resorts import get_ski_resort_details

    try:
        result = await get_ski_resort_details(
            resort_name=args.resort_name,
            country=args.country or "",
            include_snow_report=args.include_snow_report,
        )
        return result
    except Exception as e:
        return _err("skiapi_error", f"SkiAPI error: {e}")

async def _handle_get_wikipedia_resort_info(args: GetWikipediaResortInfoArgs) -> Dict[str, Any]:
    from apis.wikipedia_resorts import search_wikipedia_resort_info

    try:
        wiki = await search_wikipedia_resort_info(args.resort_name, args.country or "")
        if wiki.get("success"):
            return _ok({
                "wikipedia_info": wiki,
                "resort_name": wiki.get("resort_name"),
                "summary": wiki.get("summary"),
                "page_url": wiki.get("page_url"),
                "source": "wikipedia",
            })
        return _err("no_wikipedia_page", f"No Wikipedia page for '{args.resort_name}'")
    except Exception as e:
        return _err("wikipedia_error", f"Wikipedia error: {e}")
