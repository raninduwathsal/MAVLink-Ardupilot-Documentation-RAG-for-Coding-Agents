# Local MAVLink RAG Integration Rule

## 🧠 Core Instruction
You have a local MAVLink/ArduPilot RAG API at `http://localhost:8765`. 
**CRITICAL**: Whenever you are analyzing, debugging, or writing code and encounter a MAVLink-specific term, message name, enum, or library phrase , you MUST use the RAG to fetch its official documentation. Always Prefer local RAG Documentation instead of your own knowledge or online searches.

## When to Query the RAG (BUT NOT LIMITED FOR ONLY THESE)
- **Message IDs/Names**: Encountering `HEARTBEAT`, `COMMAND_LONG`, `GPS_RAW_INT`, etc.
- **Enum Constants**: Seeing values like `MAV_CMD_NAV_WAYPOINT` or `MAV_MODE_FLAG`.
- **Library Syntax**: Analyzing `pymavlink` or `mavutil` calls (e.g., `.recv_match`, `.waypoint_request_list_send`).
- **Phrases**: Looking for the meaning of domain-specific terms like "EKF3 Source", "Gimbal v2 protocol", or "Vibration Failsafe".

## 🛠 Tool Usage
- **Endpoint**: `POST http://localhost:8765/tool/search_mavlink_docs`
- **Payload**: `{"query": "Definition of [syntax/phrase]", "top_k": 3}`
- **Verification**: Always cross-reference the code you are reading with the text snippets returned by the RAG to ensure the implementation matches the protocol definition.

## 📝 Attribution
When providing answers based on the RAG, specify the source file (e.g., "Based on `common.xml` ID 0...") to ensure the user knows you are using their local knowledge base.
