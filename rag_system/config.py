"""
config.py - Central configuration for the MAVLink RAG system.
All tunable parameters and path definitions live here.
"""

import os
from pathlib import Path

# ── Base directory ─────────────────────────────────────────────────────────────
BASE_DIR = Path(os.environ.get("MAVLINK_KB_DIR", "C:/Users/Ranindu/Desktop/Mavlink-Knowledge"))

# ── Source folders to index ────────────────────────────────────────────────────
SOURCE_DIRS = [
    BASE_DIR / "Protocol" / "message_definitions" / "v1.0",  # XML message defs
    BASE_DIR / "Ardupilot" / "copter" / "source" / "docs",   # Copter markdown
    BASE_DIR / "Ardupilot" / "dev" / "source" / "docs",      # Dev markdown
    BASE_DIR / "Guides" / "en",                               # Guide markdown
    BASE_DIR / "Code" / "dialects" / "v20",                   # Python dialect files
    BASE_DIR / "Code",                                         # mavutil.py etc.
]

# File extensions to index (images/static assets are excluded by omission)
ALLOWED_EXTENSIONS = {".md", ".py", ".xml", ".rst", ".txt"}

# ── Index / cache paths ────────────────────────────────────────────────────────
INDEX_DIR = BASE_DIR / "rag_system" / "index"
FAISS_INDEX_PATH = INDEX_DIR / "faiss.index"
CHUNKS_PATH = INDEX_DIR / "chunks.json"

# ── Chunking parameters ────────────────────────────────────────────────────────
CHUNK_SIZE_WORDS = 400        # target words per chunk
CHUNK_OVERLAP_WORDS = 50      # overlap between consecutive chunks

# ── Embedding model ────────────────────────────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ── Search defaults ────────────────────────────────────────────────────────────
DEFAULT_TOP_K = 5

# ── API settings ──────────────────────────────────────────────────────────────
API_HOST = "0.0.0.0"
API_PORT = 8765
