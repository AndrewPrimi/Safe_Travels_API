"""Phase 3 Tests: AI Risk Analysis Agent.

Tests the PydanticAI agent and RouteRiskAnalysis model in isolation.
No Google Maps or Crime API calls needed for most tests.

Requirements:
    - OPEN_ROUTER_API_KEY must be set in .env for integration tests
    - LLM_MODEL defaults to openai/gpt-4o-mini

Run:
    pytest src/tests/test_phase3_agent.py -v -s
"""
import os
import sys
import json
import pytest
from datetime import datetime, timezone

from pydantic import ValidationError

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.safe_travels import RouteRiskAnalysis, risk_agent

# =============================================================================
# TEST RESULTS RECORDING
# =============================================================================

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "phase3_agent_results.json")
_test_results = []


def _record_test(name: str, status: str, details: dict = None):
    """Record a test result for JSON output."""
    _test_results.append({
        "test": name,
        "status": status,
        "details": details or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@pytest.fixture(autouse=True, scope="session")
def save_results():
    """Save all test results to JSON after the session completes."""
    yield
    output = {
        "test_metadata": {
            "phase": "Phase 3 - AI Agent",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_tests": len(_test_results),
            "passed": sum(1 for r in _test_results if r["status"] == "passed"),
            "failed": sum(1 for r in _test_results if r["status"] == "failed"),
        },
        "results": _test_results,
    }
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to: {RESULTS_FILE}")


# =============================================================================
# UNIT TESTS: RouteRiskAnalysis Pydantic Model
# =============================================================================

class TestRouteRiskAnalysisModel:
    """Test the Pydantic model for structured AI output."""

    def test_valid_model(self):
        """Valid risk_score and analysis should create a model instance."""
        model = RouteRiskAnalysis(risk_score=50, analysis="Moderate risk route.")
        assert model.risk_score == 50
        assert model.analysis == "Moderate risk route."
        _record_test("test_valid_model", "passed", {"risk_score": 50})

    def test_boundary_low(self):
        """risk_score=1 (minimum) should be valid."""
        model = RouteRiskAnalysis(risk_score=1, analysis="Very safe.")
        assert model.risk_score == 1
        _record_test("test_boundary_low", "passed")

    def test_boundary_high(self):
        """risk_score=100 (maximum) should be valid."""
        model = RouteRiskAnalysis(risk_score=100, analysis="Extremely dangerous.")
        assert model.risk_score == 100
        _record_test("test_boundary_high", "passed")

    def test_score_too_low(self):
        """risk_score=0 should fail validation (min is 1)."""
        with pytest.raises(ValidationError):
            RouteRiskAnalysis(risk_score=0, analysis="Invalid.")
        _record_test("test_score_too_low", "passed")

    def test_score_too_high(self):
        """risk_score=101 should fail validation (max is 100)."""
        with pytest.raises(ValidationError):
            RouteRiskAnalysis(risk_score=101, analysis="Invalid.")
        _record_test("test_score_too_high", "passed")

    def test_missing_analysis(self):
        """Missing analysis field should fail validation."""
        with pytest.raises(ValidationError):
            RouteRiskAnalysis(risk_score=50)
        _record_test("test_missing_analysis", "passed")

    def test_missing_score(self):
        """Missing risk_score field should fail validation."""
        with pytest.raises(ValidationError):
            RouteRiskAnalysis(analysis="No score provided.")
        _record_test("test_missing_score", "passed")


# =============================================================================
# INTEGRATION TESTS: AI Agent (requires OPEN_ROUTER_API_KEY)
# =============================================================================

# Sample route data for agent testing (no real API calls needed)
MOCK_ROUTE_WITH_CRIME = {
    "route_id": 1,
    "summary": "S Wacker Dr",
    "distance_miles": 2.26,
    "duration_minutes": 9,
    "start_address": "233 S Wacker Dr, Chicago, IL 60606, USA",
    "end_address": "600 E Grand Ave, Chicago, IL 60611, USA",
    "waypoints": [
        {
            "latitude": 41.87870,
            "longitude": -87.63580,
            "crime_data": {
                "total_incidents": 3,
                "incidents": [
                    {"offense": "Theft", "incident_date": "2026-02-10"},
                    {"offense": "Motor Vehicle Theft", "incident_date": "2026-02-08"},
                    {"offense": "Vandalism", "incident_date": "2026-02-05"},
                ],
                "incidents_returned": 3,
                "location": {"lat": 41.87870, "lon": -87.63580},
            },
        },
        {
            "latitude": 41.88200,
            "longitude": -87.62900,
            "crime_data": {
                "total_incidents": 1,
                "incidents": [
                    {"offense": "Battery", "incident_date": "2026-02-12"},
                ],
                "incidents_returned": 1,
                "location": {"lat": 41.88200, "lon": -87.62900},
            },
        },
        {
            "latitude": 41.89120,
            "longitude": -87.61300,
            "crime_data": {
                "total_incidents": 0,
                "incidents": [],
                "incidents_returned": 0,
                "location": {"lat": 41.89120, "lon": -87.61300},
            },
        },
    ],
}

MOCK_ROUTE_ALL_ERRORS = {
    "route_id": 2,
    "summary": "Error Route",
    "distance_miles": 1.5,
    "duration_minutes": 7,
    "start_address": "Start Address",
    "end_address": "End Address",
    "waypoints": [
        {
            "latitude": 41.87870,
            "longitude": -87.63580,
            "crime_data": {
                "error": "Rate limit exceeded",
                "status_code": 429,
                "incidents": [],
                "total_incidents": 0,
                "location": {"lat": 41.87870, "lon": -87.63580},
            },
        },
        {
            "latitude": 41.88200,
            "longitude": -87.62900,
            "crime_data": {
                "error": "Rate limit exceeded",
                "status_code": 429,
                "incidents": [],
                "total_incidents": 0,
                "location": {"lat": 41.88200, "lon": -87.62900},
            },
        },
    ],
}


def _build_agent_prompt(route: dict) -> str:
    """Build the same user prompt that analyze_route_risk() builds."""
    user_prompt = f"""Analyze the following route for crime risk:

Route ID: {route.get('route_id')}
Summary: {route.get('summary')}
Distance: {route.get('distance_miles')} miles
Duration: {route.get('duration_minutes')} minutes
Start: {route.get('start_address')}
End: {route.get('end_address')}

Waypoint Crime Data:
"""
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
    return user_prompt


@pytest.mark.asyncio
async def test_agent_with_mock_route():
    """Feed the agent a mock route with crime data and verify structured output."""
    prompt = _build_agent_prompt(MOCK_ROUTE_WITH_CRIME)
    result = await risk_agent.run(prompt)

    assert isinstance(result.output, RouteRiskAnalysis)
    assert 1 <= result.output.risk_score <= 100
    assert len(result.output.analysis) > 0

    _record_test("test_agent_with_mock_route", "passed", {
        "risk_score": result.output.risk_score,
        "analysis_length": len(result.output.analysis),
    })
    print(f"\n  Agent returned score: {result.output.risk_score}")
    print(f"  Analysis preview: {result.output.analysis[:150]}...")


@pytest.mark.asyncio
async def test_agent_returns_reasonable_score():
    """Verify the agent doesn't return extreme scores for moderate crime data."""
    prompt = _build_agent_prompt(MOCK_ROUTE_WITH_CRIME)
    result = await risk_agent.run(prompt)

    # With 4 total incidents (3 property + 1 battery) over 3 waypoints,
    # a reasonable score should be in the moderate range (20-70)
    score = result.output.risk_score
    assert 10 <= score <= 80, (
        f"Score {score} seems unreasonable for moderate crime data. "
        f"Expected 10-80 range."
    )

    _record_test("test_agent_returns_reasonable_score", "passed", {
        "risk_score": score,
    })
    print(f"\n  Reasonable score check: {score} (expected 10-80)")


@pytest.mark.asyncio
async def test_agent_handles_error_waypoints():
    """Agent should still produce output when all waypoints have errors."""
    prompt = _build_agent_prompt(MOCK_ROUTE_ALL_ERRORS)
    result = await risk_agent.run(prompt)

    assert isinstance(result.output, RouteRiskAnalysis)
    assert 1 <= result.output.risk_score <= 100
    assert len(result.output.analysis) > 0

    _record_test("test_agent_handles_error_waypoints", "passed", {
        "risk_score": result.output.risk_score,
        "analysis_length": len(result.output.analysis),
    })
    print(f"\n  Error route score: {result.output.risk_score}")
    print(f"  Analysis preview: {result.output.analysis[:150]}...")
