# MAVLink Knowledge RAG System

A production-quality local RAG (Retrieval-Augmented Generation) system for MAVLink protocol definitions and ArduPilot documentation.

## Features
- **Structured XML Parsing**: Automatically converts MAVLink XML definitions (messages, enums, fields) into readable text blocks.
- **Semantic Search**: Uses `sentence-transformers` and `FAISS` for high-speed, high-accuracy semantic retrieval.
- **FastAPI Interface**: Provides endpoints for search, context synthesis, and tool-use by AI agents.
- **Persistence**: Caches embeddings and chunks to disk to avoid re-indexing.

---

## 🛠 Setup & Installation

### 1. Prerequisites
- Python 3.9 or higher.
- `pip` (Python package manager).

### 2. Install Dependencies
Navigate to the `rag_system` folder and install the required libraries:
```powershell
pip install -r requirements.txt
```

### 3. Build the Index
Run the indexing script to crawl your documentation folders and build the vector database:
```powershell
python build_index.py
```
*Note: This will take a few minutes the first time as it downloads the `all-MiniLM-L6-v2` model and encodes ~4,000 chunks.*

---

## 🚀 Running the API

Start the FastAPI server:
```powershell
python api.py
```
The server will be available at: **`http://localhost:8765`**

---

## 🤖 Using with VS Code / Antigravity

This system is designed to act as an "External Brain" for your AI coding assistant (like Antigravity).

### 1. Manual Queries
You can use the API directly via browser or `curl`:
- **Search**: `http://localhost:8765/search?q=HEARTBEAT+message+structure`
- **Answer**: `http://localhost:8765/answer?q=What+is+the+purpose+of+MAV_MODE?`

### 2. Tool Integration
Antigravity can use the `POST /tool/search_mavlink_docs` endpoint. If you want the agent to use this automatically, simply tell it:
> "Use the local MAVLink RAG API at localhost:8765 to find information about [Topic]."

The agent will then send a JSON request:
```json
{
  "query": "How do I implement a mission command in Python?",
  "top_k": 5
}
```
And receive structured results including the exact code snippets or message definitions found in the local docs.

---

## 📂 Project Architecture
- `config.py`: Path configurations and model parameters.
- `xml_parser.py`: Logic for converting MAVLink XML into human-readable chunks.
- `loader.py`: Document crawler and text cleaner.
- `chunker.py`: Handles semantic splitting and overlapping.
- `embedder.py`: Core logic for FAISS index and sentence embeddings.
- `api.py`: The FastAPI server exposing search functionality.
- `index/`: Storage for the vector database and metadata.
