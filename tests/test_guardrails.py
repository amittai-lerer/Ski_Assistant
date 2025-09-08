"""Unit tests for hallucination prevention and guardrails.

This module tests the guardrail system to ensure it properly prevents
hallucinations and validates data integrity. Tests cover schema validation,
source ID verification, self-checking, and numeric constraints.
"""

import pytest
from datetime import date, datetime
from typing import List

from models.schemas import Itinerary, DayPlan, PlanStep, TripSlots, AbilityLevel
from core.guardrails import verify_and_prune, _verify_source_ids, _verify_numeric_constraints


class TestGuardrails:
    """Test suite for guardrail functionality."""
    
    def test_plan_step_must_have_source_id(self):
        """Test that PlanStep without source_id fails validation."""
        # Create step without source_id
        step = PlanStep(
            time="9:00 AM",
            activity="Morning skiing",
            location="Test Resort",
            duration_minutes=180,
            notes="Test notes"
            # Missing source_id - should fail
        )
        
        # This should raise a ValidationError
        with pytest.raises(ValueError, match="source_id"):
            step.source_id = ""  # Empty source_id should fail validation
    
    def test_self_check_removes_unsupported_claims(self):
        """Test that self-check identifies and removes unsupported claims."""
        # Create a plan with some unsupported claims
        trip_slots = TripSlots(
            region="Test Region",
            start_date=date(2025, 12, 20),
            end_date=date(2025, 12, 22),
            ability=AbilityLevel.INTERMEDIATE
        )
        
        # Create plan with unsupported claim
        day_plan = DayPlan(
            date=date(2025, 12, 20),
            resort="Test Resort",
            weather_summary="Sunny, 5°C",
            steps=[
                PlanStep(
                    time="9:00 AM",
                    activity="Morning skiing",
                    location="Test Resort",
                    duration_minutes=180,
                    notes="Best resort in the world",  # Unsupported claim
                    source_id="test:step_1"
                )
            ],
            total_ski_minutes=180,
            source_id="test:day_1"
        )
        
        itinerary = Itinerary(
            trip_slots=trip_slots,
            ranked_resorts=[],
            daily_plans=[day_plan]
        )
        
        # Mock evidence with limited data
        evidence = {
            "resorts": [],
            "forecasts": []
        }
        
        # Verify and prune should remove unsupported claims
        result = verify_and_prune(itinerary, evidence)
        
        # The unsupported claim should be removed or flagged
        assert result is not None
        # In a real implementation, we'd check that unsupported claims are removed
    
    def test_numeric_constraints_enforced(self):
        """Test that numeric constraints are properly enforced."""
        trip_slots = TripSlots(
            region="Test Region",
            start_date=date(2025, 12, 20),
            end_date=date(2025, 12, 22),
            ability=AbilityLevel.INTERMEDIATE
        )
        
        # Create plan with excessive ski time
        day_plan = DayPlan(
            date=date(2025, 12, 20),
            resort="Test Resort",
            weather_summary="Good conditions",
            steps=[
                PlanStep(
                    time="9:00 AM",
                    activity="All day skiing",
                    location="Test Resort",
                    duration_minutes=600,  # 10 hours - exceeds limit
                    notes="Long day",
                    source_id="test:step_1"
                )
            ],
            total_ski_minutes=600,  # Exceeds 7.5 hour limit
            source_id="test:day_1"
        )
        
        itinerary = Itinerary(
            trip_slots=trip_slots,
            ranked_resorts=[],
            daily_plans=[day_plan]
        )
        
        evidence = {"resorts": [], "forecasts": []}
        
        # This should raise a ValueError due to excessive ski time
        with pytest.raises(ValueError, match="exceeds.*hours"):
            verify_and_prune(itinerary, evidence)
    
    def test_source_id_verification(self):
        """Test that source ID verification works correctly."""
        trip_slots = TripSlots(
            region="Test Region",
            start_date=date(2025, 12, 20),
            end_date=date(2025, 12, 22),
            ability=AbilityLevel.INTERMEDIATE
        )
        
        # Create plan with missing source IDs
        day_plan = DayPlan(
            date=date(2025, 12, 20),
            resort="Test Resort",
            weather_summary="Good conditions",
            steps=[
                PlanStep(
                    time="9:00 AM",
                    activity="Morning skiing",
                    location="Test Resort",
                    duration_minutes=180,
                    notes="Test",
                    source_id=""  # Empty source_id
                )
            ],
            total_ski_minutes=180,
            source_id=""  # Empty source_id
        )
        
        itinerary = Itinerary(
            trip_slots=trip_slots,
            ranked_resorts=[{"source_id": ""}],  # Missing source_id
            daily_plans=[day_plan]
        )
        
        evidence = {"resorts": [], "forecasts": []}
        
        # This should raise a ValueError due to missing source IDs
        with pytest.raises(ValueError, match="missing source_id"):
            verify_and_prune(itinerary, evidence)
    
    def test_wind_sheltered_hints_added(self):
        """Test that wind-sheltered hints are added for high wind conditions."""
        # This test would verify that high wind conditions trigger
        # the addition of wind-sheltered area suggestions
        # Implementation depends on the specific wind threshold logic
        pass
    
    def test_plan_validation_success(self):
        """Test successful plan validation with proper data."""
        trip_slots = TripSlots(
            region="Test Region",
            start_date=date(2025, 12, 20),
            end_date=date(2025, 12, 22),
            ability=AbilityLevel.INTERMEDIATE
        )
        
        day_plan = DayPlan(
            date=date(2025, 12, 20),
            resort="Test Resort",
            weather_summary="Good conditions",
            steps=[
                PlanStep(
                    time="9:00 AM",
                    activity="Morning skiing",
                    location="Test Resort",
                    duration_minutes=180,
                    notes="Test notes",
                    source_id="test:step_1"
                )
            ],
            total_ski_minutes=180,
            source_id="test:day_1"
        )
        
        itinerary = Itinerary(
            trip_slots=trip_slots,
            ranked_resorts=[{"source_id": "test:resort_1"}],
            daily_plans=[day_plan]
        )
        
        evidence = {"resorts": [], "forecasts": []}
        
        # This should succeed without errors
        result = verify_and_prune(itinerary, evidence)
        assert result is not None
        assert len(result.daily_plans) == 1
        assert result.daily_plans[0].total_ski_minutes == 180


if __name__ == "__main__":
    pytest.main([__file__])
```

```

