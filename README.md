# SafeTravels API

**RAG-Powered Cargo Theft Prevention API**

Real-time risk intelligence using Retrieval-Augmented Generation (RAG) to protect trucking fleets from cargo theft.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API
cd safetravels
uvicorn app.main:app --reload

# Open docs at http://localhost:8000/docs
```

## 🏗️ Architecture

```
User Query → Embed → ChromaDB → LLM → Risk Assessment
```

| Component | Technology |
|-----------|------------|
| **Embeddings** | SBERT / OpenAI |
| **Vector DB** | ChromaDB |
| **LLM** | GPT-4o-mini / Groq |
| **Framework** | LangChain |
| **API** | FastAPI |

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/assess-risk` | POST | Get risk assessment for location |
| `/api/v1/analyze-route` | POST | Analyze route for theft risks |
| `/api/v1/safe-stops` | GET | Find safe parking nearby |
| `/api/v1/query` | POST | Natural language query |

## 📁 Project Structure

```
safetravels/
├── app/
│   ├── main.py          # FastAPI entry
│   ├── config.py        # Settings
│   ├── api/
│   │   ├── routes.py    # Endpoints
│   │   └── schemas.py   # Pydantic models
│   └── rag/             # RAG Pipeline
│       ├── embeddings.py
│       ├── vector_store.py
│       └── chain.py
├── data/
│   └── ingest/
└── dashboard/
```

## 🔑 Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://...
```

## 📊 Status

- [x] API skeleton
- [x] Pydantic schemas
- [ ] ChromaDB setup
- [ ] RAG pipeline
- [ ] LangChain integration
- [ ] Dashboard
