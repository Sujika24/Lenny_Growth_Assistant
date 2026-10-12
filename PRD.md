# Product Requirements Document (PRD)
## The Lenny Growth Assistant

**Document Version:** 1.0.0  
**Status:** Approved / In Implementation  
**Target Completion:** October 12, 2026  
**System Architecture Lead & AI Engineer:** Senior Full-Stack AI Engineer

---

## 1. Executive Summary & Vision

**The Lenny Growth Assistant** is a production-grade, full-stack AI conversational platform that transforms Lenny Rachitsky's podcast transcript corpus (300+ episodes featuring premier product, growth, and company-building leaders) into an intelligent, source-grounded product management and growth knowledge assistant.

The platform combines the conversational intelligence of modern chat interfaces with a dual-pane workspace featuring Claude-style interactive artifacts (Markdown documents and sandboxed HTML/CSS widgets) and a specialized **Ship 30 for 30** long-form essay generation skill (~1,250 words). Every factual claim is rigorously grounded in transcript evidence with explicit, verifiable episode citations, eliminating hallucinations and enabling product teams to make evidence-based decisions.

---

## 2. Primary Users & Personas

### 2.1 Product Managers (PMs / Group PMs / VPs of Product)
- **Need:** Tactical frameworks for feature prioritization, roadmap alignment, managing technical debt, and structuring 1:1s and team reviews.
- **Pain Point:** Sifting through hours of podcasts or conflicting online summaries to find actionable advice from leaders like Brian Chesky, Marty Cagan, Shreyas Doshi, or Julie Zhuo.

### 2.2 Growth Managers & Growth Engineers
- **Need:** Real-world playbooks for product-led growth (PLG), retention curves, pricing/packaging experiments, viral loops, and activation funnels.
- **Pain Point:** Lack of concrete numbers and specific operational trade-offs discussed on podcasts that are difficult to search by keyword alone.

### 2.3 Early-Stage Startup Founders & Strategy Teams
- **Need:** Decisive guidance on finding product-market fit (PMF), early customer discovery, hiring the first 10 employees, and fundraising pitch narratives.
- **Pain Point:** Generic AI models provide bland, generalized startup advice rather than hard-won lessons from seasoned operators.

---

## 3. User Problem Statement

1. **Information Fragmentation:** Over 300 deep-dive podcast episodes exist, representing over 400 hours of high-signal dialogue. Keyword search on YouTube or Spotify fails to synthesize cross-episode insights.
2. **Hallucination Risk:** Off-the-shelf LLMs frequently invent quotes, misattribute strategies, or blend unrelated startup stories together without factual attribution.
3. **Synthesis Gap:** PMs and founders need more than chat snippets; they require executive memos, strategy documents, experiment scorecards, and publishable essays to share with their teams.
4. **Local vs. Cloud Flexibility:** Privacy-conscious operators need full offline execution via local Ollama models on consumer hardware, while power users require cloud models (Anthropic Claude).

---

## 4. Proposed Solution

A modern, responsive web application comprising:
1. **Source-Grounded Conversational Chat:** Chat interface powered by ChromaDB vector retrieval across cleaned Lenny's Podcast transcripts with YAML metadata (guest name, episode title, YouTube URL, timestamps).
2. **Explicit Verification & Citation:** Assistant responses link directly to verifiable episode sources. If retrieved evidence is insufficient, the system explicitly acknowledges limitations rather than speculating.
3. **Ship 30 for 30 Long-Form Essay Skill:** An automated authoring engine implementing Dickie Bush and Nicolas Cole's framework to generate structured, compelling ~1,250-word deep dives with hooks, tension, transcript insights, skimmable headings, and tactical takeaways.
4. **Side-by-Side Artifact Studio:** Real-time generation and preview of Markdown strategy docs and HTML/CSS interactive dashboards/experiment cards inside a secure, sandboxed iframe.
5. **Flexible Provider Runtime:** Seamless switching between local Ollama (`qwen2.5:3b` / `llama3.2:3b`) and cloud LLMs (`Claude 3.5 Sonnet` / `GPT-4o`) with demonstrable Anthropic Agent SDK integration.
6. **Session & Message Persistence:** PostgreSQL relational storage with clean Alembic migrations and seamless local SQLite development fallback.

---

## 5. Success Metrics (Target Key Performance Indicators)

| Metric | Target | Measurement Method |
| :--- | :--- | :--- |
| **Citation Relevance Rate** | $\ge 90\%$ | Proportion of PM/Growth queries returning verified transcript citations |
| **Citation Hallucination Rate** | $0\%$ | Manual review of 50 evaluation queries to confirm zero fabricated quotes/guests |
| **Core Flow Success Rate** | $\ge 95\%$ | Automated and acceptance testing across chat, essay, and artifact generation |
| **Unsupported Query Honesty** | $100\%$ | Explicitly stating lack of evidence when asked questions outside transcript corpus |
| **Local Inference Latency** | $< 8\text{s}$ first token | Documented local Ollama response time on consumer GPU/CPU |
| **Session Isolation Integrity** | $100\%$ | Zero data leakage between independent conversation sessions |

