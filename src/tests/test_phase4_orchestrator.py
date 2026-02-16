"""Phase 4 Tests: SafeTravels Orchestrator.

Tests the full orchestration pipeline:
- Google Maps route fetching (real API)
- Crime data enrichment (mocked - Crimeometer key is rate-limited)
- AI risk analysis (real OpenRouter API)
- Final result building (unit test)

Requirements:
    - GOOGLE_MAPS_API_KEY must be set in .env
    - OPEN_ROUTER_API_KEY must be set in .env
    - CRIME_API_KEY: tests are mocked; real API tests skipped until private key available

Run:
    pytest src/tests/test_phase4_orchestrator.py -v -s
"""
import os
import sys
import json
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.safe_travels import (
    get_google_routes,
    enrich_waypoint_with_crime,
    enrich_route_with_crime,
    enrich_all_routes,
    build_final_result,
    analyze_route_risk,
    main,
)
from src.helper_functions.crimeo import get_date_range

# =============================================================================
# TEST RESULTS RECORDING
# =============================================================================

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "phase4_orchestrator_results.json")
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
            "phase": "Phase 4 - Orchestrator",
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
# MOCK DATA
# =============================================================================

MOCK_CRIME_RESPONSE = {
    "total_incidents": 3,
    "incidents": [
        {"offense": "Theft", "incident_date": "2026-02-10"},
        {"offense": "Motor Vehicle Theft", "incident_date": "2026-02-08"},
        {"offense": "Vandalism", "incident_date": "2026-02-05"},
    ],
    "incidents_returned": 3,
    "location": {"lat": 41.878, "lon": -87.636},
}

MOCK_CRIME_EMPTY = {
    "total_incidents": 0,
    "incidents": [],
    "incidents_returned": 0,
    "location": {"lat": 41.878, "lon": -87.636},
}


# =============================================================================
# UNIT TESTS: get_date_range (from crimeo.py)
# =============================================================================

class TestDateRange:
    """Test the date range helper used by crimeo.py."""

    def test_returns_tuple(self):
        """get_date_range should return a tuple of two strings."""
        result = get_date_range()
        assert isinstance(result, tuple)
        assert len(result) == 2
        _record_test("test_date_range_returns_tuple", "passed")

    def test_format(self):
        """Dates should match yyyy-MM-ddT00:00:00.000Z format."""
        start, end = get_date_range()
        assert start.endswith("T00:00:00.000Z")
        assert end.endswith("T00:00:00.000Z")
        assert len(start) == 24
        _record_test("test_date_range_format", "passed")

    def test_default_14_days(self):
        """Default range should span 14 days."""
        start, end = get_date_range()
        start_dt = datetime.strptime(start, "%Y-%m-%dT00:00:00.000Z")
        end_dt = datetime.strptime(end, "%Y-%m-%dT00:00:00.000Z")
        diff = (end_dt - start_dt).days
        assert diff == 14, f"Expected 14 day span, got {diff}"
        _record_test("test_date_range_14_days", "passed")


# =============================================================================
# UNIT TESTS: build_final_result
# =============================================================================

class TestBuildFinalResult:
    """Test the final result builder (no API calls needed)."""

    def test_basic_output_structure(self):
        """Output should have expected keys and no waypoints."""
        routes = [
            {
                "route_id": 1,
                "summary": "Test Route",
                "distance_miles": 2.0,
                "duration_minutes": 10,
                "start_address": "Start",
                "end_address": "End",
                "waypoints": [{"latitude": 41.0, "longitude": -87.0}],
            }
        ]
        analyses = [
            {
                "route_id": 1,
                "risk_score": 45,
                "analysis": "Moderate risk.",
                "status": "success",
            }
        ]

        result = build_final_result(routes, analyses)

        assert len(result) == 1
        r = result[0]
        assert r["route_id"] == 1
        assert r["risk_score"] == 45
        assert r["analysis"] == "Moderate risk."
        assert r["status"] == "success"
        # Waypoints should NOT be in the final output
        assert "waypoints" not in r
        _record_test("test_basic_output_structure", "passed")

    def test_failed_analysis(self):
        """Failed analyses should include error and null score."""
        routes = [
            {
                "route_id": 1,
                "summary": "Test",
                "distance_miles": 1.0,
                "duration_minutes": 5,
                "start_address": "A",
                "end_address": "B",
                "waypoints": [],
            }
        ]
        analyses = [
            {
                "route_id": 1,
                "risk_score": None,
                "analysis": None,
                "status": "failed",
                "error": "API timeout",
            }
        ]

        result = build_final_result(routes, analyses)
        r = result[0]
        assert r["status"] == "failed"
        assert r["risk_score"] is None
        assert r["error"] == "API timeout"
        _record_test("test_failed_analysis", "passed")

    def test_multiple_routes(self):
        """Should handle multiple routes correctly."""
        routes = [
            {"route_id": 1, "summary": "Route A", "distance_miles": 2.0,
             "duration_minutes": 10, "start_address": "A", "end_address": "B", "waypoints": []},
            {"route_id": 2, "summary": "Route B", "distance_miles": 3.0,
             "duration_minutes": 15, "start_address": "A", "end_address": "B", "waypoints": []},
        ]
        analyses = [
            {"route_id": 1, "risk_score": 30, "analysis": "Safe.", "status": "success"},
            {"route_id": 2, "risk_score": 65, "analysis": "Elevated.", "status": "success"},
        ]

        result = build_final_result(routes, analyses)
        assert len(result) == 2
        assert result[0]["risk_score"] == 30
        assert result[1]["risk_score"] == 65
        _record_test("test_multiple_routes", "passed")


