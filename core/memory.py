"""Memory and context management for SkiTrip Assistant."""

import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from models.schemas import Itinerary

logger = logging.getLogger(__name__)

# Simple file-based storage
MEMORY_FILE = Path("ski_assistant_memory.json")

def save_last_plan(itinerary: Optional[Itinerary]) -> None:
    """Save the last plan to memory.
    
    Args:
        itinerary: The itinerary to save, or None to clear
    """
    try:
        if itinerary is None:
            # Clear the plan
            if MEMORY_FILE.exists():
                MEMORY_FILE.unlink()
        else:
            # Save the plan
            data = {
                "region": itinerary.region,
                "start_date": itinerary.start_date.isoformat(),
                "end_date": itinerary.end_date.isoformat(),
                "ability": itinerary.ability.value,
                "days": [
                    {
                        "date": day.date.isoformat(),
                        "morning": {
                            "time": day.morning.time,
                            "activity": day.morning.activity,
                            "description": day.morning.description,
                            "source_id": day.morning.source_id
                        },
                        "lunch": {
                            "time": day.lunch.time,
                            "activity": day.lunch.activity,
                            "description": day.lunch.description,
                            "source_id": day.lunch.source_id
                        },
                        "afternoon": {
                            "time": day.afternoon.time,
                            "activity": day.afternoon.activity,
                            "description": day.afternoon.description,
                            "source_id": day.afternoon.source_id
                        }
                    }
                    for day in itinerary.days
                ],
                "created_at": itinerary.created_at.isoformat(),
                "source_id": itinerary.source_id
            }
            
            with open(MEMORY_FILE, 'w') as f:
                json.dump(data, f, indent=2)
                
    except Exception as e:
        logger.error(f"Error saving plan: {e}")

def load_last_plan() -> Optional[Itinerary]:
    """Load the last plan from memory.
    
    Returns:
        The last itinerary, or None if not found
    """
    try:
        if not MEMORY_FILE.exists():
            return None
            
        with open(MEMORY_FILE, 'r') as f:
            data = json.load(f)
            
        # Convert back to Itinerary object
        from datetime import date, datetime
        from models.schemas import DayPlan, PlanStep, AbilityLevel
        
        days = []
        for day_data in data.get("days", []):
            day = DayPlan(
                date=date.fromisoformat(day_data["date"]),
                morning=PlanStep(**day_data["morning"]),
                lunch=PlanStep(**day_data["lunch"]),
                afternoon=PlanStep(**day_data["afternoon"]),
                weather=None,  # Weather data not stored in memory
                resort=None    # Resort data not stored in memory
            )
            days.append(day)
            
        return Itinerary(
            region=data["region"],
            start_date=date.fromisoformat(data["start_date"]),
            end_date=date.fromisoformat(data["end_date"]),
            ability=AbilityLevel(data["ability"]),
            days=days,
            created_at=datetime.fromisoformat(data["created_at"]),
            source_id=data["source_id"]
        )
        
    except Exception as e:
        logger.error(f"Error loading plan: {e}")
        return None

def get_plan_info() -> str:
    """Get a summary of the current plan.
    
    Returns:
        Plan summary string
    """
    try:
        plan = load_last_plan()
        if not plan:
            return "No plan found"
            
        return f"Current plan: {plan.region} from {plan.start_date} to {plan.end_date} for {plan.ability.value} skiers"
        
    except Exception as e:
        logger.error(f"Error getting plan info: {e}")
        return "Error getting plan info"


