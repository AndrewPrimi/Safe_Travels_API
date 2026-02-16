# Orchestration Layer — Implementation Guide

> Covers Phase 3 (AI Agent) and Phase 4 (Orchestrator) of the SafeTravels API.

---

## What Was Built

The orchestration layer connects Google Maps routes, Crimeometer crime data, and an AI risk analysis agent into a single pipeline. Given a start address and destination, it returns multiple routes each scored for crime risk.

### Data Flow

```
User provides start + destination
        │
        ▼
Step 1: get_routes() — Google Maps Directions API
        Returns 1-3 route alternatives with adaptive waypoints
        │
        ▼
Step 2: enrich_all_routes() — Crimeometer API (parallel)
        For each waypoint in each route, fetch crime incidents
        All API calls run concurrently via asyncio.gather()
        │
        ▼
Step 3: analyze_all_routes() — PydanticAI Agent via OpenRouter (parallel)
        Each route (with crime data) is sent to the AI agent
        Agent returns a risk_score (1-100) and written analysis
        │
        ▼
Step 4: build_final_result()
        Combines route info + AI analysis
        Strips waypoints from output (internal data only)
        Returns clean JSON
```

---

## Files Created

| File | Purpose |
|------|---------|
| `src/helper_functions/crimeo.py` | Standalone Crimeometer API helper |
| `src/safe_travels.py` | Main orchestrator |
| `src/tests/test_phase3_agent.py` | AI agent tests (10 tests) |
| `src/tests/test_phase4_orchestrator.py` | Orchestrator tests (13 tests + 2 skipped) |

### Files Already Existing (Not Modified)

| File | Purpose |
|------|---------|
| `src/helper_functions/google_maps_final.py` | Google Maps route helper (Phase 2) |
| `src/MCP_Servers/crime_mcp/functions.py` | Crime MCP server functions (Phase 1) |

---

## File Details

### `src/helper_functions/crimeo.py`

Adapted from `src/MCP_Servers/crime_mcp/functions.py` but simplified for direct use by the orchestrator. The MCP version takes 7+ parameters (api_key, client, radius, etc.); this version hardcodes everything and only exposes `(latitude, longitude)`.

**Hardcoded defaults:**
- `RADIUS_MILES = 0.25` — search radius around each waypoint
- `DAYS_BACK = 14` — look back 14 days for crime data
- `LIMIT = 5` — max 5 incidents per waypoint

**Functions:**
- `get_date_range(days_back=14)` — returns `(datetime_ini, datetime_end)` tuple
- `get_crime_stats(latitude, longitude)` — crime statistics (total + breakdown)
- `get_crime_incidents(latitude, longitude)` — individual incident records

**Error handling:** All functions return a dict with an `"error"` key on failure (rate limits, timeouts, missing API key). They never raise exceptions.

### `src/safe_travels.py`

The main orchestrator with these components:

**RouteRiskAnalysis** — Pydantic model for structured AI output:
- `risk_score: int` (1-100, enforced by Pydantic validation)
- `analysis: str` (detailed risk explanation)

**AI Agent** — PydanticAI agent configured with:
- Model: OpenRouter via `OpenAIModel` + `OpenAIProvider`
- Default model: `openai/gpt-4o-mini` (configurable via `LLM_MODEL` env var)
- System prompt: Detailed crime risk analyst instructions with scoring scale, examples, and rules for nuanced assessment
- Structured output: `output_type=RouteRiskAnalysis`
- Retries: 2

**Orchestration functions:**
- `get_google_routes(start, destination)` — wraps `get_routes()` from google_maps_final
- `enrich_waypoint_with_crime(waypoint)` — adds crime data to one waypoint
- `enrich_route_with_crime(route)` — enriches all waypoints in parallel
- `enrich_all_routes(routes)` — enriches all routes in parallel
- `analyze_route_risk(route)` — sends one route to AI agent, returns score + analysis
- `analyze_all_routes(routes)` — analyzes all routes in parallel
- `build_final_result(routes, analyses)` — merges data, removes waypoints
- `main(start, destination)` — runs the full pipeline

**CLI entry point:** `python src/safe_travels.py` runs a test with Willis Tower -> Navy Pier and saves output to `src/tests/final_result_test.json`.

---

## Environment Variables

All configured in `.env` at the project root:

