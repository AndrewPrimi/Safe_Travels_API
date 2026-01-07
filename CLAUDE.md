# SafeTravels API - AI Assistant Rules

## Project Overview
SafeTravels is a **RAG-powered** B2B cargo theft prevention API that retrieves and synthesizes risk intelligence from crime databases, theft reports, and news sources.

## Core Architecture

```
User Query → Embed → ChromaDB Retrieval → LLM Synthesis → Risk Assessment
```

| Component | Technology |
|-----------|------------|
| Embeddings | SBERT / OpenAI |
| Vector DB | ChromaDB |
| LLM | GPT-4o-mini / Groq |
| Framework | LangChain |
| API | FastAPI |

## Core Development Philosophy

### 1. Think Before You Code
- **EXPLAIN APPROACH**: Before writing code, explain your reasoning
- **RAG FIRST**: Everything goes through the RAG pipeline
- **ROOT CAUSE FOCUS**: Fix underlying issues, not symptoms

### 2. Collaborative Principles
- **COLLABORATE**: Work with the user, don't go rogue
- **ASK FIRST**: If unclear about requirements, ask
- **NO ASSUMPTIONS**: Verify file structure, APIs, data models in code
- **SMALL STEPS**: Minimal, focused changes

### 3. Quality Standards
- **Follow Patterns**: Match existing code style
- **Type Safety**: Use Pydantic models, type hints
- **Document Intent**: Clear docstrings for non-obvious logic

### 4. Important Constraints
- **No Random Docs**: Don't create .md files unless requested
- **Prefer Editing**: Edit existing files over creating new ones
- **Respect Scope**: Only change what's explicitly requested

## Architecture Rules

### RAG Pipeline
- Vector DB: ChromaDB (local)
- Embeddings: SBERT or OpenAI
- LLM: OpenAI GPT-4o-mini or Groq
- Framework: LangChain for orchestration

### API Design
- FastAPI with Pydantic validation
- All endpoints under `/api/v1/`
- Async where possible
- Return JSON with consistent schema

### Database
- PostgreSQL + PostGIS for location data
- ChromaDB for vector storage

## File Structure
```
safetravels/
├── app/
│   ├── main.py          # FastAPI entry
│   ├── config.py        # Settings
│   ├── api/routes.py    # Endpoints
│   ├── api/schemas.py   # Pydantic models
│   └── rag/             # RAG PIPELINE
│       ├── embeddings.py
│       ├── vector_store.py
│       ├── retriever.py
│       └── chain.py
├── data/
│   └── ingest/
└── dashboard/app.py
```

## Key Decisions
| Decision | Choice | Why |
|----------|--------|-----|
| Risk Assessment | RAG + LLM | Contextual, explainable |
| Vector DB | ChromaDB | Simple, local, free |
| LLM | GPT-4o-mini | Fast, cheap, good quality |
| API | FastAPI | Fast, async, auto-docs |
