"""Unit tests for deterministic scoring and ranking.

This module tests the scoring system to ensure it produces consistent,
deterministic results based on weather data. Tests verify that resorts
are ranked correctly according to skiing conditions.
"""

import pytest
from datetime import date

from models.schemas import Resort, ForecastDay
from ranking.scorer import normalize, compute_features, score, rank


class TestScorer:
    """Test suite for scoring and ranking functionality."""
    
    def test_normalize_function(self):
        """Test the normalize function with various inputs."""
        # Test normal case
        assert normalize(15, 0, 30) == 0.5
        
        # Test edge cases
        assert normalize(0, 0, 30) == 0.0
        assert normalize(30, 0, 30) == 1.0
        
        # Test values outside range
        assert normalize(-5, 0, 30) == 0.0  # Clamped to 0
        assert normalize(35, 0, 30) == 1.0  # Clamped to 1
        
        # Test equal min/max
        assert normalize(10, 10, 10) == 0.5
    
    def test_compute_features(self):
        """Test feature computation from forecast data."""
        # Create test forecast data
        forecast_days = [
            ForecastDay(
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
            ),
            ForecastDay(
                date=date(2025, 12, 21),
                latitude=39.1,
                longitude=-120.0,
                max_temp_c=0.0,
                min_temp_c=-8.0,
                precipitation_mm=8.0,
                snowfall_mm=15.0,
                wind_speed_kph=20.0,
                wind_direction_deg=200.0,
                freezing_level_m=1200.0,
                source_id="test:forecast_2"
            )
        ]
        
        features = compute_features(forecast_days)
        
        # Check computed values
        assert features["new_snow"] == 25.0  # 10 + 15
        assert features["wind_speed"] == 17.5  # (15 + 20) / 2
        assert features["freezing_level"] == 1350.0  # (1500 + 1200) / 2
        assert features["temperature"] > 0  # Should be positive for comfort
    
    def test_compute_features_empty_list(self):
        """Test feature computation with empty forecast list."""
        features = compute_features([])
        
        # Should return default values
        assert features["new_snow"] == 0.0
        assert features["wind_speed"] == 0.5
        assert features["freezing_level"] == 0.5
        assert features["temperature"] == 0.5
    
    def test_score_calculation(self):
        """Test score calculation with known inputs."""
        features = {
            "new_snow": 20.0,      # Good snow
            "wind_speed": 10.0,    # Low wind
            "freezing_level": 1500.0,  # Moderate freezing level
            "temperature": 0.8     # Good temperature comfort
        }
        
        calculated_score = score(features)
        
        # Score should be between 0 and 1
        assert 0.0 <= calculated_score <= 1.0
        
        # With good conditions, score should be relatively high
        assert calculated_score > 0.6
    
    def test_score_with_custom_weights(self):
        """Test score calculation with custom weights."""
        features = {
            "new_snow": 30.0,
            "wind_speed": 5.0,
            "freezing_level": 1000.0,
            "temperature": 0.9
        }
        
        # Custom weights emphasizing snow
        custom_weights = {
            "new_snow": 0.7,
            "wind_speed": 0.1,
            "freezing_level": 0.1,
            "temperature": 0.1
        }
        
        score_default = score(features)
        score_custom = score(features, custom_weights)
        
        # Custom score should be different from default
        assert score_custom != score_default
        
        # With high snow emphasis, custom score should be higher
        assert score_custom > score_default
    
    def test_rank_resorts_deterministic(self):
        """Test that resort ranking is deterministic and correct."""
        # Create test resorts
        resort1 = Resort(
            name="Resort A",
            address="Address A",
            latitude=39.1,
            longitude=-120.0,
            category="Ski Resort",
            source_id="test:resort_a"
        )
        
        resort2 = Resort(
            name="Resort B", 
            address="Address B",
            latitude=39.2,
            longitude=-120.1,
            category="Ski Resort",
            source_id="test:resort_b"
        )
        
        # Create forecasts with different conditions
        forecast_a = [
            ForecastDay(
                date=date(2025, 12, 20),
                latitude=39.1,
                longitude=-120.0,
                max_temp_c=0.0,
                min_temp_c=-5.0,
                precipitation_mm=10.0,
                snowfall_mm=20.0,  # More snow
                wind_speed_kph=5.0,  # Less wind
                wind_direction_deg=180.0,
                freezing_level_m=1000.0,  # Lower freezing level
                source_id="test:forecast_a"
            )
        ]
        
        forecast_b = [
            ForecastDay(
                date=date(2025, 12, 20),
                latitude=39.2,
                longitude=-120.1,
                max_temp_c=5.0,
                min_temp_c=-2.0,
                precipitation_mm=5.0,
                snowfall_mm=5.0,   # Less snow
                wind_speed_kph=25.0,  # More wind
                wind_direction_deg=200.0,
                freezing_level_m=2000.0,  # Higher freezing level
                source_id="test:forecast_b"
            )
        ]
        
        forecasts_by_resort = {
            "test:resort_a": forecast_a,
            "test:resort_b": forecast_b
        }
        
        # Rank resorts
        rankings = rank([resort1, resort2], forecasts_by_resort)
        
        # Should have 2 rankings
        assert len(rankings) == 2
        
        # Resort A should rank higher (better conditions)
        top_resort, top_score, top_reasons = rankings[0]
        assert top_resort.name == "Resort A"
        assert top_score > 0.5  # Should be a good score
        
        # Resort B should rank lower
        second_resort, second_score, second_reasons = rankings[1]
        assert second_resort.name == "Resort B"
        assert second_score < top_score
        
        # Reasons should be provided
        assert len(top_reasons) > 0
        assert len(second_reasons) > 0
    
    def test_rank_resorts_no_forecast(self):
        """Test ranking when some resorts have no forecast data."""
        resort1 = Resort(
            name="Resort A",
            address="Address A",
            latitude=39.1,
            longitude=-120.0,
            category="Ski Resort",
            source_id="test:resort_a"
        )
        
        resort2 = Resort(
            name="Resort B",
            address="Address B", 
            latitude=39.2,
            longitude=-120.1,
            category="Ski Resort",
            source_id="test:resort_b"
        )
        
        # Only provide forecast for one resort
        forecasts_by_resort = {
            "test:resort_a": [
                ForecastDay(
                    date=date(2025, 12, 20),
                    latitude=39.1,
                    longitude=-120.0,
                    max_temp_c=0.0,
                    min_temp_c=-5.0,
                    precipitation_mm=10.0,
                    snowfall_mm=15.0,
                    wind_speed_kph=10.0,
                    wind_direction_deg=180.0,
                    freezing_level_m=1500.0,
                    source_id="test:forecast_a"
                )
            ]
            # No forecast for resort_b
        }
        
        rankings = rank([resort1, resort2], forecasts_by_resort)
        
        # Should still rank both resorts
        assert len(rankings) == 2
        
        # Resort A should rank higher (has forecast data)
        top_resort, top_score, top_reasons = rankings[0]
        assert top_resort.name == "Resort A"
        
        # Resort B should have default score
        second_resort, second_score, second_reasons = rankings[1]
        assert second_resort.name == "Resort B"
        assert second_score == 0.5  # Default score
        assert "No forecast data available" in second_reasons
    
    def test_rank_empty_resort_list(self):
        """Test ranking with empty resort list."""
        rankings = rank([], {})
        assert len(rankings) == 0


if __name__ == "__main__":
    pytest.main([__file__])
```

```

