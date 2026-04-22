"""
loader.py - Walks source directories and loads document text.
Handles .md, .py, .xml, .rst, .txt files.
HTML tags are stripped from markdown/rst content.
"""

import os
import re
from pathlib import Path
from typing import List, Dict

from config import SOURCE_DIRS, ALLOWED_EXTENSIONS
from xml_parser import parse_mavlink_xml


def strip_html_tags(text: str) -> str:
    """Remove HTML tags from text while preserving content."""
    clean = re.sub(r"<[^>]+>", "", text)
    return clean


def extract_section_title(text: str, file_ext: str) -> str:
    """
    Try to extract the first heading / section title from the document.
    Supports Markdown (#), RST (underline-style), and Python docstrings.
    """
    if file_ext in (".md", ".rst", ".txt"):
        # Markdown heading
        m = re.search(r"^#{1,3}\s+(.+)", text, re.MULTILINE)
        if m:
            return m.group(1).strip()
        # RST underline heading (line followed by ===== or -----)
        m = re.search(r"^(.+)\n[=\-~^]{3,}", text, re.MULTILINE)
        if m:
            return m.group(1).strip()
    if file_ext == ".py":
        # Module docstring
        m = re.search(r'^"""(.+?)"""', text, re.DOTALL)
        if m:
            first_line = m.group(1).strip().split("\n")[0]
            return first_line
    return ""


def load_text_file(file_path: Path) -> Dict:
    """Load a single text file and return its metadata dict."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()
    except Exception as e:
        print(f"  [!] Could not read {file_path}: {e}")
        return None

    ext = file_path.suffix.lower()
    text = strip_html_tags(raw) if ext in (".md", ".rst", ".txt") else raw
    title = extract_section_title(text, ext)

    return {
        "text": text,
        "source": str(file_path),
        "title": title,
        "extension": ext,
    }


def load_all_documents() -> tuple:
    """
    Walk every SOURCE_DIR, load text documents, and parse XML files.

    Returns
    -------
    docs : list[dict]   - raw document dicts  (text, source, title, extension)
    xml_blocks : list[dict] - parsed MAVLink message/enum blocks
    """
    docs: List[Dict] = []
    xml_blocks: List[Dict] = []
    seen_paths: set = set()

    for src_dir in SOURCE_DIRS:
        if not src_dir.exists():
            print(f"  [!] Source directory not found, skipping: {src_dir}")
            continue

        for root, _dirs, files in os.walk(src_dir):
            for fname in files:
                fpath = Path(root) / fname
                if fpath.suffix.lower() not in ALLOWED_EXTENSIONS:
                    continue
                abs_key = str(fpath.resolve())
                if abs_key in seen_paths:
                    continue
                seen_paths.add(abs_key)

                if fpath.suffix.lower() == ".xml":
                    blocks = parse_mavlink_xml(str(fpath))
                    xml_blocks.extend(blocks)
                    print(f"  [v] Parsed XML  {fpath.name}  -> {len(blocks)} blocks")
                else:
                    doc = load_text_file(fpath)
                    if doc and len(doc["text"].strip()) > 20:
                        docs.append(doc)

    print(f"\n  Loaded {len(docs)} text documents, {len(xml_blocks)} XML blocks")
    return docs, xml_blocks
