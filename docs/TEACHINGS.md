# SafeTravels API — Teachings & Learnings

> Understanding the code, what works, what doesn't, and why

**Author:** Snigdha

---

## 📚 Understanding the RAG Architecture

### What is RAG?
**Retrieval-Augmented Generation** combines two things:
1. **Retrieval** — Finding relevant documents from a database
2. **Generation** — Using an LLM to synthesize an answer

```
Traditional LLM:
Query → LLM → Answer (based only on training data)

RAG:
Query → Embed → Search DB → Get Relevant Docs → LLM + Docs → Answer
```

### Why RAG for SafeTravels?
| Problem | How RAG Solves It |
|---------|-------------------|
| LLMs don't know current theft data | Retrieve from our database |
| LLMs hallucinate locations | Ground answers in real documents |
| Can't update LLM with new incidents | Just add docs to vector DB |
| Need source citations | Retrieved docs are the sources |

---

## 🔧 Code Walkthrough

### 1. `main.py` — The Entry Point
```python
app = FastAPI(...)      # Creates the API
app.include_router(...) # Adds all our endpoints
```
**Why this structure?**  
- FastAPI is async-first → fast responses
- Router pattern → organize endpoints by feature

### 2. `config.py` — Settings
```python
class Settings(BaseSettings):
    openai_api_key: Optional[str] = None
    chroma_persist_dir: str = "./chroma_db"
```
**Why Pydantic Settings?**  
- Loads from `.env` automatically
- Type-validated → catches config errors early
- Easy to access anywhere: `from app.config import settings`

### 3. `schemas.py` — Data Validation
```python
class RiskAssessmentRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
```
**Why Pydantic Models?**  
- Auto-validates incoming requests
- Generates API documentation
- Type hints → better IDE support

### 4. `routes.py` — API Endpoints
```python
@router.post("/assess-risk")
async def assess_risk(request: RiskAssessmentRequest):
    # TODO: Call RAG chain here
    return RiskAssessmentResponse(...)
```
**Current state:** Returns mock data  
**Next step:** Connect to RAG chain

---

## 🔴 What Didn't Work (And Why)

### Issue 1: Risk Scoring Consistency
**The challenge:**  
- LLMs can give slightly different answers for the same question
- "Is Dallas safe?" might vary in phrasing each time

**Why this happens:**  
- LLMs are probabilistic by nature
- Temperature setting affects randomness

**How we fix it:**  
- Set `temperature=0.1` for consistent answers
- Add structured extraction after LLM response

### Issue 2: ChromaDB Not Yet Integrated
**Current state:**  
- `vector_store.py` has placeholder code
- Returns mock results

**What's needed:**  
```python
import chromadb
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("safetravels")
```

---

## ⚠️ Common Pitfalls

### 1. Forgetting to Chunk Documents
**Wrong:** Embed entire 50-page PDF as one vector  
**Right:** Split into 500-token chunks with overlap

### 2. Not Setting Temperature
**Problem:** LLM responses too random  
**Fix:** `temperature=0.1` for consistent answers

### 3. Ignoring Rate Limits
**Problem:** OpenAI 429 errors  
**Fix:** Add retry logic with exponential backoff

### 4. Not Caching Embeddings
**Problem:** Re-embedding same docs = wasted API calls  
**Fix:** Use ChromaDB persistence

---

## 🎯 What's Working Now

| Component | Status | Notes |
|-----------|--------|-------|
| FastAPI app | ✅ Works | Returns mock data |
| Pydantic schemas | ✅ Works | Full validation |
| API endpoints | ✅ Works | 10 endpoints defined |
| RAG module structure | ✅ Created | Placeholder logic |

## ❌ What Needs Work

| Component | Status | What's Missing |
|-----------|--------|----------------|
| ChromaDB | ❌ Placeholder | Actual integration |
| Embeddings | ❌ Placeholder | SBERT loading |
| LLM Chain | ❌ Placeholder | LangChain setup |
| Data ingestion | ❌ Not started | FBI data loader |

---

## 📖 Further Reading

- [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/)
- [ChromaDB Getting Started](https://docs.trychroma.com/getting-started)
- [SBERT Documentation](https://www.sbert.net/)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
