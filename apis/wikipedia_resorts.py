"""
Wikipedia API integration for ski resort information.

This module provides access to Wikipedia summaries for ski resorts
using the MediaWiki Action API.
"""

import logging
from typing import Optional, Dict, Any

import httpx
from core.config import TIMEOUT_S

logger = logging.getLogger(__name__)

# Wikipedia API endpoint
WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"


async def get_resort_wikipedia_summary(resort_name: str) -> Dict[str, Any]:
    """
    Get Wikipedia summary for a ski resort.

    Args:
        resort_name: Name of the ski resort

    Returns:
        Dictionary with summary or error information
    """
    if not resort_name:
        return {"error": "missing_resort_name"}

    try:
        # Clean up resort name for Wikipedia search
        # Remove common ski resort suffixes and clean formatting
        clean_name = resort_name.strip()
        clean_name = clean_name.replace(" ski resort", "").replace(" Ski Resort", "")
        clean_name = clean_name.replace(" ski area", "").replace(" Ski Area", "")

        params = {
            "action": "query",
            "prop": "extracts",
            "exintro": True,  # Only get intro section
            "explaintext": True,  # Return plain text, not HTML
            "titles": clean_name,
            "format": "json"
        }

        async with httpx.AsyncClient(timeout=TIMEOUT_S) as client:
            response = await client.get(WIKIPEDIA_API_URL, params=params)
            response.raise_for_status()
            data = response.json()

        # Parse the Wikipedia response
        pages = data.get("query", {}).get("pages", {})

        # Get the first page (should only be one)
        page_id = list(pages.keys())[0]
        page = pages[page_id]

        # Check if page exists
        if page_id == "-1" or not page.get("extract"):
            return {
                "error": "no_wikipedia_page",
                "resort_name": resort_name,
                "message": f"No Wikipedia page found for '{resort_name}'"
            }

        # Extract the summary
        summary = page.get("extract", "").strip()

        # Clean up the summary (remove excessive whitespace)
        summary = " ".join(summary.split())

        return {
            "resort_name": resort_name,
            "wikipedia_title": page.get("title", ""),
            "summary": summary,
            "page_url": f"https://en.wikipedia.org/wiki/{page.get('title', '').replace(' ', '_')}",
            "success": True
        }

    except httpx.HTTPStatusError as e:
        logger.error(f"Wikipedia API HTTP error: {e.response.status_code}")
        return {
            "error": "wikipedia_api_error",
            "status_code": e.response.status_code,
            "message": f"Wikipedia API error: {e.response.status_code}"
        }
    except Exception as e:
        logger.error(f"Wikipedia API request failed: {e}")
        return {
            "error": "request_failed",
            "message": f"Failed to fetch Wikipedia data: {str(e)}"
        }


async def search_wikipedia_resort_info(resort_name: str = "", country: str = "") -> Dict[str, Any]:
    """
    Main function for Wikipedia tool integration.
    Search for ski resort information on Wikipedia.

    Args:
        resort_name: Name of the ski resort
        country: Optional country for context

    Returns:
        Resort information from Wikipedia or error
    """
    try:
        result = await get_resort_wikipedia_summary(resort_name)

        if result.get("error") == "no_wikipedia_page":
            # Try alternative search terms if the first attempt fails
            alternatives = []

            # Try with "ski resort" suffix
            if not resort_name.lower().endswith("ski resort"):
                alternatives.append(f"{resort_name} ski resort")

            # Try with country context if provided
            if country and country.lower() != "us":
                if country.lower() == "canada" or country.lower() == "ca":
                    alternatives.append(f"{resort_name} ski area")
                else:
                    alternatives.append(f"{resort_name} {country}")

            # Try alternatives
            for alt_name in alternatives:
                alt_result = await get_resort_wikipedia_summary(alt_name)
                if alt_result.get("success"):
                    return alt_result

            # If no alternatives work, return the original error
            return result

        return result

    except Exception as e:
        logger.error(f"Error in search_wikipedia_resort_info: {e}")
        return {
            "error": "integration_error",
            "message": f"Wikipedia integration error: {str(e)}"
        }
