# Manual UI Acceptance Checklist
## The Lenny Growth Assistant

Use this checklist during manual acceptance testing and evaluator walkthroughs.

---

### Phase 1: Application Launch & Telemetry
- [x] **Backend Server Boot:** FastAPI server starts on port 8000 (`python -m uvicorn app.main:app --reload --port 8000`).
- [x] **Database Initialization:** SQLite fallback creates `lenny_growth.db` automatically with tables (`sessions`, `messages`, `artifacts`) when PostgreSQL is not running.
- [x] **Health Check:** `GET http://localhost:8000/health` returns HTTP 200 `{"status": "ok"}`.
- [x] **Readiness Check:** `GET http://localhost:8000/ready` returns indexed chunk count and Ollama connection status.
- [x] **Frontend Launch:** React development server starts on port 5173 (`npm run dev`).
- [x] **Telemetry Indicators:** Sidebar displays connection status (`Connected` in green) and indexed chunk counter (`1,748 chunks`).

---

### Phase 2: Navigation & Welcome Experience
- [x] **Welcome Screen:** Displays hero title *"The Lenny Growth Assistant"* and subtitle *"Turn the world's best product and growth conversations into actionable insights."*
- [x] **Interactive Prompt Cards:** All 4 suggested prompt cards are visible and clickable:
  - *How can startups improve user retention?*
  - *What are the most effective product-led growth strategies?*
  - *How should a product manager prioritize features?*
  - *What makes a successful product launch?*
- [x] **Session Creation:** Clicking `+ New Conversation` creates an independent session in the sidebar.

---

### Phase 3: Conversational RAG & Grounded Citations
- [x] **Submitting Query:** Typing *"How does Brian Chesky prioritize features at Airbnb?"* displays an optimistic user message and shows the pulsing loading indicator.
- [x] **Assistant Grounded Answer:** Assistant responds citing Brian Chesky's philosophy (e.g. staying in the details, single roadmap across the entire company).
- [x] **Citation Pill Badges:** Renders clickable citation chips beneath the response showing guest name (*Brian Chesky*) and episode title (*Brian Chesky's new playbook*).
- [x] **External YouTube Link:** Clicking external link icon navigates to the episode on YouTube.
- [x] **Snippet Drawer:** Clicking a citation expands a verbatim transcript quote.
- [x] **Unsupported Query Honesty:** Asking an unrelated question outside Lenny's podcast triggers explicit boundary acknowledgment rather than hallucinations.

---

### Phase 4: Ship 30 for 30 Essay Skill
- [x] **Trigger Action:** Clicking the *"Ship 30 for 30 Essay (~1,250w)"* button opens a prompt dialog.
- [x] **Authoring Engine:** System executes Dickie Bush and Nicolas Cole's 10-step digital writing framework:
  1. Compelling title
  2. Opening hook
  3. Problem tension
  4. Grounded podcast insights
  5. Narrative progression
  6. Skimmable 1-3-1 headings
  7. Selective bolding
  8. Real examples
  9. Actionable lessons
  10. Concluding takeaway
- [x] **Artifact Link:** Assistant message includes an *"Open Generated Artifact in Side Panel"* trigger button.

---

### Phase 5: Side-by-Side Artifact Studio
- [x] **Panel Appearance:** Artifact Studio docks smoothly on the right side without layout jumping.
- [x] **Preview Tab:** Formats Markdown cleanly with headers, bullet points, and code blocks.
- [x] **Code Tab:** Displays formatted raw code with monospace typography.
- [x] **HTML/CSS Sandboxed Iframe:** When generating an HTML card or dashboard widget:
  - Renders inside an `<iframe>` with `sandbox="allow-popups"` (strictly excluding `allow-scripts` and `allow-same-origin`).
  - Enforces Content Security Policy (`default-src 'none'`).
- [x] **Copy Action:** Copies raw content to clipboard with a 2-second checkmark confirmation.
- [x] **Download Action:** Downloads file (`.md` or `.html`) with sanitized filename.
- [x] **Close Action:** Closes the side panel cleanly.

---

### Phase 6: Session Isolation & History Persistence
- [x] **Session Switching:** Selecting an older conversation loads its exact historical messages and attached artifacts.
- [x] **Session Isolation:** Conversation messages in Session A do not appear in Session B.
- [x] **Session Deletion:** Hovering over a session in the sidebar reveals the trash icon; clicking deletes the session from the database.
- [x] **Browser Refresh:** Refreshing the browser page preserves all conversations, messages, citations, and artifacts.
