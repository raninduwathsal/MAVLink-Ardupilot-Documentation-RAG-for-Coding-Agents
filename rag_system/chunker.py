"""
chunker.py - Splits documents and XML blocks into overlapping semantic chunks.

Each chunk is a dict with keys:
    text      – the chunk text
    source    – originating file path
    title     – section / message name (best-effort)
"""

import re
from typing import List, Dict

from config import CHUNK_SIZE_WORDS, CHUNK_OVERLAP_WORDS


def _split_into_words(text: str) -> List[str]:
    """Split text into word tokens (whitespace-based)."""
    return text.split()


def _chunk_text(text: str, source: str, title: str = "") -> List[Dict]:
    """
    Split *text* into overlapping word-level chunks.

    Parameters
    ----------
    text   : full document / block text
    source : file path for attribution
    title  : optional section title attached to every chunk from this doc

    Returns
    -------
    list of chunk dicts
    """
    words = _split_into_words(text)
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = start + CHUNK_SIZE_WORDS
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        chunks.append({
            "text": chunk_text,
            "source": source,
            "title": title,
        })

        # Advance by (size - overlap) so consecutive chunks share `overlap` words
        step = CHUNK_SIZE_WORDS - CHUNK_OVERLAP_WORDS
        if step < 1:
            step = 1
        start += step

    return chunks


def _try_section_split(text: str) -> List[tuple]:
    """
    Attempt to split a markdown/rst doc by headings so chunks align
    with natural sections.  Returns list of (section_title, section_text).
    """
    # Split on markdown headings (## or ###)
    parts = re.split(r"(?m)^(#{1,4}\s+.+)$", text)

    sections = []
    current_title = ""
    current_text = ""

    for part in parts:
        heading_match = re.match(r"^#{1,4}\s+(.+)$", part.strip())
        if heading_match:
            # Save previous section
            if current_text.strip():
                sections.append((current_title, current_text.strip()))
            current_title = heading_match.group(1).strip()
            current_text = ""
        else:
            current_text += part

    if current_text.strip():
        sections.append((current_title, current_text.strip()))

    return sections


def chunk_documents(docs: List[Dict]) -> List[Dict]:
    """
    Chunk a list of raw document dicts into smaller pieces.
    For markdown documents, tries to split on section headings first.
    """
    all_chunks: List[Dict] = []

    for doc in docs:
        text = doc["text"]
        source = doc["source"]
        base_title = doc.get("title", "")
        ext = doc.get("extension", "")

        if ext in (".md", ".rst", ".txt"):
            sections = _try_section_split(text)
            if len(sections) > 1:
                for sec_title, sec_text in sections:
                    title = sec_title or base_title
                    all_chunks.extend(_chunk_text(sec_text, source, title))
            else:
                all_chunks.extend(_chunk_text(text, source, base_title))
        else:
            all_chunks.extend(_chunk_text(text, source, base_title))

    return all_chunks


def chunk_xml_blocks(xml_blocks: List[Dict]) -> List[Dict]:
    """
    Chunk parsed XML blocks (messages / enums).
    Small blocks are kept as single chunks; large ones are split.
    """
    all_chunks: List[Dict] = []

    for block in xml_blocks:
        text = block["text"]
        source = block["source"]
        name = block.get("name", "")
        block_type = block.get("type", "")
        title = f"MAVLink {block_type.capitalize()}: {name}"

        words = _split_into_words(text)
        if len(words) <= CHUNK_SIZE_WORDS + CHUNK_OVERLAP_WORDS:
            # Keep the whole block as one chunk
            all_chunks.append({
                "text": text,
                "source": source,
                "title": title,
            })
        else:
            all_chunks.extend(_chunk_text(text, source, title))

    return all_chunks
