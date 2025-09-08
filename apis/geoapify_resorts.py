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
        print(f"Geocoding error: {e}")
        return None

async def find_resorts_geoapify(city: str = None, lat: float = None, lon: float = None,
                          radius_km: float = 50, limit: int = 8) -> Dict[str, Any]:
    """Find ski resorts near a location using Geoapify API."""
    key = os.getenv("GEOAPIFY_API_KEY")
    if not key:
        return {"error": "missing_geoapify_key"}

    if city and (lat is None or lon is None):
        # Handle country searches by using major cities instead
        country_cities = {
            "canada": "Whistler",
            "usa": "Lake Tahoe",
            "united states": "Lake Tahoe",
            "america": "Lake Tahoe",
            "france": "Chamonix",
            "switzerland": "Zermatt",
            "italy": "Cortina d'Ampezzo",
            "austria": "Innsbruck"
        }

        search_city = country_cities.get(city.lower(), city)

        g = await _geocode(search_city)
        if not g:
            return {"error": "could_not_geocode", "city": city}
        lat, lon, label = g
    else:
        label = city or "selected area"

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("https://api.geoapify.com/v2/places",
                params={
                    "categories": "activity",
                    "text": "ski",
                    "filter": f"circle:{lon},{lat},{int(radius_km*1000)}",
                    "limit": limit,
                    "apiKey": key
                }, timeout=30)

            if r.status_code == 401:
                return {"error": "geoapify_unauthorized"}
            r.raise_for_status()

            feats = r.json().get("features", [])
            out = []

            # Filter and process results
            for f in feats:
                props = f.get("properties", {})
                name = props.get("name") or ""
                formatted = props.get("formatted") or ""

                # Filter for ski-related places (improved heuristic)
                ski_keywords = ["ski", "alpine", "snow", "mountain", "resort", "winter", "sport", "club", "center", "fitness"]
                text_to_check = (name + " " + formatted).lower()
                if any(keyword.lower() in text_to_check for keyword in ski_keywords):
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
                print("⚠️  No ski-specific results found, showing general activities")
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
