"""
SkiAPI integration for detailed ski resort information.

This module provides access to the SkiAPI (skiapi.com) database which contains
comprehensive information about ski resorts worldwide including lift counts,
trail information, snow conditions, and resort details.

Uses RapidAPI for authentication and access.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

import httpx
from core.config import RAPIDAPI_KEY, TIMEOUT_S

logger = logging.getLogger(__name__)

# SkiAPI endpoints
SKIAPI_BASE_URL = "https://ski-resorts-and-conditions.p.rapidapi.com"
SKIAPI_HOST = "ski-resorts-and-conditions.p.rapidapi.com"

# Request headers for RapidAPI
HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": SKIAPI_HOST,
    "Content-Type": "application/json"
}


async def _make_request(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Make a request to SkiAPI with proper error handling.

    Args:
        endpoint: API endpoint (without base URL)
        params: Query parameters

    Returns:
        JSON response data

    Raises:
        httpx.HTTPStatusError: For HTTP error responses
        Exception: For other errors
    """
    if not RAPIDAPI_KEY:
        return {"error": "missing_rapidapi_key"}

    url = f"{SKIAPI_BASE_URL}{endpoint}"

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_S) as client:
            response = await client.get(url, headers=HEADERS, params=params or {})
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"SkiAPI HTTP error: {e.response.status_code} - {e.response.text}")

        # Handle specific HTTP status codes with informative messages
        if e.response.status_code == 429:
            return {
                "error": "rate_limit_exceeded",
                "message": "SkiAPI daily request limit exceeded. Your free tier allows limited requests per day.",
                "solution": "Wait until tomorrow for the limit to reset, or upgrade to a paid plan for higher limits.",
                "details": "This is normal for free API tiers. The assistant will use general ski knowledge instead."
            }
        elif e.response.status_code == 401:
            return {
                "error": "authentication_failed",
                "message": "SkiAPI authentication failed. Please check your RAPIDAPI_KEY.",
                "solution": "Verify your RAPIDAPI_KEY in the .env file or regenerate it on RapidAPI.",
                "details": e.response.text
            }
        elif e.response.status_code == 403:
            return {
                "error": "subscription_required",
                "message": "SkiAPI subscription required or expired.",
                "solution": "Subscribe to SkiAPI on RapidAPI or renew your subscription.",
                "details": e.response.text
            }
        else:
            return {"error": f"http_{e.response.status_code}", "details": e.response.text}
    except Exception as e:
        logger.error(f"SkiAPI request failed: {e}")
        return {"error": "request_failed", "details": str(e)}


async def search_resorts(query: str = "", country: str = "", region: str = "",
                        page: int = 1, per_page: int = 10) -> Dict[str, Any]:
    """
    Search for ski resorts using SkiAPI.

    Args:
        query: Search query (resort name)
        country: Country code (e.g., "US", "CA", "FR")
        region: Region/state code (e.g., "CO", "BC", "CA")
        page: Page number for pagination
        per_page: Results per page (max 25)

    Returns:
        Dictionary containing search results or error
    """
    params = {
        "page": page,
        "per_page": min(per_page, 25)  # API limit is 25
    }

    if query:
        params["q"] = query
    if country:
        params["country"] = country.upper()
    if region:
        params["region"] = region.upper()

    result = await _make_request("/v1/resort", params)

    if "error" in result:
        return result

    # Process and format the results
    resorts = []
    for resort in result.get("data", []):
        resorts.append({
            "name": resort.get("name", "Unknown Resort"),
            "slug": resort.get("slug", ""),
            "country": resort.get("country", ""),
            "region": resort.get("region", ""),
            "latitude": resort.get("location", {}).get("latitude"),
            "longitude": resort.get("location", {}).get("longitude"),
            "api_url": resort.get("url", "")
        })

    return {
        "resorts": resorts,
        "total": result.get("total", 0),
        "total_pages": result.get("total_pages", 0),
        "current_page": result.get("page", page),
        "per_page": result.get("per_page", per_page)
    }


async def get_resort_details(slug: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific ski resort.

    Args:
        slug: Resort slug from search results

    Returns:
        Detailed resort information or error
    """
    if not slug:
        return {"error": "missing_resort_slug"}

    result = await _make_request(f"/v1/resort/{slug}")

    if "error" in result:
        return result

    # The detailed endpoint might return different structure
    # This is a placeholder - we'd need to see the actual API response
    # to properly format the detailed information
    return {
        "name": result.get("name", "Unknown Resort"),
        "details": result,
        "last_updated": datetime.now().isoformat()
    }


async def get_resort_snow_report(slug: str) -> Dict[str, Any]:
    """
    Get snow report for a specific resort.

    Args:
        slug: Resort slug

    Returns:
        Snow conditions or error
    """
    if not slug:
        return {"error": "missing_resort_slug"}

    result = await _make_request(f"/v1/resort/{slug}/snow")

    if "error" in result:
        return result

    return {
        "resort_slug": slug,
        "snow_conditions": result,
        "last_updated": datetime.now().isoformat()
    }


# Main integration function for the LLM tool
async def get_ski_resort_details(resort_name: str = "", country: str = "",
                                include_snow_report: bool = False) -> Dict[str, Any]:
    """
    Main function for LLM tool integration.
    Get detailed ski resort information by name and/or country.

    Args:
        resort_name: Name of the ski resort
        country: Country code (optional)
        include_snow_report: Whether to include snow conditions

    Returns:
        Resort details with optional snow report
    """
    try:
        # First, search for the resort
        search_result = await search_resorts(query=resort_name, country=country, per_page=5)

        if "error" in search_result:
            return {
                "error": search_result["error"],
                "fallback": True
            }

        resorts = search_result.get("resorts", [])

        if not resorts:
            return {
                "error": "no_resorts_found",
                "query": resort_name,
                "country": country,
                "fallback": True
            }

        # Get the best match (first result)
        resort = resorts[0]
        slug = resort.get("slug")

        result = {
            "resort_name": resort.get("name"),
            "country": resort.get("country"),
            "region": resort.get("region"),
            "location": {
                "latitude": resort.get("latitude"),
                "longitude": resort.get("longitude")
            },
            "api_url": resort.get("api_url")
        }

        # Note: Snow report endpoint may not be available in this API
        # Optionally get snow report (commented out to avoid 404 errors)
        # if include_snow_report and slug:
        #     snow_result = await get_resort_snow_report(slug)
        #     if "error" not in snow_result:
        #         result["snow_report"] = snow_result.get("snow_conditions")

        return result

    except Exception as e:
        logger.error(f"Error in get_ski_resort_details: {e}")
        return {
            "error": "integration_error",
            "details": str(e),
            "fallback": True
        }
