"""
Configuration Management - Clean Configuration Pattern

Demonstrates professional practices:
- Centralized configuration management
- Environment-specific settings
- Type-safe configuration values
- Clear separation of concerns
- Easy to modify without code changes

Interview Notes:
- Shows understanding of configuration management
- Demonstrates 12-factor app principles
- Clean separation of config from business logic
- Easy to test with different configurations
"""

import os
from typing import Dict, Any, List

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, continue without it
    pass

# ============================================================================
# Environment Variable Loading
# ============================================================================

def _get_env_var(name: str, default: str = "") -> str:
    """Get environment variable with optional default."""
    return os.getenv(name, default)

# API Keys (loaded from environment variables)
OPENAI_API_KEY = _get_env_var("OPENAI_API_KEY")
GEOAPIFY_API_KEY = _get_env_var("GEOAPIFY_API_KEY")
RAPIDAPI_KEY = _get_env_var("RAPIDAPI_KEY")

# Validate required API keys (allow dummy values for testing)
def _validate_api_key(key: str, name: str) -> None:
    """Validate API key is not empty and not obviously dummy."""
    if not key or key.strip() == "":
        raise ValueError(f"{name} environment variable is required")
    if key.startswith("sk-your-") or key.startswith("your-") or key.startswith("dummy"):
        # Allow dummy keys for testing, but warn
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Using dummy {name} - replace with real API key for production")

_validate_api_key(OPENAI_API_KEY, "OPENAI_API_KEY")
_validate_api_key(GEOAPIFY_API_KEY, "GEOAPIFY_API_KEY")
_validate_api_key(RAPIDAPI_KEY, "RAPIDAPI_KEY")

# ============================================================================
# LLM Configuration
# ============================================================================

MODEL_NAME = "gpt-4o-mini"
"""
Primary LLM model for all reasoning tasks.

Interview Notes:
- Shows understanding of model selection criteria
- Easy to change for different use cases
- Centralized for consistency
"""

# Temperature settings for different reasoning phases
TEMPERATURE_CHAIN_OF_THOUGHT = 0.2  # Balanced reasoning for trip planning
TEMPERATURE_EVIDENCE_ONLY = 0.1     # Allow structured planning while staying factual
TEMPERATURE_VERIFY = 0.05           # Strict verification and conciseness

MAX_RETRIES = 2                    # Reasonable retry limit for API calls

# ============================================================================
# Tool Strategy Configuration
# ============================================================================

TOOL_PRIORITIES: Dict[str, List[str]] = {
    "resort_info": ["wikipedia", "skiapi"],    # Wikipedia primary, SkiAPI fallback
    "location_search": ["geoapify"],           # Geoapify for location discovery
    "weather": ["openmeteo"]                   # Open-Meteo for weather data
}
"""
Tool prioritization strategy for different query types.

Interview Notes:
- Shows understanding of business logic rules
- Easy to modify strategy without code changes
- Clear fallback mechanisms
- Prevents hard-coded logic in business code
"""

# ============================================================================
# Default Parameters
# ============================================================================

DEFAULT_RADIUS_KM = 50
"""Default search radius for location-based queries."""

DEFAULT_LIMIT = 8
"""Default result limit for tool responses."""

# ============================================================================
# Feature Flags (for A/B testing or gradual rollouts)
# ============================================================================

ENABLE_ADVANCED_LOGGING = False
"""Enable detailed logging for debugging (set to False in production)."""

ENABLE_TOOL_FALLBACKS = True
"""Enable automatic fallback to alternative tools when primary fails."""

# ============================================================================
# Timeout Configuration
# ============================================================================

TIMEOUT_S = 30
"""Default timeout for API requests in seconds."""
