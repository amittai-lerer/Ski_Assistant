"""Geoapify API integration for finding ski resorts."""

import os
import httpx
from typing import Optional, Dict, List, Any

async def _geocode(city: str) -> Optional[tuple]:
    """Geocode a city name to coordinates."""
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("https://geocoding-api.open-meteo.com/v1/search",
                                params={"name": city, "count": 1, "language": "en"}, timeout=20)
            items = (r.json().get("results") or [])
            if not items:
                return None
            it = items[0]
            return float(it["latitude"]), float(it["longitude"]), f"{it['name']}, {it.get('country_code','')}"
    except Exception as e:
        # Use logging instead of print for production code
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Geocoding error for '{city}': {e}")
        return None

async def find_resorts_geoapify(city: str = None, lat: float = None, lon: float = None,
                          radius_km: float = None, limit: int = 8) -> Dict[str, Any]:
    """Find ski resorts near a location using Geoapify API."""
    key = os.getenv("GEOAPIFY_API_KEY")
    if not key:
        return {"error": "missing_geoapify_key"}

    if city and (lat is None or lon is None):
        # Use the city/country name directly - let the geocoding service handle it
        # The LLM will provide appropriate city names for countries when needed
        g = await _geocode(city)
        if not g:
            return {"error": "could_not_geocode", "city": city}
        lat, lon, label = g

        search_radius = radius_km if radius_km is not None else 50
    else:
        label = city or "selected area"
        search_radius = radius_km if radius_km is not None else 50

    try:
        async with httpx.AsyncClient() as client:
            # Use broader sport category with ski-specific keywords (ski_resort category doesn't exist)
            r = await client.get("https://api.geoapify.com/v2/places",
                params={
                    "categories": "sport",
                    "text": "ski resort OR alpine OR winter sport OR snow OR piste OR ski lift",
                    "filter": f"circle:{lon},{lat},{int(search_radius*1000)}",
                    "limit": limit,
                    "apiKey": key
                }, timeout=30)

            if r.status_code == 401:
                return {"error": "geoapify_unauthorized"}
            r.raise_for_status()

            feats = r.json().get("features", [])
            out = []

            # Process results (Geoapify already filters by sport category and ski keywords)
            for f in feats:
                props = f.get("properties", {})
                name = props.get("name") or ""
                formatted = props.get("formatted") or ""

                # Additional filtering for ski-related places
                ski_keywords = [
                    "ski", "alpine", "snow", "mountain", "resort", "winter", "sport",
                    "piste", "lift", "gondola", "chairlift", "telecabin", "seilbahn", "bergbahn",
                    "schnee", "berg", "alpen", "skiparadies", "skigebiet", "wintersport", "snowboard"
                ]
                text_to_check = (name + " " + formatted).lower()
                is_ski_related = any(keyword.lower() in text_to_check for keyword in ski_keywords)

                if is_ski_related:
                    geom = f.get("geometry", {})
                    coords = (geom.get("coordinates") or [None, None])
                    out.append({
                        "name": name,
                        "address": props.get("formatted"),
                        "lat": coords[1],
                        "lon": coords[0],
                        "datasource": props.get("datasource", {}).get("raw", {}).get("website") or props.get("website")
                    })

            # If no ski-specific results, return some general activity places as fallback
            if not out and feats:
                import logging
                logger = logging.getLogger(__name__)
                logger.info("No ski-specific results found, showing general activities")
                for f in feats[:2]:  # Show first 2 as general activities
                    props = f.get("properties", {})
                    geom = f.get("geometry", {})
                    coords = (geom.get("coordinates") or [None, None])
                    out.append({
                        "name": props.get("name") or "Local activity center",
                        "address": props.get("formatted"),
                        "lat": coords[1],
                        "lon": coords[0],
                        "datasource": props.get("datasource", {}).get("raw", {}).get("website") or props.get("website")
                    })

            # If we have no results at all, provide a helpful fallback
            if not out:
                return {"area": label, "resorts": [], "fallback": True}

            return {"area": label, "resorts": out}

    except httpx.RequestError as e:
        return {"error": f"api_request_failed", "details": str(e), "fallback": True}
    except Exception as e:
        return {"error": f"unexpected_error", "details": str(e), "fallback": True}
