from __future__ import annotations
"""
Centralized settings loader for SkiTrip Assistant.

Only environment variables and simple flags live here.
NO data models or business logic should be defined in this module.
"""

import os
from dotenv import load_dotenv

# Load .env from project root
load_dotenv()

# -------------------------
# Core env configuration
# -------------------------
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
GEOAPIFY_API_KEY: str = os.getenv("GEOAPIFY_API_KEY", "")
RAPIDAPI_KEY: str = os.getenv("RAPIDAPI_KEY", "")

OPEN_METEO_BASE: str = os.getenv("OPEN_METEO_BASE", "https://api.open-meteo.com/v1/forecast")

TIMEOUT_S: float = float(os.getenv("TIMEOUT_S", "15"))
ENV: str = os.getenv("ENV", "dev")  # "dev" or "prod"

# LLM configuration
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))
LLM_MAX_RETRIES: int = int(os.getenv("LLM_MAX_RETRIES", "2"))

# -------------------------
# App/domain defaults
# (override in .env if needed)
# -------------------------
MAX_RESORTS: int = int(os.getenv("MAX_RESORTS", "8"))
MAX_SKI_HOURS_PER_DAY: float = float(os.getenv("MAX_SKI_HOURS_PER_DAY", "7.5"))
WIND_THRESHOLD_KPH: float = float(os.getenv("WIND_THRESHOLD_KPH", "60.0"))

# A simple DEBUG flag that some modules expect
def is_dev() -> bool:
    return (ENV or "dev").lower() == "dev"

def is_prod() -> bool:
    return (ENV or "dev").lower() == "prod"

DEBUG: bool = (os.getenv("DEBUG", "0") == "1") or is_dev()

# Feature flags (keep real external calls off by default in dev)
USE_REAL_OPENAI: bool = os.getenv("USE_REAL_OPENAI", "0") == "1"  # Allow in dev for testing
# Open-Meteo is free; okay to use in dev. Set to "0" in .env to force stub.
USE_REAL_OPEN_METEO: bool = os.getenv("USE_REAL_OPEN_METEO", "1") == "1"

def require(key: str, value: str) -> str:
    """Ensure a required setting is present; raise with a friendly message otherwise."""
    if not value:
        raise RuntimeError(f"Missing required setting: {key}. Put it in your .env")
    return value

# Safety checks when running in prod
if is_prod():
    require("OPENAI_API_KEY", OPENAI_API_KEY)
    # FOURSQUARE_API_KEY is now optional since we use Geoapify for resorts
    # require("FOURSQUARE_API_KEY", FOURSQUARE_API_KEY)

__all__ = [
    "OPENAI_API_KEY", "GEOAPIFY_API_KEY", "RAPIDAPI_KEY",
    "OPEN_METEO_BASE",
    "TIMEOUT_S", "ENV", "OPENAI_MODEL",
    "LLM_TEMPERATURE", "LLM_MAX_RETRIES",
    "MAX_RESORTS", "MAX_SKI_HOURS_PER_DAY", "WIND_THRESHOLD_KPH",
    "DEBUG", "USE_REAL_OPENAI", "USE_REAL_OPEN_METEO",
    "is_dev", "is_prod",
]
