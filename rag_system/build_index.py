"""
build_index.py - One-shot script to load documents, chunk them, and build
the FAISS vector index.

Usage:
    cd rag_system
    python build_index.py
"""

import time
from config import FAISS_INDEX_PATH, CHUNKS_PATH
from loader import load_all_documents
from chunker import chunk_documents, chunk_xml_blocks
from embedder import build_index


def main():
    # Check for existing index
    if FAISS_INDEX_PATH.exists() and CHUNKS_PATH.exists():
        print("=" * 60)
        print("  Existing index found.")
        resp = input("  Rebuild? [y/N]: ").strip().lower()
        if resp != "y":
            print("  Skipped. Use the existing index.")
            return

    print("=" * 60)
    print("  STEP 1 / 3 - Loading documents")
    print("=" * 60)
    t0 = time.time()
    docs, xml_blocks = load_all_documents()

    print()
    print("=" * 60)
    print("  STEP 2 / 3 - Chunking")
    print("=" * 60)
    doc_chunks = chunk_documents(docs)
    xml_chunks = chunk_xml_blocks(xml_blocks)
    all_chunks = doc_chunks + xml_chunks
    print(f"  {len(doc_chunks)} doc chunks + {len(xml_chunks)} XML chunks = {len(all_chunks)} total")

    print()
    print("=" * 60)
    print("  STEP 3 / 3 - Building embeddings & FAISS index")
    print("=" * 60)
    build_index(all_chunks)

    elapsed = time.time() - t0
    print()
    print("=" * 60)
    print(f"  Done in {elapsed:.1f}s")
    print(f"  Index: {FAISS_INDEX_PATH}")
    print(f"  Chunks: {CHUNKS_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
