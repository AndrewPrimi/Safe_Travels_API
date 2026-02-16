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
