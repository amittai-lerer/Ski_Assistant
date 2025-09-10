"""Open-Meteo weather API integration for SkiTrip Assistant."""

import logging
from datetime import date, datetime
from typing import List, Optional
import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class WeatherForecast(BaseModel):
    """Weather forecast data from Open-Meteo API."""
    date: date
    temperature_2m_max: float
    temperature_2m_min: float
    precipitation_sum: float
    snowfall_sum: float
    wind_speed_10m_max: float
    freezing_level: float
    source_id: str = "open_meteo"

async def get_forecast(latitude: float, longitude: float, start_date: date, end_date: date) -> List[WeatherForecast]:
    """Get weather forecast from Open-Meteo API.
    
    Args:
        latitude: Resort latitude
        longitude: Resort longitude  
        start_date: Start date for forecast
        end_date: End date for forecast
        
    Returns:
        List of weather forecasts
    """
    try:
        # Open-Meteo API endpoint
        url = "https://api.open-meteo.com/v1/forecast"
        
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,snowfall_sum,wind_speed_10m_max",
            "timezone": "auto"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=15.0)
            response.raise_for_status()
            data = response.json()
            
        # Parse the response
        forecasts = []
        daily = data.get("daily", {})
        
        for i, date_str in enumerate(daily.get("time", [])):
            forecast = WeatherForecast(
                date=date.fromisoformat(date_str),
                temperature_2m_max=daily["temperature_2m_max"][i],
                temperature_2m_min=daily["temperature_2m_min"][i],
                precipitation_sum=daily["precipitation_sum"][i],
                snowfall_sum=daily["snowfall_sum"][i],
                wind_speed_10m_max=daily["wind_speed_10m_max"][i],
                freezing_level=0.0,  # Not available in free API
                source_id="open_meteo"
            )
            forecasts.append(forecast)
            
        return forecasts
        
    except Exception as e:
        logger.error(f"Error getting weather forecast: {e}")
        return []

async def get_current_weather(latitude: float, longitude: float) -> Optional[WeatherForecast]:
    """Get current weather conditions.
    
    Args:
        latitude: Resort latitude
        longitude: Resort longitude
        
    Returns:
        Current weather forecast or None
    """
    try:
        forecasts = await get_forecast(latitude, longitude, date.today(), date.today())
        return forecasts[0] if forecasts else None
    except Exception as e:
        logger.error(f"Error getting current weather: {e}")
        return None