# =============================================================================
# INTEGRATION TEST: Google Maps Routes (real API)
# =============================================================================

class TestGoogleMapsRoutes:
    """Test route fetching from Google Maps (requires GOOGLE_MAPS_API_KEY)."""

    def test_get_routes_returns_list(self):
        """get_google_routes should return a non-empty list of routes."""
        routes = get_google_routes("Willis Tower, Chicago, IL", "Navy Pier, Chicago, IL")

        assert isinstance(routes, list)
        assert len(routes) >= 1
        _record_test("test_get_routes_returns_list", "passed", {
            "num_routes": len(routes),
        })

    def test_route_has_expected_keys(self):
        """Each route should have the keys needed by the orchestrator."""
        routes = get_google_routes("Willis Tower, Chicago, IL", "Navy Pier, Chicago, IL")
        route = routes[0]

        expected_keys = [
            "route_id", "summary", "distance_miles", "duration_minutes",
            "start_address", "end_address", "waypoints", "polyline",
        ]
        for key in expected_keys:
            assert key in route, f"Missing key: {key}"

        assert len(route["waypoints"]) > 0
        wp = route["waypoints"][0]
        assert "latitude" in wp
        assert "longitude" in wp

        _record_test("test_route_has_expected_keys", "passed", {
            "num_waypoints": len(route["waypoints"]),
        })


# =============================================================================
# MOCKED TESTS: Crime Data Enrichment
# =============================================================================

class TestCrimeEnrichmentMocked:
    """Test crime data enrichment with mocked Crimeometer API."""

    @pytest.mark.asyncio
    async def test_enrich_single_waypoint(self):
        """A waypoint should get a crime_data key after enrichment."""
        waypoint = {"latitude": 41.878, "longitude": -87.636, "description": None, "area_type": None}

        with patch("src.safe_travels.get_crime_incidents", new_callable=AsyncMock) as mock_crime:
            mock_crime.return_value = MOCK_CRIME_RESPONSE

            result = await enrich_waypoint_with_crime(waypoint)

            assert "crime_data" in result
            assert result["crime_data"]["total_incidents"] == 3
            mock_crime.assert_called_once_with(latitude=41.878, longitude=-87.636)

        _record_test("test_enrich_single_waypoint", "passed")

    @pytest.mark.asyncio
    async def test_enrich_route_all_waypoints(self):
        """All waypoints in a route should get crime_data."""
        route = {
            "route_id": 1,
            "waypoints": [
                {"latitude": 41.878, "longitude": -87.636, "description": None, "area_type": None},
                {"latitude": 41.882, "longitude": -87.629, "description": None, "area_type": None},
                {"latitude": 41.891, "longitude": -87.613, "description": None, "area_type": None},
            ],
        }

        with patch("src.safe_travels.get_crime_incidents", new_callable=AsyncMock) as mock_crime:
            mock_crime.return_value = MOCK_CRIME_RESPONSE

            result = await enrich_route_with_crime(route)

            assert all("crime_data" in wp for wp in result["waypoints"])
            assert mock_crime.call_count == 3

        _record_test("test_enrich_route_all_waypoints", "passed")

    @pytest.mark.asyncio
    async def test_enrich_route_no_waypoints(self):
        """A route with no waypoints should be returned unchanged."""
        route = {"route_id": 1, "waypoints": []}

        with patch("src.safe_travels.get_crime_incidents", new_callable=AsyncMock) as mock_crime:
            result = await enrich_route_with_crime(route)

            assert result["waypoints"] == []
            mock_crime.assert_not_called()

        _record_test("test_enrich_route_no_waypoints", "passed")

    @pytest.mark.asyncio
    async def test_enrich_all_routes_parallel(self):
        """Multiple routes should all get enriched."""
        routes = [
            {
                "route_id": 1,
                "waypoints": [
                    {"latitude": 41.878, "longitude": -87.636, "description": None, "area_type": None},
                ],
            },
            {
                "route_id": 2,
                "waypoints": [
                    {"latitude": 41.882, "longitude": -87.629, "description": None, "area_type": None},
                ],
            },
        ]

        with patch("src.safe_travels.get_crime_incidents", new_callable=AsyncMock) as mock_crime:
            mock_crime.return_value = MOCK_CRIME_EMPTY

            result = await enrich_all_routes(routes)

            assert len(result) == 2
            assert all("crime_data" in r["waypoints"][0] for r in result)
            assert mock_crime.call_count == 2

        _record_test("test_enrich_all_routes_parallel", "passed")


