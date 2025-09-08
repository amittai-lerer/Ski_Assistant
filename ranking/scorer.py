"""Deterministic scoring and ranking for ski resorts."""

import logging
from typing import List, Dict, Any
from models.schemas import Resort, WeatherForecast

logger = logging.getLogger(__name__)

def rank_resorts(resorts: List[Resort], weather_data: Dict[str, List[WeatherForecast]]) -> List[Resort]:
    """Rank resorts based on weather conditions.
    
    Args:
        resorts: List of resorts to rank
        weather_data: Weather data for each resort
        
    Returns:
        Ranked list of resorts
    """
    try:
        # Simple ranking based on weather
        scored_resorts = []
        
        for resort in resorts:
            score = 0.0
            weather = weather_data.get(resort.name, [])
            
            if weather:
                # Score based on snowfall (higher is better)
                total_snowfall = sum(day.snowfall_sum for day in weather)
                score += total_snowfall * 0.4
                
                # Score based on wind (lower is better)
                avg_wind = sum(day.wind_speed_10m_max for day in weather) / len(weather)
                score += max(0, 50 - avg_wind) * 0.3
                
                # Score based on temperature (moderate is better)
                avg_temp = sum((day.temperature_2m_max + day.temperature_2m_min) / 2 for day in weather) / len(weather)
                score += max(0, 20 - abs(avg_temp + 5)) * 0.3
            else:
                # Default score if no weather data
                score = 50.0
                
            scored_resorts.append((resort, score))
            
        # Sort by score (descending)
        scored_resorts.sort(key=lambda x: x[1], reverse=True)
        
        return [resort for resort, score in scored_resorts]
        
    except Exception as e:
        logger.error(f"Error ranking resorts: {e}")
        return resorts  # Return original order if ranking fails

