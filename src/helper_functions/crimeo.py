"""Crimeometer API Helper Functions.

Direct access to Crimeometer API for crime data.
Used by the orchestrator to enrich route waypoints with crime data.

Environment Variables Required:
    CRIME_API_KEY: Your Crimeometer API key
    CRIME_API_BASE_URL: API base URL (default: https://api.crimeometer.com/v1)

Usage:
    from src.helper_functions.crimeo import get_crime_incidents

    crime_data = await get_crime_incidents(latitude=41.8781, longitude=-87.6298)
"""
import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
CRIME_API_KEY = os.getenv("CRIME_API_KEY")
CRIME_API_BASE_URL = os.getenv("CRIME_API_BASE_URL", "https://api.crimeometer.com/v1")

# Hardcoded defaults - these are NOT parameters
RADIUS_MILES = 0.25
DAYS_BACK = 14
LIMIT = 5

# Logging
logger = logging.getLogger(__name__)


# =============================================================================
# DATE RANGE HELPER
# =============================================================================

def get_date_range(days_back: int = DAYS_BACK) -> tuple[str, str]:
    """
    Compute datetime_ini and datetime_end for Crimeometer queries.

    Args:
        days_back: Number of days to look back (default: 14)

    Returns:
        Tuple of (datetime_ini, datetime_end) formatted as yyyy-MM-ddT00:00:00.000Z
    """
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=days_back)

    fmt = "%Y-%m-%dT00:00:00.000Z"
    return start.strftime(fmt), now.strftime(fmt)


# =============================================================================
# CRIME STATS FUNCTION
# =============================================================================

async def get_crime_stats(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Get crime statistics for a location from Crimeometer.

    Uses hardcoded defaults:
        - radius: 0.25 miles
        - days_back: 14 days

    Args:
        latitude: GPS latitude
        longitude: GPS longitude

    Returns:
        Dict with total_incidents, report_types, and location.
        On error, returns dict with "error" key.
    """
    if not CRIME_API_KEY:
        return {"error": "CRIME_API_KEY not set", "location": {"lat": latitude, "lon": longitude}}

    datetime_ini, datetime_end = get_date_range(DAYS_BACK)

    url = f"{CRIME_API_BASE_URL}/incidents/stats"
    params = {
        "lat": latitude,
        "lon": longitude,
        "distance": f"{RADIUS_MILES}mi",
        "datetime_ini": datetime_ini,
        "datetime_end": datetime_end,
    }
    headers = {
        "Content-Type": "application/json",
        "x-api-key": CRIME_API_KEY,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params, headers=headers)

            if response.status_code == 429:
                return {
                    "error": "Rate limit exceeded",
                    "status_code": 429,
                    "location": {"lat": latitude, "lon": longitude},
                }

            response.raise_for_status()
            data = response.json()

            # Crimeometer returns a list with one element
            if isinstance(data, list) and len(data) > 0:
                result = data[0]
                return {
                    "total_incidents": result.get("total_incidents", 0),
                    "report_types": result.get("report_types", []),
                    "location": {"lat": latitude, "lon": longitude},
                }

            return {
                "total_incidents": 0,
                "report_types": [],
                "location": {"lat": latitude, "lon": longitude},
            }

    except httpx.HTTPStatusError as e:
        logger.error(f"Crime stats HTTP error: {e.response.status_code}")
        return {
            "error": f"HTTP {e.response.status_code}",
            "location": {"lat": latitude, "lon": longitude},
        }
    except Exception as e:
        logger.error(f"Crime stats error: {e}")
        return {
            "error": str(e),
            "location": {"lat": latitude, "lon": longitude},
        }


# =============================================================================
# CRIME INCIDENTS FUNCTION
# =============================================================================

async def get_crime_incidents(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Get crime incident data for a location from Crimeometer.

    Uses hardcoded defaults:
        - radius: 0.25 miles
        - days_back: 14 days
        - limit: 5 incidents

    Args:
        latitude: GPS latitude
        longitude: GPS longitude

    Returns:
        Dict with incidents list, total_incidents, and location.
        On error, returns dict with "error" key.
    """
    if not CRIME_API_KEY:
        return {"error": "CRIME_API_KEY not set", "location": {"lat": latitude, "lon": longitude}}

    datetime_ini, datetime_end = get_date_range(DAYS_BACK)

    url = f"{CRIME_API_BASE_URL}/incidents/raw-data"
    params = {
        "lat": latitude,
        "lon": longitude,
        "distance": f"{RADIUS_MILES}mi",
        "datetime_ini": datetime_ini,
        "datetime_end": datetime_end,
        "page": 1,
    }
    headers = {
        "Content-Type": "application/json",
        "x-api-key": CRIME_API_KEY,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params, headers=headers)

            if response.status_code == 429:
                return {
                    "error": "Rate limit exceeded",
                    "status_code": 429,
                    "incidents": [],
                    "total_incidents": 0,
                    "location": {"lat": latitude, "lon": longitude},
                }

            response.raise_for_status()
            data = response.json()

            # Crimeometer returns a list with one element
            if isinstance(data, list) and len(data) > 0:
                result = data[0]
                incidents = result.get("incidents", [])

                # Apply limit
                limited_incidents = incidents[:LIMIT]

                return {
                    "total_incidents": result.get("total_incidents", 0),
                    "incidents": limited_incidents,
                    "incidents_returned": len(limited_incidents),
                    "location": {"lat": latitude, "lon": longitude},
                }

            return {
                "total_incidents": 0,
                "incidents": [],
                "incidents_returned": 0,
                "location": {"lat": latitude, "lon": longitude},
            }

    except httpx.HTTPStatusError as e:
        logger.error(f"Crime incidents HTTP error: {e.response.status_code}")
        return {
            "error": f"HTTP {e.response.status_code}",
            "incidents": [],
            "total_incidents": 0,
            "location": {"lat": latitude, "lon": longitude},
        }
    except Exception as e:
        logger.error(f"Crime incidents error: {e}")
        return {
            "error": str(e),
            "incidents": [],
            "total_incidents": 0,
            "location": {"lat": latitude, "lon": longitude},
        }
