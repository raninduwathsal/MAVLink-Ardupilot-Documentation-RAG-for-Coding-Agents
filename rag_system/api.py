"""
api.py - FastAPI server exposing the MAVLink RAG knowledge base.

Endpoints
---------
GET  /search?q=...&top_k=5   → top matching chunks
GET  /answer?q=...&top_k=5   → synthesised answer from top chunks
GET  /health                  → liveness check
POST /tool/search_mavlink_docs → MCP-style tool endpoint
"""

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import uvicorn
import logging

from config import API_HOST, API_PORT, DEFAULT_TOP_K
from embedder import search as vector_search, load_index

# -- App init ------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("rag_api")
app = FastAPI(
    title="MAVLink Knowledge RAG API",
    description="Local RAG system for MAVLink & ArduPilot documentation",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# -- Pydantic models ----------------------------------------------------------
class SearchResult(BaseModel):
    text: str
    source: str
    title: str = ""
    score: float


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]


class AnswerResponse(BaseModel):
    query: str
    answer: str
    sources: List[str]


class ToolRequest(BaseModel):
    query: str
    top_k: int = Field(default=DEFAULT_TOP_K, ge=1, le=20)


# -- Startup ------------------------------------------------------------------
@app.on_event("startup")
async def startup_load_index():
    """Pre-load FAISS index into memory on server start."""
    try:
        load_index()
    except FileNotFoundError as e:
        print(f"  [!] {e}")
        print("  The API will return errors until the index is built.")


# -- Endpoints ----------------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/search", response_model=SearchResponse)
async def search_endpoint(
    q: str = Query(..., description="Search query"),
    top_k: int = Query(DEFAULT_TOP_K, ge=1, le=20),
):
    """Return top-k relevant text chunks for the query."""
    results = vector_search(q, top_k=top_k)
    return SearchResponse(
        query=q,
        results=[SearchResult(**r) for r in results],
    )


@app.get("/answer", response_model=AnswerResponse)
async def answer_endpoint(
    q: str = Query(..., description="Question to answer"),
    top_k: int = Query(DEFAULT_TOP_K, ge=1, le=20),
):
    """
    Retrieve top chunks and synthesise a concatenated answer.
    The chunks are combined with source attribution so an LLM or
    downstream consumer can use them as grounded context.
    """
    results = vector_search(q, top_k=top_k)

    if not results:
        return AnswerResponse(
            query=q,
            answer="No relevant information found in the knowledge base.",
            sources=[],
        )

    # Build a context block from retrieved chunks
    context_parts = []
    sources = []
    for i, r in enumerate(results, 1):
        src_label = r["source"].split("Mavlink-Knowledge")[-1].lstrip("/\\")
        header = f"--- Source {i}: {src_label}"
        if r.get("title"):
            header += f" | {r['title']}"
        header += f" (score: {r['score']}) ---"
        context_parts.append(f"{header}\n{r['text']}")
        sources.append(r["source"])

    answer = (
        f"Based on {len(results)} relevant passages from the MAVLink / ArduPilot "
        f"knowledge base:\n\n" + "\n\n".join(context_parts)
    )

    return AnswerResponse(query=q, answer=answer, sources=sources)


@app.post("/tool/search_mavlink_docs", response_model=SearchResponse)
async def tool_search(body: ToolRequest):
    """
    MCP-style tool endpoint.

    Usage from an AI agent:
        search_mavlink_docs(query="How does HEARTBEAT work?")
    """
    results = vector_search(body.query, top_k=body.top_k)
    return SearchResponse(
        query=body.query,
        results=[SearchResult(**r) for r in results],
    )


@app.get("/browse")
async def browse_docs(type: Optional[str] = None):
    """
    List all documents or filter by type (e.g., 'message', 'enum', 'markdown').
    This enables the 'browse' functionality requested by the user.
    """
    _, chunks = load_index()
    
    unique_sources = {}
    for c in chunks:
        src = c["source"]
        if src not in unique_sources:
            unique_sources[src] = {
                "source": src,
                "label": src.split("Mavlink-Knowledge")[-1].lstrip("/\\"),
                "title": c.get("title", "Untitled"),
                "type": "xml" if src.endswith(".xml") else "markdown" if src.endswith(".md") else "other"
            }
            
    # Convert to list
    docs = list(unique_sources.values())
    
    if type:
        docs = [d for d in docs if d["type"] == type]
        
    return {"documents": docs, "total": len(docs)}


# -- Direct run ---------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("api:app", host=API_HOST, port=API_PORT, reload=False)
