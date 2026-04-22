"""
embedder.py - Builds and queries a FAISS index with sentence-transformer embeddings.

Public API
----------
build_index(chunks)        – encode chunks, save FAISS index + metadata to disk
load_index()               – load from disk (returns index, chunks list)
search(query, top_k)       – search the loaded index, return ranked results
"""

import json
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple, Optional

from config import EMBEDDING_MODEL, FAISS_INDEX_PATH, CHUNKS_PATH, INDEX_DIR, DEFAULT_TOP_K


# -- Module-level singletons ---------------------------------------------------
_model: Optional[SentenceTransformer] = None
_index: Optional[faiss.Index] = None
_chunks: Optional[List[Dict]] = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"  Loading embedding model: {EMBEDDING_MODEL} ...")
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def build_index(chunks: List[Dict]) -> Tuple[faiss.Index, List[Dict]]:
    """
    Encode all chunk texts, build a FAISS IndexFlatIP (inner-product / cosine)
    index, and persist both the index and the chunk metadata to disk.
    """
    global _index, _chunks

    model = _get_model()
    texts = [c["text"] for c in chunks]

    print(f"  Encoding {len(texts)} chunks ...")
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    embeddings = np.array(embeddings, dtype="float32")

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # cosine similarity (vectors are normalised)
    index.add(embeddings)

    # Persist
    os.makedirs(INDEX_DIR, exist_ok=True)
    faiss.write_index(index, str(FAISS_INDEX_PATH))

    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=1)

    _index = index
    _chunks = chunks
    print(f"  [v] FAISS index saved ({index.ntotal} vectors, dim={dim})")
    return index, chunks


def load_index() -> Tuple[faiss.Index, List[Dict]]:
    """Load index and chunk metadata from disk (cached after first call)."""
    global _index, _chunks

    if _index is not None and _chunks is not None:
        return _index, _chunks

    if not FAISS_INDEX_PATH.exists() or not CHUNKS_PATH.exists():
        raise FileNotFoundError(
            "Index files not found. Run `python build_index.py` first."
        )

    _index = faiss.read_index(str(FAISS_INDEX_PATH))
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        _chunks = json.load(f)

    print(f"  [v] Loaded FAISS index ({_index.ntotal} vectors)")
    return _index, _chunks


def search(query: str, top_k: int = DEFAULT_TOP_K) -> List[Dict]:
    """
    Embed *query*, search the FAISS index, and return the top_k results.

    Each result dict contains:
        text   - the chunk text
        source – originating file
        title  – section / message title
        score  – cosine similarity (0-1)
    """
    index, chunks = load_index()
    model = _get_model()

    q_vec = model.encode([query], normalize_embeddings=True).astype("float32")
    scores, indices = index.search(q_vec, top_k)

    results = []
    for rank, (score, idx) in enumerate(zip(scores[0], indices[0])):
        if idx < 0 or idx >= len(chunks):
            continue
        chunk = chunks[idx]
        results.append({
            "text": chunk["text"],
            "source": chunk["source"],
            "title": chunk.get("title", ""),
            "score": round(float(score), 4),
        })

    return results
