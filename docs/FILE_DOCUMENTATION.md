# SafeTravels API - File Documentation

> Detailed explanation of each file in the project

---

## 📁 Root Level Files

### `MASTER_PLAN.md`
**Purpose:** Project roadmap and architecture overview

**What it does:**
- Defines the RAG-powered architecture
- 8-week sprint plan
- Tech stack decisions
- Deliverables timeline

---

### `CLAUDE.md`
**Purpose:** AI assistant rules file

**What it does:**
- Guidelines for AI tools when working on this project
- Documents RAG architecture
- Coding standards and constraints

---

### `README.md`
**Purpose:** Project documentation for GitHub

**What it does:**
- Quick start guide
- API endpoints list
- Project structure

---

### `requirements.txt`
**Purpose:** Python dependencies

**Key packages:**
| Package | Purpose |
|---------|---------|
| `fastapi` | Web API framework |
| `langchain` | RAG orchestration |
| `chromadb` | Vector database |
| `openai` | LLM for synthesis |
| `sentence-transformers` | Text embeddings |

---

## 📁 `safetravels/app/` - Core Application

### `main.py`
**Purpose:** FastAPI application entry point

**What it does:**
- Creates the FastAPI app
- Configures CORS middleware
- Includes API router

**How to run:**
```bash
cd safetravels
uvicorn app.main:app --reload
```

---

### `config.py`
**Purpose:** Application settings

**Key settings:**
| Setting | Purpose |
|---------|---------|
| `openai_api_key` | LLM access |
| `chroma_persist_dir` | Vector DB storage |
| `embedding_model` | SBERT model name |
| `retrieval_k` | Docs to retrieve |

---

## 📁 `safetravels/app/api/` - API Layer

### `schemas.py`
**Purpose:** Pydantic models for request/response

**Key models:**
| Model | Purpose |
|-------|---------|
| `RiskAssessmentRequest` | Location + query input |
| `RiskAssessmentResponse` | Risk + explanation + sources |
| `QueryRequest` | Natural language question |
| `QueryResponse` | RAG-generated answer |

---

### `routes.py`
**Purpose:** API endpoint definitions

**Endpoints:**
| Endpoint | What it does |
|----------|--------------|
| `/api/v1/assess-risk` | RAG risk assessment |
| `/api/v1/analyze-route` | Route analysis |
| `/api/v1/query` | Natural language query |
| `/api/v1/safe-stops` | Find safe parking |
| `/api/v1/incidents` | Report incidents |

---

## 📁 `safetravels/app/rag/` - RAG Pipeline

### `embeddings.py`
**Purpose:** Text embedding service

**What it does:**
- Converts text to vectors
- Supports SBERT or OpenAI embeddings
- Used for query and document embedding

---

### `vector_store.py`
**Purpose:** ChromaDB operations

**What it does:**
- Stores document embeddings
- Retrieves similar documents
- Manages collections

---

### `chain.py`
**Purpose:** LangChain RAG chain

**What it does:**
- Combines retrieval + LLM
- Generates risk assessments
- Answers natural language queries

**Key methods:**
| Method | Purpose |
|--------|---------|
| `assess_risk()` | Location risk assessment |
| `answer_query()` | NL question answering |
| `analyze_route()` | Route risk analysis |

---

## 🔄 How Files Connect

```
User Request
     │
     ▼
routes.py (API endpoint)
     │
     ▼
chain.py (RAG chain)
     │
     ├── embeddings.py (embed query)
     │
     ├── vector_store.py (retrieve docs)
     │
     └── LLM (synthesize answer)
     │
     ▼
Response (risk + explanation + sources)
```

---

## ✅ What's Working Now

| Component | Status |
|-----------|--------|
| FastAPI app | ✅ Runs |
| All endpoints | ✅ Return mock data |
| RAG module structure | ✅ Created |

## ❌ What Needs Implementation

| Component | Status |
|-----------|--------|
| ChromaDB integration | ❌ TODO |
| SBERT embeddings | ❌ TODO |
| LangChain chain | ❌ TODO |
| Data ingestion | ❌ TODO |
| Dashboard | ❌ TODO |