---

## 6. Assumptions & Operating Constraints

1. **Transcript Dataset:** Sourced from `ChatPRD/lennys-podcast-transcripts`, consisting of 303 Markdown files with YAML frontmatter containing guest names, titles, URLs, and timestamps.
2. **Local Hardware Constraints:** Host machine runs Windows with Python 3.13 and Node.js 25. Ollama is running with `llama3.2:3b` (and `qwen2.5:3b` configurable). Local vector embeddings use lightweight, high-performance Sentence Transformers (`all-MiniLM-L6-v2`) or ChromaDB default ONNX embeddings to guarantee fast retrieval without GPU exhaustion.
3. **Database Environment:** Docker Compose provides PostgreSQL; for host environments without Docker running, backend includes seamless SQLite ORM fallback to guarantee zero evaluator setup friction.
4. **Authentication:** Anonymous multi-session persistence for MVP, storing session IDs in client storage and database with zero auth overhead for evaluators.
5. **Agent SDK Integration:** Real Anthropic Claude Agent SDK integration utilizing structured tool calling (`search_transcripts`, `generate_essay`, `create_artifact`), backed by an explicit provider adapter for local Ollama models.

---

## 7. Scope & Phasing

### In Scope (MVP Core):
- Full transcript ingestion pipeline (parsing YAML, cleaning sponsor breaks, chunking 700–1000 tokens with overlap, ChromaDB indexing).
- Semantic retrieval pipeline with configurable top-$k$ and cosine similarity filtering.
- Conversational chat with full session context and chat history preservation.
- Source citation engine returning guest, episode title, and transcript evidence snippets.
- Dedicated Ship 30 for 30 essay generation action (~1,250 words, 10-step structure).
- Artifact generation and dual-pane preview for Markdown and HTML/CSS.
- Secure HTML iframe sandboxing (disabling `allow-scripts` and `allow-same-origin`).
- Model selector: Local Ollama vs. Cloud Anthropic / OpenAI.
- PostgreSQL / SQLite database persistence with Alembic migrations.
- REST API (FastAPI) with health checks, session management, and configuration endpoints.
- Modern dark-mode UI (React, Vite, Tailwind CSS, Lucide icons, syntax highlighting).
- Automated Pytest test suite covering RAG, session isolation, routing, and artifact security.
- Docker Compose configuration and step-by-step evaluator documentation.

### Out of Scope (Future Enhancements):
- Multi-user authentication via OAuth2/Auth0.
- Audio playback synchronized to transcript timestamps.
- Live automated web scraping of new YouTube episodes.
- Multi-agent debate between different podcast guests.

---

## 8. Risks and Mitigation Strategies

| Risk | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Hallucination of Quotes/Guests** | High | System prompts enforce strict grounding. If retrieval score is below threshold or chunks are empty, the assistant explicitly states it cannot find evidence in Lenny's podcast. |
| **Malicious HTML/XSS in Artifacts** | Critical | Render HTML artifacts exclusively in an isolated `iframe` with `sandbox="allow-popups"` (no `allow-scripts`, no `allow-same-origin`) and strict Content Security Policy. Sanitize Markdown via DOMPurify. |
| **Local Model Timeout / OOM** | Medium | Implement configurable request timeouts (default 60s), streaming response options, and use lightweight quantized models (`3b` parameter class). |
| **PostgreSQL Unavailable on Host** | Medium | Automated fallback in database connection manager to local SQLite (`lenny_growth.db`) if PostgreSQL port 5432 is unreachable, logging clear diagnostic status. |
| **Prompt Injection via Transcripts** | Medium | Strictly separate retrieved context blocks with XML delimiters (`<transcript_evidence>`) and instruct model that retrieved text is data, not instructions. |

---

## 9. User Acceptance Criteria

1. **User Query Flow:** User selects or types "How does Brian Chesky prioritize features at Airbnb?", receives an answer citing Brian Chesky's episode with verbatim evidence, and sees clickable source pill.
2. **Essay Generation Flow:** Clicking "Generate Essay" triggers the Ship 30 for 30 skill, generating a ~1,250-word structured piece with hook, tension, insights, and actionable lessons displayed in the artifact panel.
3. **Artifact Preview Flow:** User requests a "Feature Prioritization Matrix HTML widget", which opens in the right-hand panel with functional Preview and Code tabs, copyable and downloadable.
4. **Session Persistence Flow:** Refreshing the browser or reopening a previous session in the sidebar restores all previous messages, citations, and artifacts without data loss or session mixing.
5. **Provider Switching Flow:** User can toggle between Local Ollama and Cloud Claude; UI displays active model and indicates readiness status.
