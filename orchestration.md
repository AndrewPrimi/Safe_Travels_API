# SafeTravels Orchestration Plan

> **GOAL**: Create the final orchestration layer that combines Google Maps routes, Crimeometer crime data, and AI risk analysis into a complete route safety assessment system.

---

## Table of Contents

1. [Overview](#overview)
2. [File Structure](#file-structure)
3. [Step 1: Create crimeo.py Helper](#step-1-create-crimeopy-helper)
4. [Step 2: Create safe_travels.py Orchestrator](#step-2-create-safe_travelspy-orchestrator)
5. [Step 3: Create the AI Agent](#step-3-create-the-ai-agent)
6. [Step 4: Test Everything](#step-4-test-everything)
7. [Expected Output Format](#expected-output-format)

---

## Overview

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              def main(start, destination)                    │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: Call get_routes(start, destination)                                │
│  Source: src/helper_functions/google_maps_final.py                          │
│  Returns: List of route dictionaries with waypoints                         │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: For each route, extract waypoints                                  │
│  For each waypoint (lat, lon), call get_crime_incidents() IN PARALLEL       │
│  Source: src/helper_functions/crimeo.py                                     │
│  Append crime_data to each waypoint dictionary                              │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 3: For each route (with enriched waypoints), call AI agent IN PARALLEL│
│  Send route dictionary (including waypoints + crime_data) as user prompt    │
│  Agent returns: risk_score (int 1-100) and analysis (str)                   │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 4: Build final result (WITHOUT waypoints)                             │
│  For each route: route_id, summary, distance, duration, addresses,          │
│                  risk_score, analysis                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Crime API access | Direct import (not MCP) | Simpler for MVP |
| Parallelism | asyncio.gather() | Efficient async I/O |
| Crime function | get_crime_incidents() | More detailed data for AI |
| Hardcoded params | radius=0.25mi, days=14, limit=5 | Consistent analysis |

---

## File Structure

After completing this plan, your `src/` directory will look like:

```
src/
├── safe_travels.py                    # Main orchestrator (CREATE)
├── helper_functions/
│   ├── __init__.py
│   ├── google_maps_final.py           # Already exists
│   └── crimeo.py                      # Crime helper (CREATE)
├── MCP_Servers/
│   └── crime_mcp/                     # Already exists (not used in MVP)
└── tests/
    ├── final_result_test.json         # Test output (GENERATED)
    └── ... (existing tests)
```

---

## Step 1: Create crimeo.py Helper

### File: `src/helper_functions/crimeo.py`

This file provides direct access to Crimeometer API functions without going through the MCP server.

### What to Import

Copy and adapt these functions from `src/MCP_Servers/crime_mcp/functions.py`:
- `get_date_range()` - computes datetime_ini and datetime_end
- `get_crime_stats()` - gets crime statistics (include but not used in main)
- `get_crime_incidents()` - gets incident details (used in main)

### Implementation Requirements

1. **Environment Variables Required:**
   ```
   CRIME_API_KEY        # Crimeometer API key
   CRIME_API_BASE_URL   # Default: https://api.crimeometer.com/v1
   ```

2. **Hardcoded Defaults (do NOT make these parameters):**
   ```python
   RADIUS_MILES = 0.25
   DAYS_BACK = 14
   LIMIT = 5
   ```

3. **Function Signatures:**
   ```python
   def get_date_range(days_back: int = 14) -> tuple[str, str]:
       """Returns (datetime_ini, datetime_end) formatted for Crimeometer."""
       pass

   async def get_crime_stats(latitude: float, longitude: float) -> dict:
       """Get crime statistics for a location. Only takes lat/lon."""
       pass

   async def get_crime_incidents(latitude: float, longitude: float) -> dict:
       """Get crime incidents for a location. Only takes lat/lon."""
       pass
   ```

4. **Error Handling:**
   - If API call fails (rate limit, timeout, network error), return a dict with `"error"` key
   - Example: `{"error": "Rate limit exceeded", "location": {"lat": 41.87, "lon": -87.63}}`

### Complete Code for crimeo.py

```python
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
```

### Verification Checklist for Step 1

- [ ] File created at `src/helper_functions/crimeo.py`
- [ ] `get_date_range()` returns tuple of formatted date strings
- [ ] `get_crime_stats()` only takes latitude and longitude
- [ ] `get_crime_incidents()` only takes latitude and longitude
- [ ] All defaults are hardcoded (RADIUS_MILES=0.25, DAYS_BACK=14, LIMIT=5)
- [ ] Error handling returns dict with "error" key
- [ ] Functions are async

---

## Step 2: Create safe_travels.py Orchestrator

### File: `src/safe_travels.py`

This is the main orchestration script that ties everything together.

### Architecture

```python
async def main(start: str, destination: str) -> list[dict]:
    """
    Main orchestration function.

    1. Get routes from Google Maps
    2. Enrich waypoints with crime data (parallel)
    3. Send each route to AI agent for analysis (parallel)
    4. Return final results (without waypoints)
    """
```

### Complete Code for safe_travels.py

```python
"""SafeTravels Route Analysis Orchestrator.

Main orchestration script that:
1. Gets routes from Google Maps
2. Enriches waypoints with crime data
3. Sends routes to AI agent for risk analysis
4. Returns final risk assessments

Usage:
    python src/safe_travels.py

    # Or import and use programmatically:
    from src.safe_travels import main
    import asyncio
    results = asyncio.run(main("Willis Tower, Chicago, IL", "Navy Pier, Chicago, IL"))
"""
import os
import sys
import json
import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime, timezone

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.helper_functions.google_maps_final import get_routes
from src.helper_functions.crimeo import get_crime_incidents

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")
OPENROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("OPEN_ROUTER_API_KEY environment variable not set")


# =============================================================================
# AI AGENT OUTPUT TYPE
# =============================================================================

class RouteRiskAnalysis(BaseModel):
    """Structured output from the AI risk analysis agent."""

    risk_score: int = Field(
        ...,
        ge=1,
        le=100,
        description="Risk score from 1 (safest) to 100 (most dangerous)"
    )
    analysis: str = Field(
        ...,
        description="Detailed analysis explaining the risk assessment"
    )


# =============================================================================
# AI AGENT SETUP
# =============================================================================

# Initialize model via OpenRouter
model = OpenAIModel(
    LLM_MODEL,
    provider=OpenAIProvider(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    ),
)

# System prompt for the risk analysis agent
# IMPORTANT: Spend time crafting this prompt for nuanced, accurate assessments
SYSTEM_PROMPT = """You are a Crime Risk Analyst AI specializing in urban route safety assessment.

## YOUR MISSION
Analyze driving route data (including crime incidents at waypoints) and provide:
1. A risk score from 1-100
2. A detailed analysis explaining your assessment

## SCORING GUIDELINES

### Scale Definition
- 1-20: VERY SAFE - Minimal to no crime activity. Residential or well-patrolled areas.
- 21-40: SAFE - Low crime levels typical of normal urban areas. Standard precautions.
- 41-60: MODERATE - Notable crime presence but manageable. Stay aware, avoid stopping unnecessarily.
- 61-80: ELEVATED RISK - Significant crime activity. Pass through without stopping if possible.
- 81-100: HIGH RISK - Concentrated crime. Consider alternative routes.

### Critical Context
- You are analyzing URBAN ROUTES in major cities like Chicago
- Some crime is NORMAL and EXPECTED in any major city
- Do NOT give extreme scores (90+) unless crime is truly severe
- A few property crimes (theft, vandalism) should NOT result in high scores
- Violent crimes (assault, robbery) should weight more heavily
- Consider the TIME CONTEXT: 14 days of data in a 0.25 mile radius

### Scoring Factors (in order of importance)
1. **Violent Crime Presence**: Assault, robbery, battery (highest weight)
2. **Crime Volume**: Total incidents relative to route length
3. **Crime Concentration**: Spread out vs clustered at specific points
4. **Crime Types**: Property crime is less concerning than violent crime
5. **Missing Data**: If waypoints have errors, note this uncertainty

## YOUR ANALYSIS MUST INCLUDE

1. **Overall Assessment** (1-2 sentences): Quick summary of route safety
2. **Key Findings**: What types of crimes were found? Where?
3. **Risk Factors**: What specifically contributed to your score?
4. **Context**: Acknowledge that some crime is normal for urban areas
5. **Recommendation**: Brief advice for travelers

## IMPORTANT RULES

- Be NUANCED - avoid extreme scores without strong justification
- Be SPECIFIC - reference actual crime types and locations when available
- Be BALANCED - acknowledge both risks AND safer aspects
- Be REALISTIC - urban routes will have some crime; that's normal
- If data shows errors or rate limits, acknowledge the uncertainty

## EXAMPLE OUTPUT

Risk Score: 52

Analysis: This route through downtown Chicago presents moderate risk typical of major urban corridors. Crime data shows 12 total incidents across 5 waypoints over 14 days, primarily consisting of theft (5 incidents) and motor vehicle theft (3 incidents) concentrated near the commercial district. One assault was reported near the midpoint of the route. While property crime is elevated, violent crime remains limited. The route passes through well-trafficked areas during daylight hours. Recommendation: Standard urban precautions apply - keep valuables hidden, stay aware of surroundings, and avoid unnecessary stops in the commercial corridor area."""

# Create the agent
risk_agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    output_type=RouteRiskAnalysis,
    retries=2,
)


# =============================================================================
# STEP 1: GET ROUTES FROM GOOGLE MAPS
# =============================================================================

def get_google_routes(start: str, destination: str) -> List[Dict[str, Any]]:
    """
    Get route alternatives from Google Maps.

    Args:
        start: Starting address
        destination: Destination address

    Returns:
        List of route dictionaries from google_maps_final.get_routes()
    """
    logger.info(f"Getting routes: {start} -> {destination}")
    routes = get_routes(start, destination, include_traffic=True)
    logger.info(f"Found {len(routes)} route(s)")
    return routes


# =============================================================================
# STEP 2: ENRICH WAYPOINTS WITH CRIME DATA
# =============================================================================

async def enrich_waypoint_with_crime(waypoint: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add crime data to a single waypoint.

    Args:
        waypoint: Dict with latitude, longitude, description, area_type

    Returns:
        Same dict with added "crime_data" key
    """
    lat = waypoint["latitude"]
    lon = waypoint["longitude"]

    crime_data = await get_crime_incidents(latitude=lat, longitude=lon)

    # Add crime_data to waypoint
    waypoint["crime_data"] = crime_data

    return waypoint


async def enrich_route_with_crime(route: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich all waypoints in a route with crime data (parallel).

    Args:
        route: Route dictionary with waypoints list

    Returns:
        Same route with crime_data added to each waypoint
    """
    waypoints = route.get("waypoints", [])

    if not waypoints:
        logger.warning(f"Route {route.get('route_id')} has no waypoints")
        return route

    logger.info(f"Enriching route {route.get('route_id')} with {len(waypoints)} waypoints")

    # Enrich all waypoints in parallel
    tasks = [enrich_waypoint_with_crime(wp) for wp in waypoints]
    enriched_waypoints = await asyncio.gather(*tasks)

    route["waypoints"] = enriched_waypoints
    return route


async def enrich_all_routes(routes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enrich all routes with crime data (parallel per route).

    Args:
        routes: List of route dictionaries

    Returns:
        Same routes with crime_data added to each waypoint
    """
    logger.info(f"Enriching {len(routes)} routes with crime data")

    # Process all routes in parallel
    tasks = [enrich_route_with_crime(route) for route in routes]
    enriched_routes = await asyncio.gather(*tasks)

    return enriched_routes


# =============================================================================
# STEP 3: AI RISK ANALYSIS
# =============================================================================

async def analyze_route_risk(route: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send route to AI agent for risk analysis.

    Args:
        route: Enriched route dictionary (with crime_data in waypoints)

    Returns:
        Dict with risk_score and analysis
    """
    route_id = route.get("route_id", "?")
    logger.info(f"Analyzing risk for route {route_id}")

    # Build user prompt with route data
    user_prompt = f"""Analyze the following route for crime risk:

Route ID: {route.get('route_id')}
Summary: {route.get('summary')}
Distance: {route.get('distance_miles')} miles
Duration: {route.get('duration_minutes')} minutes
Start: {route.get('start_address')}
End: {route.get('end_address')}

Waypoint Crime Data:
"""

    # Add waypoint data
    for i, wp in enumerate(route.get("waypoints", []), 1):
        user_prompt += f"\n--- Waypoint {i} ({wp['latitude']:.5f}, {wp['longitude']:.5f}) ---\n"
        crime_data = wp.get("crime_data", {})

        if "error" in crime_data:
            user_prompt += f"  ERROR: {crime_data['error']}\n"
        else:
            user_prompt += f"  Total Incidents: {crime_data.get('total_incidents', 0)}\n"
            incidents = crime_data.get("incidents", [])
            if incidents:
                user_prompt += f"  Incidents ({len(incidents)} returned):\n"
                for inc in incidents:
                    offense = inc.get("offense", "Unknown")
                    date = inc.get("incident_date", "Unknown date")
                    user_prompt += f"    - {offense} ({date})\n"
            else:
                user_prompt += "  No incidents reported\n"

    user_prompt += "\nProvide your risk score (1-100) and detailed analysis."

    try:
        result = await risk_agent.run(user_prompt)

        return {
            "route_id": route_id,
            "risk_score": result.output.risk_score,
            "analysis": result.output.analysis,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Risk analysis failed for route {route_id}: {e}")
        return {
            "route_id": route_id,
            "risk_score": None,
            "analysis": None,
            "status": "failed",
            "error": str(e)
        }


async def analyze_all_routes(routes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analyze all routes for risk (parallel).

    Args:
        routes: List of enriched route dictionaries

    Returns:
        List of analysis results
    """
    logger.info(f"Running AI risk analysis on {len(routes)} routes")

    # Analyze all routes in parallel
    tasks = [analyze_route_risk(route) for route in routes]
    analyses = await asyncio.gather(*tasks)

    return analyses


# =============================================================================
# STEP 4: BUILD FINAL RESULT
# =============================================================================

def build_final_result(
    routes: List[Dict[str, Any]],
    analyses: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Build final result combining route info with risk analysis.

    IMPORTANT: Final result does NOT include waypoints.

    Args:
        routes: Original route dictionaries
        analyses: Risk analysis results

    Returns:
        List of final route results
    """
    # Create a lookup for analyses by route_id
    analysis_lookup = {a["route_id"]: a for a in analyses}

    final_results = []

    for route in routes:
        route_id = route.get("route_id")
        analysis = analysis_lookup.get(route_id, {})

        final_route = {
            "route_id": route_id,
            "summary": route.get("summary"),
            "distance_miles": route.get("distance_miles"),
            "duration_minutes": route.get("duration_minutes"),
            "start_address": route.get("start_address"),
            "end_address": route.get("end_address"),
            "risk_score": analysis.get("risk_score"),
            "analysis": analysis.get("analysis"),
            "status": analysis.get("status", "unknown")
        }

        # Include error if present
        if "error" in analysis:
            final_route["error"] = analysis["error"]

        final_results.append(final_route)

    return final_results


# =============================================================================
# MAIN FUNCTION
# =============================================================================

async def main(start: str, destination: str) -> List[Dict[str, Any]]:
    """
    Main orchestration function.

    Flow:
    1. Get routes from Google Maps
    2. Enrich waypoints with crime data (parallel)
    3. Send each route to AI for risk analysis (parallel)
    4. Return final results (without waypoints)

    Args:
        start: Starting address (e.g., "Willis Tower, Chicago, IL")
        destination: Destination address (e.g., "Navy Pier, Chicago, IL")

    Returns:
        List of route results, each containing:
        - route_id, summary, distance_miles, duration_minutes
        - start_address, end_address
        - risk_score (1-100), analysis (str)
        - status ("success" or "failed")
    """
    logger.info("=" * 60)
    logger.info("SafeTravels Route Analysis")
    logger.info("=" * 60)
    logger.info(f"Start: {start}")
    logger.info(f"Destination: {destination}")
    logger.info("=" * 60)

    # Step 1: Get routes
    routes = get_google_routes(start, destination)

    if not routes:
        logger.error("No routes found")
        return []

    # Step 2: Enrich with crime data
    enriched_routes = await enrich_all_routes(routes)

    # Step 3: AI risk analysis
    analyses = await analyze_all_routes(enriched_routes)

    # Step 4: Build final result
    final_results = build_final_result(routes, analyses)

    logger.info("=" * 60)
    logger.info("Analysis Complete")
    logger.info("=" * 60)

    return final_results


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Test with Willis Tower to Navy Pier
    TEST_START = "Willis Tower, Chicago, IL"
    TEST_DESTINATION = "Navy Pier, Chicago, IL"

    print("=" * 60)
    print("SafeTravels Orchestrator Test")
    print("=" * 60)
    print(f"Start: {TEST_START}")
    print(f"Destination: {TEST_DESTINATION}")
    print("=" * 60)

    # Run the main function
    results = asyncio.run(main(TEST_START, TEST_DESTINATION))

    # Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    for route in results:
        print(f"\nRoute {route['route_id']}: {route['summary']}")
        print(f"  Distance: {route['distance_miles']} miles")
        print(f"  Duration: {route['duration_minutes']} minutes")
        print(f"  Risk Score: {route.get('risk_score', 'N/A')}")
        print(f"  Status: {route['status']}")
        if route.get('analysis'):
            print(f"  Analysis: {route['analysis'][:200]}...")

    # Save to JSON
    output_file = os.path.join(
        os.path.dirname(__file__),
        "tests",
        "final_result_test.json"
    )

    output_data = {
        "test_metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "start_address": TEST_START,
            "destination_address": TEST_DESTINATION,
            "num_routes": len(results)
        },
        "results": results
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n\nResults saved to: {output_file}")
```

### Verification Checklist for Step 2

- [ ] File created at `src/safe_travels.py`
- [ ] `main(start, destination)` is async function
- [ ] Step 1 calls `get_routes()` from google_maps_final
- [ ] Step 2 enriches waypoints with crime data using `asyncio.gather()`
- [ ] Step 3 calls AI agent for each route using `asyncio.gather()`
- [ ] Step 4 builds final result WITHOUT waypoints
- [ ] `if __name__ == "__main__"` tests with Willis Tower -> Navy Pier
- [ ] Results saved to `src/tests/final_result_test.json`

---

## Step 3: Create the AI Agent

The AI agent is created **within** `safe_travels.py` (see code above). Here's the detailed breakdown:

### Output Type Definition

```python
class RouteRiskAnalysis(BaseModel):
    """Structured output from the AI risk analysis agent."""

    risk_score: int = Field(
        ...,
        ge=1,
        le=100,
        description="Risk score from 1 (safest) to 100 (most dangerous)"
    )
    analysis: str = Field(
        ...,
        description="Detailed analysis explaining the risk assessment"
    )
```

### Accessing Output

After running the agent:
```python
result = await risk_agent.run(user_prompt)

# Access structured output
score = result.output.risk_score    # int between 1-100
text = result.output.analysis       # str with detailed analysis
```

### System Prompt Guidelines

The system prompt is **critical** for good results. Key elements:

1. **Clear Scoring Scale**: Define what each range (1-20, 21-40, etc.) means
2. **Urban Context**: Remind the AI that some crime is NORMAL in cities
3. **Nuanced Assessment**: Discourage extreme scores without justification
4. **Crime Type Weighting**: Violent crime > property crime > minor offenses
5. **Required Output Format**: Specify what the analysis must include

### Customizing the System Prompt

To improve results, experiment with:
- Adding more specific crime type weights
- Adjusting the scoring thresholds
- Including more example outputs
- Tweaking language for your target audience

---

## Step 4: Test Everything

### Running the Test

```bash
# From project root
cd /path/to/Safe_Travels_API

# Make sure environment variables are set
# .env should have:
# GOOGLE_MAPS_API_KEY=...
# CRIME_API_KEY=...
# OPEN_ROUTER_API_KEY=...
# LLM_MODEL=openai/gpt-4o-mini

# Run the orchestrator
python src/safe_travels.py
```

### Expected Console Output

```
============================================================
SafeTravels Orchestrator Test
============================================================
Start: Willis Tower, Chicago, IL
Destination: Navy Pier, Chicago, IL
============================================================
2026-02-13 10:00:00 - INFO - Getting routes: Willis Tower -> Navy Pier
2026-02-13 10:00:01 - INFO - Found 3 route(s)
2026-02-13 10:00:01 - INFO - Enriching 3 routes with crime data
2026-02-13 10:00:01 - INFO - Enriching route 1 with 6 waypoints
2026-02-13 10:00:01 - INFO - Enriching route 2 with 5 waypoints
2026-02-13 10:00:01 - INFO - Enriching route 3 with 5 waypoints
2026-02-13 10:00:05 - INFO - Running AI risk analysis on 3 routes
2026-02-13 10:00:05 - INFO - Analyzing risk for route 1
2026-02-13 10:00:05 - INFO - Analyzing risk for route 2
2026-02-13 10:00:05 - INFO - Analyzing risk for route 3
2026-02-13 10:00:15 - INFO - Analysis Complete

============================================================
RESULTS
============================================================

Route 1: S Lower Wacker Dr
  Distance: 2.26 miles
  Duration: 9 minutes
  Risk Score: 48
  Status: success
  Analysis: This route through downtown Chicago presents moderate risk...

Route 2: S Wacker Dr
  Distance: 2.26 miles
  Duration: 13 minutes
  Risk Score: 45
  Status: success
  Analysis: ...

Route 3: W Jackson Blvd...
  Distance: 2.16 miles
  Duration: 10 minutes
  Risk Score: 52
  Status: success
  Analysis: ...

Results saved to: src/tests/final_result_test.json
```

### Verification Checklist for Step 4

- [ ] Script runs without errors
- [ ] Google Maps returns 1-3 routes
- [ ] Crime data is fetched for each waypoint
- [ ] AI agent returns risk scores and analyses
- [ ] Results saved to `src/tests/final_result_test.json`
- [ ] Risk scores are reasonable (not all 100s or all 1s)

---

## Expected Output Format

### final_result_test.json Structure

```json
{
  "test_metadata": {
    "timestamp": "2026-02-13T10:00:15.123456+00:00",
    "start_address": "Willis Tower, Chicago, IL",
    "destination_address": "Navy Pier, Chicago, IL",
    "num_routes": 3
  },
  "results": [
    {
      "route_id": 1,
      "summary": "S Lower Wacker Dr",
      "distance_miles": 2.26,
      "duration_minutes": 9,
      "start_address": "233 S Wacker Dr, Chicago, IL 60606, USA",
      "end_address": "600 E Grand Ave, Chicago, IL 60611, USA",
      "risk_score": 48,
      "analysis": "This route through downtown Chicago presents moderate risk typical of major urban corridors. Crime data shows 8 total incidents across 6 waypoints over 14 days, primarily consisting of theft (3 incidents) and motor vehicle theft (2 incidents). The downtown area near Wacker Drive shows elevated property crime but limited violent incidents. One battery case was reported near the midpoint. Overall, the route passes through well-trafficked commercial areas. Recommendation: Standard urban precautions apply - keep valuables hidden and stay aware of surroundings.",
      "status": "success"
    },
    {
      "route_id": 2,
      "summary": "S Wacker Dr",
      "distance_miles": 2.26,
      "duration_minutes": 13,
      "start_address": "233 S Wacker Dr, Chicago, IL 60606, USA",
      "end_address": "600 E Grand Ave, Chicago, IL 60611, USA",
      "risk_score": 45,
      "analysis": "...",
      "status": "success"
    },
    {
      "route_id": 3,
      "summary": "W Jackson Blvd and S DuSable Lake Shore Dr...",
      "distance_miles": 2.16,
      "duration_minutes": 10,
      "start_address": "233 S Wacker Dr, Chicago, IL 60606, USA",
      "end_address": "600 E Grand Ave, Chicago, IL 60611, USA",
      "risk_score": 52,
      "analysis": "...",
      "status": "success"
    }
  ]
}
```

### Key Points About Output

1. **No waypoints in final output** - Waypoints are used internally but NOT included in results
2. **risk_score is 1-100** - Enforced by Pydantic validation
3. **analysis is always present** - String explanation of the score
4. **status indicates success/failure** - "success" or "failed" with error message

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `CRIME_API_KEY not set` | Add to `.env` file |
| `OPEN_ROUTER_API_KEY not set` | Add to `.env` file |
| `GOOGLE_MAPS_API_KEY not set` | Add to `.env` file |
| Rate limit (429) errors | Crime API has rate limits; errors are captured gracefully |
| No routes found | Check addresses are valid and Google Maps API key works |
| AI returns extreme scores | Adjust system prompt to be more nuanced |

### Required Environment Variables

```bash
# .env file
GOOGLE_MAPS_API_KEY=your_google_api_key
CRIME_API_KEY=your_crimeometer_api_key
CRIME_API_BASE_URL=https://api.crimeometer.com/v1
OPEN_ROUTER_API_KEY=your_openrouter_api_key
LLM_MODEL=openai/gpt-4o-mini
```

---

## Summary

This plan provides everything needed to complete the SafeTravels orchestration:

1. **crimeo.py**: Direct Crimeometer API access with hardcoded defaults
2. **safe_travels.py**: Main orchestrator with parallel processing
3. **AI Agent**: PydanticAI agent with structured output
4. **Test**: Willis Tower -> Navy Pier with JSON output

The final product takes a start and destination, returns a list of routes with AI-generated risk scores and analyses.
