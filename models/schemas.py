"""Pydantic data models for SkiTrip Assistant."""

from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator

class AbilityLevel(str, Enum):
    """Ski ability levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class TripSlots(BaseModel):
    """Extracted trip information from user input."""
    region: Optional[str] = None
    origin: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    ability: Optional[AbilityLevel] = None
    preferences: List[str] = Field(default_factory=list)
    
    @validator('end_date')
    def end_date_after_start_date(cls, v, values):
        if v and 'start_date' in values and values['start_date']:
            if v < values['start_date']:
                raise ValueError('end_date must be after start_date')
        return v

class ConversationResponse(BaseModel):
    """Response from the conversational LLM."""
    message: str = Field(..., description="The assistant's response to the user")
    needs_info: bool = Field(default=False, description="Whether the assistant needs more information")
    missing_fields: List[str] = Field(default_factory=list, description="What information is still needed")
    action: str = Field(default="chat", description="What action to take: chat, plan, refine, clear")
    slots: Optional[TripSlots] = Field(default=None, description="Extracted trip information if planning")

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

class Resort(BaseModel):
    """Ski resort information from Foursquare API."""
    name: str
    location: str
    latitude: float
    longitude: float
    rating: Optional[float] = None
    source_id: str = "foursquare"

class PlanStep(BaseModel):
    """A single step in the daily plan."""
    time: str
    activity: str
    description: str
    source_id: str = "assistant"

class DayPlan(BaseModel):
    """Daily plan for the ski trip."""
    date: date
    morning: PlanStep
    lunch: PlanStep
    afternoon: PlanStep
    weather: Optional[WeatherForecast] = None
    resort: Optional[Resort] = None

class Itinerary(BaseModel):
    """Complete ski trip itinerary."""
    region: str
    start_date: date
    end_date: date
    ability: AbilityLevel
    days: List[DayPlan]
    total_cost_estimate: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    source_id: str = "assistant"
