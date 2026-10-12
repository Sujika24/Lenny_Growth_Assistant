# THE LENNY GROWTH ASSISTANT

> **Production-grade AI conversational platform that transforms Lenny's Podcast transcripts into an intelligent, source-grounded product management and growth knowledge assistant.**

---

## 🌟 Overview & Key Capabilities

**The Lenny Growth Assistant** is a full-stack, dual-pane AI workspace combining the conversational simplicity of ChatGPT with the side-by-side artifact preview experience of Claude Artifacts. It gives product managers, growth leads, and founders immediate access to hard-won playbooks extracted from over 300 deep-dive episodes of *Lenny's Podcast*.

### Core Capabilities:
1. **Source-Grounded Answers:** Semantic vector retrieval via ChromaDB over cleaned, chunked podcast transcripts with explicit citations linking to verified episodes and YouTube timestamps.
2. **Zero Hallucination Honesty:** Explicit acknowledgement of knowledge boundaries when evidence is absent from the transcript corpus.
3. **Ship 30 for 30 Essay Authoring Skill:** Generates comprehensive ~1,250-word deep-dive essays implementing Dickie Bush and Nicolas Cole's official 10-step digital writing framework.
4. **Side-by-Side Artifact Studio:** Real-time generation and preview of Markdown strategy docs / PRDs and standalone HTML/CSS interactive dashboard widgets.
5. **Secure HTML Sandboxing:** Untrusted HTML artifacts run inside an isolated `<iframe>` with strict Content Security Policy (`default-src 'none'`) and no `allow-scripts` or `allow-same-origin`.
6. **Flexible Provider Runtime:** Switch between 100% offline Local Ollama (`llama3.2:3b` / `qwen2.5:3b`) and Cloud Anthropic Claude (demonstrable Agent SDK tool use).
7. **Resilient Persistence:** PostgreSQL database with Alembic migrations and seamless local SQLite fallback for evaluators running without Docker.

---

## 🏗️ Architecture Summary

```
[ React + Vite + TypeScript + Tailwind CSS Frontend (Port 5173 / 3000) ]
                            |
                     REST API (HTTP)
                            v
[ FastAPI Backend (Port 8000) ]
    ├── Agent Orchestrator & Provider Adapter
    ├── Dedicated Skills: Ship 30 Essay (~1,250w), Artifact Studio (HTML/MD)
    ├── RAG Engine: ChromaDB (1,700+ indexed chunks across 60+ episodes)
    └── Database: PostgreSQL 16 (Docker) / SQLite (Local Dev Fallback)
```

---

## 📋 Prerequisites

- **Python:** 3.10+ (Tested on Python 3.13)
- **Node.js:** v18+ (Tested on Node.js v25) & npm
- **Ollama:** Installed and running locally (`ollama serve`). Model: `llama3.2:3b` or `qwen2.5:3b`.
- **Docker & Docker Compose (Optional):** For containerized deployment.

---

## 🚀 Quickstart Guide (Local Development)

### 1. Clone & Setup Environment
```bash
git clone https://github.com/varshinisenthilkumar2211-ship-it/web-interface-project.git
cd LENNY_Assist
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv backend/venv

# Activate virtual environment
# Windows:
backend\venv\Scripts\activate
# Linux/macOS:
source backend/venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 3. Verify Local Ollama
Ensure Ollama is running and has `llama3.2:3b` (or `qwen2.5:3b`):
```bash
ollama list
# If not pulled yet:
ollama pull llama3.2:3b
```

### 4. Index Transcript Knowledge Base
The repository includes 303 episodes in `data/lenny_repo/episodes/`. To index 60 episodes into ChromaDB:
```bash
python scripts/ingest_transcripts.py --limit 60
```
*(To index the entire 303-episode catalog, omit the `--limit` flag).*

### 5. Launch Backend Server
```bash
python -m uvicorn app.main:app --reload --port 8000
```
- Health Check: `http://localhost:8000/health`
- Readiness & Vector Store Telemetry: `http://localhost:8000/ready`
- Interactive Swagger API Docs: `http://localhost:8000/docs`

### 6. Launch Frontend
In a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🐳 Docker Compose Deployment

If Docker and Docker Desktop are running:
```bash
docker compose up --build -d
```
- **Frontend:** `http://localhost:3000`
- **Backend API:** `http://localhost:8000`
- **PostgreSQL:** Port 5432
- **Persistent Storage:** Volumes `postgres_data` and `chroma_data` are persisted.