# =============================================================================
# INTEGRATION TEST: Full Pipeline (mocked crime, real Maps + AI)
# =============================================================================

@pytest.mark.asyncio
async def test_full_pipeline_mocked_crime():
    """
    Run the full main() pipeline with:
    - Real Google Maps API (routes)
    - Mocked Crimeometer API (crime data)
    - Real OpenRouter AI agent (risk analysis)

    Verifies the output JSON structure matches the spec.
    """
    with patch("src.safe_travels.get_crime_incidents", new_callable=AsyncMock) as mock_crime:
        mock_crime.return_value = MOCK_CRIME_RESPONSE

        results = await main("Willis Tower, Chicago, IL", "Navy Pier, Chicago, IL")

    assert isinstance(results, list)
    assert len(results) >= 1

    for route in results:
        # Check all expected keys
        assert "route_id" in route
        assert "summary" in route
        assert "distance_miles" in route
        assert "duration_minutes" in route
        assert "start_address" in route
        assert "end_address" in route
        assert "risk_score" in route
        assert "analysis" in route
        assert "status" in route

        # Waypoints should NOT be in final output
        assert "waypoints" not in route

        # If status is success, score and analysis should be present
        if route["status"] == "success":
            assert isinstance(route["risk_score"], int)
            assert 1 <= route["risk_score"] <= 100
            assert len(route["analysis"]) > 0

    # Save results for inspection
    output_file = os.path.join(os.path.dirname(__file__), "phase4_full_pipeline_result.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "test_metadata": {
                "test": "test_full_pipeline_mocked_crime",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "num_routes": len(results),
            },
            "results": results,
        }, f, indent=2, ensure_ascii=False)

    _record_test("test_full_pipeline_mocked_crime", "passed", {
        "num_routes": len(results),
        "scores": [r.get("risk_score") for r in results],
    })

    print(f"\n  Full pipeline returned {len(results)} routes:")
    for r in results:
        print(f"    Route {r['route_id']}: score={r.get('risk_score')} status={r['status']}")


# =============================================================================
# SKIPPED: Real Crimeometer API Tests (awaiting private API key)
# =============================================================================

@pytest.mark.skip(reason="Awaiting private Crimeometer API key - shared key is rate-limited (429)")
@pytest.mark.asyncio
async def test_real_crime_enrichment():
    """
    Test crime enrichment with real Crimeometer API.
    Remove @pytest.mark.skip once you have a working API key.
    """
    from src.helper_functions.crimeo import get_crime_incidents

    result = await get_crime_incidents(latitude=41.8781, longitude=-87.6298)

    assert "error" not in result, f"API returned error: {result.get('error')}"
    assert "total_incidents" in result
    assert "incidents" in result
    _record_test("test_real_crime_enrichment", "passed", result)


@pytest.mark.skip(reason="Awaiting private Crimeometer API key - shared key is rate-limited (429)")
@pytest.mark.asyncio
async def test_full_pipeline_real():
    """
    Test the full pipeline with ALL real APIs (Maps + Crime + AI).
    Remove @pytest.mark.skip once you have a working Crimeometer API key.
    """
    results = await main("Willis Tower, Chicago, IL", "Navy Pier, Chicago, IL")

    assert len(results) >= 1
    for route in results:
        assert route["status"] == "success"
        assert 1 <= route["risk_score"] <= 100
    _record_test("test_full_pipeline_real", "passed", {
        "num_routes": len(results),
        "scores": [r["risk_score"] for r in results],
    })