```
GOOGLE_MAPS_API_KEY=your_key        # Required — Google Maps Directions API
CRIME_API_KEY=your_key              # Required — Crimeometer API
CRIME_API_BASE_URL=https://api.crimeometer.com/v1  # Optional, has default
OPEN_ROUTER_API_KEY=your_key        # Required — OpenRouter for AI agent
LLM_MODEL=openai/gpt-4o-mini       # Optional, has default
```

---

## Testing

### Test Structure

**Phase 3 tests** (`src/tests/test_phase3_agent.py`):

| Test | Type | What It Tests |
|------|------|---------------|
| `test_valid_model` | Unit | RouteRiskAnalysis accepts valid data |
| `test_boundary_low` | Unit | Score = 1 is valid |
| `test_boundary_high` | Unit | Score = 100 is valid |
| `test_score_too_low` | Unit | Score = 0 rejected |
| `test_score_too_high` | Unit | Score = 101 rejected |
| `test_missing_analysis` | Unit | Missing analysis rejected |
| `test_missing_score` | Unit | Missing score rejected |
| `test_agent_with_mock_route` | Integration | Agent returns valid output for mock route |
| `test_agent_returns_reasonable_score` | Integration | Score is reasonable (10-80) for moderate data |
| `test_agent_handles_error_waypoints` | Integration | Agent handles all-error waypoints gracefully |

**Phase 4 tests** (`src/tests/test_phase4_orchestrator.py`):

| Test | Type | What It Tests |
|------|------|---------------|
| `test_date_range_*` (3 tests) | Unit | Date range formatting and 14-day span |
| `test_basic_output_structure` | Unit | Final result has correct keys, no waypoints |
| `test_failed_analysis` | Unit | Failed routes get null score + error |
| `test_multiple_routes` | Unit | Handles multiple routes correctly |
| `test_get_routes_returns_list` | Integration | Google Maps returns routes |
| `test_route_has_expected_keys` | Integration | Routes have all required keys |
| `test_enrich_single_waypoint` | Mocked | Waypoint gets crime_data key |
| `test_enrich_route_all_waypoints` | Mocked | All waypoints in route enriched |
| `test_enrich_route_no_waypoints` | Mocked | Empty waypoint list handled |
| `test_enrich_all_routes_parallel` | Mocked | Multiple routes enriched in parallel |
| `test_full_pipeline_mocked_crime` | Integration | Full pipeline with mocked crime + real AI |
| `test_real_crime_enrichment` | **SKIPPED** | Awaiting private Crimeometer key |
| `test_full_pipeline_real` | **SKIPPED** | Awaiting private Crimeometer key |

### Running Tests

```bash
# Phase 3 — AI Agent tests
pytest src/tests/test_phase3_agent.py -v -s

# Phase 4 — Orchestrator tests
pytest src/tests/test_phase4_orchestrator.py -v -s

# All tests
pytest src/tests/ -v -s

# Manual end-to-end test
python src/safe_travels.py
```

### Test Output Files

Tests save JSON results for inspection:
- `src/tests/phase3_agent_results.json`
- `src/tests/phase4_orchestrator_results.json`
- `src/tests/phase4_full_pipeline_result.json`
- `src/tests/final_result_test.json` (from manual CLI run)

---

## Expected Output Format

The final output from `main()` looks like this:

```json
{
  "test_metadata": {
    "timestamp": "2026-02-15T...",
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
      "analysis": "This route through downtown Chicago presents moderate risk...",
      "status": "success"
    }
  ]
}
```

Key points:
- **No waypoints** in final output (used internally only)
- **risk_score** is always 1-100 (enforced by Pydantic)
- **status** is `"success"` or `"failed"` (with `"error"` key if failed)

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Crime API access | Direct import (not MCP) | Simpler for orchestrator; MCP server still exists for other uses |
| Parallelism | `asyncio.gather()` | Efficient async I/O for multiple API calls |
| Crime function | `get_crime_incidents()` | More detailed data for AI analysis than stats |
| AI framework | PydanticAI with OpenRouter | Structured output via Pydantic model, flexible LLM choice |
| Error handling | Return error dicts, never raise | Pipeline continues even if some waypoints fail |
| Hardcoded crime params | radius=0.25mi, days=14, limit=5 | Consistent analysis across all routes |