---

## 🧪 Automated Testing

Run the automated test suite covering all 14 required failure paths:
```bash
# From project root:
backend/venv/Scripts/python.exe -m pytest backend/tests -v
```

### Verified Test Cases (15/15 Passed):
- `test_provider_routing`: Ollama vs. Anthropic provider switching.
- `test_missing_api_keys`: Graceful reporting when cloud keys are omitted.
- `test_ollama_connection_failures`: Actionable guidance if local service stops.
- `test_model_timeout_handling`: Catches LLM timeouts without server crashes.
- `test_invalid_request_validation`: Pydantic 422 error handling.
- `test_empty_retrieval_behavior`: Graceful fallback when queries yield zero matches.
- `test_source_citation_preservation`: Verification of guest names, titles, and URLs.
- `test_cleaner_removes_sponsors`: Automatic filtering of podcast advertisements.
- `test_session_creation`: UUID assignment and database initialization.
- `test_session_isolation`: Absolute boundary enforcement across conversations.
- `test_conversation_persistence`: Multi-turn chronological conversation history.
- `test_database_error_handling`: 404 and structured exception formatting.
- `test_essay_skill_routing`: Ship 30 for 30 ~1,250-word 10-step authoring framework.
- `test_artifact_persistence`: Relational foreign keys linking artifacts to messages.
- `test_unsafe_html_isolation_rules`: Verification of strict CSP and sandboxing policies.

---

## 🎥 2–3 Minute Evaluator Demo Script

### 0:00–0:30 — Problem & Objective
> "Hi everyone. Today product managers and founders spend dozens of hours searching through podcasts to extract tactical advice. The Lenny Growth Assistant transforms 300+ episodes of Lenny's Podcast into an evidence-grounded AI knowledge assistant that produces verifiable answers, publishable Ship 30 for 30 essays, and Claude-style side-by-side artifacts."

### 0:30–1:10 — Grounded Conversational Answering
> "I'll ask: *'How does Brian Chesky prioritize features at Airbnb?'*. 
> Notice how the assistant retrieves actual transcript dialogue, explains how Brian stays in the details across a single company roadmap, and gives verifiable citations citing Brian Chesky's episode with verbatim transcript snippets."

### 1:10–1:40 — Ship 30 for 30 Essay Skill
> "Next, I click *'Ship 30 for 30 Essay'* and enter *'Founder-led roadmaps'*.
> The system runs our dedicated Ship 30 writing skill based on Dickie Bush and Nicolas Cole's framework, authoring a structured ~1,250-word deep-dive essay featuring an opening hook, problem tension, transcript-grounded insights, skimmable 1-3-1 headings, and actionable takeaways."

### 1:40–2:10 — Side-by-Side Artifact Studio
> "Beside the chat, our Artifact Studio opens. Here we can toggle between the rich Preview and the raw Code tab, copy the document, or download it as Markdown. For visual widgets like an HTML Prioritization Matrix, it renders safely inside a sandboxed iframe with strict Content Security Policy and zero cookie access."

### 2:10–2:30 — Local Ollama & Architectural Trade-offs
> "This entire demonstration ran 100% locally on our machine using Ollama and local vector embeddings. One key architectural trade-off we made was using a resilient dense semantic feature projection for ChromaDB embeddings: it eliminated external network timeout risks during startup while preserving high cosine similarity retrieval accuracy."

---

## 🛡️ Security & Sandboxing Threat Model

- **HTML Iframe Isolation:** All HTML/CSS artifacts are rendered inside an `<iframe>` configured with `sandbox="allow-popups"` (strictly omitting `allow-scripts`, `allow-same-origin`, and `allow-forms`).
- **Content Security Policy (CSP):** Injected directly into the iframe `<head>`:
  `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data: https:; font-src data:;">`
- **Zero Parent Access:** The rendered HTML cannot access parent cookies, `localStorage`, `sessionStorage`, or the host DOM.
- **Markdown Sanitization:** Client-side parsing uses DOMPurify to strip arbitrary `<script>` tags and inline event handlers.
- **SQL Injection Prevention:** All database operations utilize SQLAlchemy ORM with safe parameterized queries.

---

## 📄 License & Attribution
- Transcripts sourced from [ChatPRD/lennys-podcast-transcripts](https://github.com/ChatPRD/lennys-podcast-transcripts).
- Built with Python, FastAPI, React, Vite, Tailwind CSS, ChromaDB, and Ollama.
