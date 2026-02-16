# Next Steps — Phase 3: PydanticAI Agent

## Current Status

| Phase | Status |
|-------|--------|
| Phase 1 — Crime MCP Server | **COMPLETE** (9/9 tests passing) |
| Phase 2 — Google Maps Helper | **COMPLETE** (adaptive waypoints + traffic) |
| **Phase 3 — PydanticAI Agent** | **UP NEXT** |
| Phase 4 — Orchestrator | Not started |
| Phase 5 — FastAPI Endpoint | Not started |

---

## Phase 3: SafeTravels AI Agent

### What It Does

A PydanticAI agent that takes route waypoints, queries the Crime MCP server for crime data at each point, and returns a structured risk assessment.

**Input:** Route waypoints (list of lat/lng coordinates from Phase 2)
**Output:** `RouteAnalysisResult` — risk score (1-100) + text summary

### Files to Create / Edit

| File | Action |
|------|--------|
| `src/safe_travels_agent.py` | Implement (currently empty) |
| `src/tests/test_phase3_agent.py` | Implement (currently empty) |

### Pre-Implementation Research

Before writing code, study these reference files:

1. `docs/agent_zero.py` — Primary PydanticAI agent reference (MCPServerStreamableHTTP pattern)
2. `docs/Pydantic_AI/agent.py` — Simple MCP connection example
3. `docs/Pydantic_AI/pydantic_ai_docs/agents.md` — System prompts, running agents
4. `docs/Pydantic_AI/pydantic_ai_docs/output.md` — Structured output types
5. `docs/Pydantic_AI/pydantic_ai_docs/mcp_client.md` — MCPServerStreamableHTTP usage

### Key Components

1. **Output Type** — `RouteAnalysisResult` Pydantic model
   - `risk_score`: int (1-100)
   - `risk_summary`: str (50-500 chars)

2. **Agent Input** — `RouteAnalysisInput` dataclass
   - route_id, summary, distance_miles, duration_minutes, waypoints

3. **LLM Config** — OpenRouter via PydanticAI's OpenAI provider
   - Model: `openai/gpt-4o-mini` (configurable via `LLM_MODEL` env var)
   - Key: `OPEN_ROUTER_API_KEY`

4. **MCP Connection** — `MCPServerStreamableHTTP(url="http://localhost:8001/mcp")`
   - Connects to the Phase 1 Crime MCP server
   - Uses `agent.run_mcp_servers()` context manager

5. **System Prompt** — Instructs the agent to:
   - Query crime data for each waypoint via MCP tools
   - Aggregate findings (total incidents, crime types, hotspots)
   - Calculate a 1-100 risk score based on volume, severity, concentration
   - Write a concise summary with key risk areas and recommendations

6. **SafeTravelsAgent Class** — Wraps the agent with an `analyze_route()` async method

### Environment Variables Required

```
OPEN_ROUTER_API_KEY=your_openrouter_key
LLM_MODEL=openai/gpt-4o-mini          # optional, has default
CRIME_MCP_URL=http://localhost:8001/mcp # optional, has default
```

### How to Test

```bash
# 1. Start the Crime MCP server (terminal 1)
python -m src.MCP_Servers.crime_mcp

# 2. Run Phase 3 tests (terminal 2)
pytest src/tests/test_phase3_agent.py -v -s
```

### Completion Criteria

- [ ] `SafeTravelsAgent` class implemented in `src/safe_travels_agent.py`
- [ ] Agent connects to Crime MCP server via MCPServerStreamableHTTP
- [ ] Agent uses `output_type=RouteAnalysisResult` for structured output
- [ ] System prompt is comprehensive (scoring scale, analysis steps, rules)
- [ ] `analyze_route()` returns `{route_id, risk_score, risk_summary, status}`
- [ ] All tests in `test_phase3_agent.py` pass

---

## After Phase 3

### Phase 4: Orchestrator (`src/safe_travels.py`)

- Calls `get_routes()` from Phase 2 to get route alternatives
- Converts route data to agent input format
- Runs agent analysis for all routes **in parallel** via `asyncio.gather()`
- Handles timeouts and partial failures
- Returns consolidated results

### Phase 5: FastAPI (`src/safe_travels_api.py`)

- `POST /analyze-route` endpoint accepting `{start, destination}`
- Calls the Phase 4 orchestrator
- Returns `{routes: [{route_id, risk_score, risk_summary, status}]}`
- Health check at `GET /health`
- OpenAPI docs at `GET /docs`
