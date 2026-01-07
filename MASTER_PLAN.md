# SafeTravels API — Master Plan

> **RAG-Powered Cargo Theft Prevention**

**Author:** Snigdha  
**Version:** 1.0 | January 2026

---

## 🎯 Project Vision

Build a **RAG-powered API** that provides real-time cargo theft risk intelligence by retrieving and synthesizing relevant data from crime databases, theft reports, and news sources.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        RAG PIPELINE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   [User Query]                                                   │
│        │                                                         │
│        ▼                                                         │
│   ┌─────────────┐                                                │
│   │  Embedding  │  ← SBERT / OpenAI Embeddings                  │
│   └─────────────┘                                                │
│        │                                                         │
│        ▼                                                         │
│   ┌─────────────┐                                                │
│   │  ChromaDB   │  ← Vector Store (theft reports, news, data)   │
│   │  Retrieval  │                                                │
│   └─────────────┘                                                │
│        │                                                         │
│        ▼                                                         │
│   ┌─────────────┐                                                │
│   │    LLM      │  ← GPT-4o-mini / Groq                         │
│   │  Synthesis  │                                                │
│   └─────────────┘                                                │
│        │                                                         │
│        ▼                                                         │
│   [Risk Assessment + Recommendations]                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **API Framework** | FastAPI | REST API endpoints |
| **Embeddings** | SBERT / OpenAI | Convert text to vectors |
| **Vector DB** | ChromaDB | Store and retrieve documents |
| **LLM** | OpenAI GPT-4o-mini / Groq | Generate risk assessments |
| **Framework** | LangChain | RAG orchestration |
| **Database** | PostgreSQL + PostGIS | Store location data |
| **Dashboard** | Streamlit | Demo UI |

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /api/v1/assess-risk` | POST | Get risk assessment for location |
| `POST /api/v1/analyze-route` | POST | Analyze route for theft risks |
| `GET /api/v1/safe-stops` | GET | Find safe parking nearby |
| `POST /api/v1/query` | POST | Natural language query |
| `POST /api/v1/incidents` | POST | Report incident (feedback) |

---

## 📊 Data Sources (For RAG Ingestion)

| Source | Type | Update |
|--------|------|--------|
| FBI UCR Crime Data | Structured | Annual |
| CargoNet Reports | PDF/Text | Monthly |
| FreightWaves News | Scraped | Daily |
| OpenStreetMap | Structured | Real-time |
| Truck Stop Reviews | Scraped | Weekly |

---

## 🔄 RAG Pipeline Details

### 1. Document Ingestion
```
FBI Data → Parse → Chunk → Embed → ChromaDB
News Articles → Scrape → Chunk → Embed → ChromaDB
Theft Reports → Extract → Chunk → Embed → ChromaDB
```

### 2. Query Flow
```
User: "Is this truck stop in Dallas safe at night?"
       │
       ▼
Embed query → Search ChromaDB → Top 5 relevant docs
       │
       ▼
Send to LLM: "Based on these documents, assess risk..."
       │
       ▼
LLM Response: "This location has moderate risk due to..."
```

### 3. Response Format
```json
{
  "location": {"lat": 32.77, "lon": -96.79},
  "risk_level": "moderate",
  "assessment": "This truck stop has seen 2 reported incidents in the past 6 months. The area has elevated crime rates for the county. Recommend parking in well-lit areas.",
  "sources": [
    {"title": "FBI Crime Data - Dallas County", "relevance": 0.89},
    {"title": "FreightWaves - Texas Theft Alert", "relevance": 0.76}
  ],
  "recommendations": [
    "Park in well-lit areas near entrance",
    "Consider alternative: Pilot #4521 (8 miles, lower risk)"
  ]
}
```

---

## 📅 2-Month Sprint Plan

### Phase 1: Data Pipeline (Weeks 1-2)

| Week | Tasks |
|------|-------|
| **Week 1** | - Set up ChromaDB<br>- Ingest FBI crime data<br>- Basic embedding pipeline |
| **Week 2** | - News scraper (FreightWaves)<br>- Truck stop data from OSM<br>- Document chunking |

### Phase 2: RAG Core (Weeks 3-4)

| Week | Tasks |
|------|-------|
| **Week 3** | - LangChain RAG chain<br>- Query endpoint<br>- Basic risk assessment |
| **Week 4** | - Route analysis<br>- Safe stop finder<br>- Response formatting |

### Phase 3: API & Dashboard (Weeks 5-6)

| Week | Tasks |
|------|-------|
| **Week 5** | - FastAPI endpoints<br>- Streamlit dashboard<br>- Map visualization |
| **Week 6** | - Natural language queries<br>- UI polish<br>- Testing |

### Phase 4: Demo Prep (Weeks 7-8)

| Week | Tasks |
|------|-------|
| **Week 7** | - Edge cases<br>- Performance tuning<br>- Documentation |
| **Week 8** | - Demo rehearsal<br>- Pitch deck<br>- Video recording |

---

## 📁 Project Structure

```
safetravels/
├── app/
│   ├── main.py              # FastAPI entry
│   ├── config.py            # Settings
│   ├── api/
│   │   ├── routes.py        # Endpoints
│   │   └── schemas.py       # Pydantic models
│   └── rag/                  # RAG PIPELINE
│       ├── embeddings.py    # Embedding functions
│       ├── vector_store.py  # ChromaDB operations
│       ├── retriever.py     # Document retrieval
│       └── chain.py         # LangChain RAG chain
├── data/
│   ├── ingest/
│   │   ├── fbi_loader.py    # FBI data ingestion
│   │   ├── news_scraper.py  # News scraping
│   │   └── osm_loader.py    # Truck stop data
│   └── processed/
├── dashboard/
│   └── app.py               # Streamlit UI
└── scripts/
    └── ingest_all.py        # Run all ingestion
```

---

## ✅ Deliverables

| Week | Deliverable |
|------|-------------|
| Week 2 | ChromaDB with ingested data |
| Week 4 | Working RAG API (risk assessment) |
| Week 6 | Complete API + Dashboard |
| Week 8 | Demo-ready product |

---

## 🔑 Key Differentiators

| What Others Do | What We Do |
|----------------|------------|
| Static risk databases | **Dynamic RAG retrieval** |
| Manual report lookup | **Natural language queries** |
| Generic location scores | **Contextual explanations** |
| Expensive enterprise tools | **Affordable API** |

---

## 💡 Why RAG?

1. **Natural Language**: Users can ask questions in plain English
2. **Contextual**: Explanations include relevant sources
3. **Up-to-date**: Easy to add new data (just embed and store)
4. **Explainable**: Shows which documents influenced the answer
5. **Flexible**: Can handle any question, not just predefined queries

---

## 📊 Success Metrics

| Metric | Target |
|--------|--------|
| Query latency | < 3 seconds |
| Retrieval accuracy | Top 5 docs relevant |
| API uptime | 99% |
| Demo impressiveness | Incubator approval ✓ |
