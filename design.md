# UI/UX Design Specification
## The Lenny Growth Assistant

**Document Version:** 1.0.0  
**Status:** Approved Specification  
**Design System:** Lenny Dark Slate & Electric Indigo  

---

## 1. Design Philosophy

The Lenny Growth Assistant is designed to evoke the precision, focus, and polish of modern high-tier AI developer workspaces (such as Claude Artifacts, Linear, and Raycast). 

### Guiding Principles:
1. **Content Over Chrome:** Subtle borders, glassmorphic card overlays, and dark navy backdrops place the focus squarely on high-signal product insights and generated artifacts.
2. **Cognitive Clarity:** Dense transcript citations and multi-step essays are structured with clear hierarchy, distinct badge chips, and rhythmic typographic spacing.
3. **Frictionless Dual-Pane Workflow:** The chat and artifact viewers coexist seamlessly without jarring layout jumps, allowing iterative refinement of documents and HTML prototypes.
4. **Resilient Feedback:** Every network request, retrieval step, and model generation phase provides real-time visual feedback and graceful error diagnostics.

---

## 2. Color Palette & Design Tokens

A tailored, high-contrast dark aesthetic built on HSL/Hex color tokens:

### 2.1 Neutral Foundation
- **Background Deep:** `#0B0F19` (Canvas base / App root)
- **Background Surface / Sidebar:** `#111827` (Side navigation and panel headers)
- **Background Card / Bubble (Assistant):** `#1E293B` (Elevated assistant response container)
- **Background Bubble (User):** `#312E81` (Deep Indigo user prompt container)
- **Borders & Dividers:** `#334155` (Subtle 1px boundaries)
- **Muted Hover Surface:** `#1E293B` / `#374151`

### 2.2 Brand & Semantic Accents
- **Primary Violet:** `#8B5CF6` (Buttons, brand highlights, active state indicators)
- **Accent Indigo:** `#6366F1` (Focus rings, secondary actions, active session pill)
- **Electric Cyan:** `#06B6D4` (Citation links, artifact badge indicators, verified source tags)
- **Success Emerald:** `#10B981` (Connection active, system ready, copy confirmed)
- **Warning Amber:** `#F59E0B` (Retrieval threshold notice, local fallback active)
- **Destructive Rose:** `#F43F5E` (Connection dropped, error toast, clear session)

### 2.3 Typography Scale
- **Font Family:** `Inter`, `Plus Jakarta Sans`, system-ui, -apple-system, sans-serif
- **Monospace Family:** `JetBrains Mono`, `Fira Code`, monospace (for code artifacts & YAML inspector)
- **Sizes:**
  - Display Title: `24px` / `1.5rem` (`font-bold`, tracking tight)
  - Section Headings: `18px` / `1.125rem` (`font-semibold`)
  - Body Text: `14px` / `0.875rem` (`leading-relaxed`, color `#E2E8F0`)
  - Microcopy / Badges: `12px` / `0.75rem` (`font-medium`, tracking wide)

---

## 3. Information Architecture & Layout Structure

The desktop application employs an adaptive 3-column layout:

```
+------------------------------------------------------------------------------------------------------+
|                                   THE LENNY GROWTH ASSISTANT                                         |
+---------------------+---------------------------------------------------+----------------------------+
| LEFT SIDEBAR        | CENTER CHAT WORKSPACE                             | RIGHT ARTIFACT STUDIO      |
| [260px Fixed]       | [Flexible Flex-1]                                 | [480px-600px Toggleable]   |
|                     |                                                   |                            |
| * Logo & Title      | * Active Header (Session Title & Provider Badge)  | * Artifact Title & Meta    |
| * [+ New Chat]      | * Welcome Screen (when empty):                    | * [Preview Tab] [Code Tab] |
| * Session History   |   - Hero Title & Subtitle                         | * [Copy] [Download] [X]    |
|   - Today           |   - 4 Interactive Prompt Cards                    | * Content Canvas:          |
|   - Previous 7 Days | * Message Feed:                                   |   - Sandboxed <iframe>     |
| * Knowledge Base    |   - User Query Bubble                             |     (HTML/CSS rendering)   |
|   Status Chip       |   - Grounded Assistant Response                   |   - Syntax Highlighted     |
| * Model Provider    |   - Verified Citations (Guest, Episode, Time)     |     Markdown Viewer        |
|   Selector (Ollama/ | * Generation Action Bar:                          |                            |
|   Claude/OpenAI)    |   - [Generate Essay] [Create Artifact]            |                            |
| * Settings / Health | * Input Bar:                                      |                            |
|   Connection Status |   - Auto-resizing Textarea + Send Button          |                            |
+---------------------+---------------------------------------------------+----------------------------+
```

---

## 4. Component Specifications

### 4.1 Left Sidebar
- **Header:** Lenny Growth Assistant logo with electric cyan glow badge.
- **New Session Trigger:** Elevated pill button `+ New Chat` with keyboard shortcut hint (`Cmd/Ctrl + K`).
- **Session List:** Chronologically grouped (`Today`, `Yesterday`, `Older`). Active session highlighted with subtle indigo border and soft violet background. Hover triggers delete icon.
- **Provider Selector:** Dropdown switch between:
  - Local Ollama (`llama3.2:3b` / `qwen2.5:3b`)
  - Anthropic Cloud (`claude-3-5-sonnet-20241022`)
  - OpenAI Cloud (`gpt-4o`)
- **System Telemetry:** Real-time indicator dot:
  - Green: Ollama / Cloud API ready, ChromaDB indexed.
  - Amber: Knowledge base indexing in progress.
  - Red: Host service disconnected with actionable tooltip.

### 4.2 Center Chat Area
- **Welcome Hero:** Displayed when active session contains zero messages:
  - **Title:** The Lenny Growth Assistant
  - **Subtitle:** "Turn the world's best product and growth conversations into actionable insights."
  - **Quick-Start Prompts:**
    1. *"How can startups improve user retention?"*
    2. *"What are the most effective product-led growth strategies?"*
    3. *"How should a product manager prioritize features?"*
    4. *"What makes a successful product launch?"*
- **Message List:**
  - User messages aligned right with deep indigo background.
  - Assistant messages formatted in GitHub-flavored Markdown with table support and code highlighting.
  - **Citations Container:** Clickable pill tags underneath assistant answers listing Guest Name (e.g. `Brian Chesky`), Episode Title (`Brian Chesky's new playbook`), and expandable transcript evidence drawer.
- **Action Toolbar:** Fast-action buttons positioned directly above the input box:
  - `Generate Ship 30 for 30 Essay`: Automatically transforms the current topic into a ~1,250-word deep-dive essay.
  - `Generate HTML Dashboard / Card`: Produces an interactive HTML/CSS visualization.
- **Chat Input:** Multi-line text field supporting `Shift+Enter` for newline and `Enter` to submit.

### 4.3 Right Artifact Studio
- Opens automatically whenever an assistant response generates an artifact, or when the user clicks an artifact reference.
- **Tabs:**
  - `Preview`: Renders Markdown with rich formatting or HTML/CSS inside a secure `<iframe>`.
  - `Code`: Displays raw source code with line numbers and syntax highlighting.
- **Header Actions:**
  - `Copy`: Copies formatted content to clipboard with 2-second checkmark confirmation.
  - `Download`: Exports file as `.md` or `.html` with sanitized title filename.
  - `Close`: Minimizes panel back to chat canvas.

---

## 5. Security & Sandboxing Architecture

To protect against malicious code injection, cross-site scripting (XSS), and unauthorized DOM traversal:

1. **HTML/CSS Artifact Sandbox:**
   - Generated HTML is rendered exclusively inside an `<iframe>`.
   - Attributes: `sandbox="allow-popups"` (strictly excluding `allow-scripts`, `allow-same-origin`, `allow-forms`, and `allow-top-navigation`).
   - Content Security Policy (CSP) injected into iframe `<head>`:
     ```html
     <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data: https:; font-src data:;">
     ```
   - Prevents access to parent cookies, local storage, session storage, or DOM.
2. **Markdown Sanitization:**
   - All parsed Markdown is sanitized using `DOMPurify` to strip arbitrary `<script>` tags, inline event listeners (`onload`, `onerror`), and `javascript:` URIs.

---

## 6. Responsive Breakpoints

| Breakpoint | Target Device | Layout Behavior |
| :--- | :--- | :--- |
| **Desktop ($\ge 1280\text{px}$)** | Widescreen Monitor / Laptop | Full 3-column view: Sidebar (260px) + Chat (Flex) + Artifact Panel (520px). |
| **Tablet ($768\text{px} - 1279\text{px}$)** | iPad / Medium Screens | Collapsible sidebar (hamburger toggle), Chat view fills screen, Artifact panel overlays or docks at 50% width. |
| **Mobile ($< 768\text{px}$)** | Smartphones | 1-column view. Sidebar becomes slide-out drawer; Artifact panel becomes full-screen modal with back button. |

---

## 7. Accessibility & Ergonomics (WCAG 2.1 AA)

- **Contrast Ratios:** Text against background meets or exceeds 4.5:1 (Body text `#E2E8F0` on `#0B0F19` achieves 12.8:1).
- **Keyboard Navigation:** Full tab order across sidebar items, prompt buttons, input textarea, and artifact tabs.
- **Focus Indicators:** 2px high-visibility cyan focus rings (`focus-visible:ring-2 focus-visible:ring-cyan-400`).
- **Screen Reader Support:** Semantic HTML tags (`<nav>`, `<main>`, `<aside>`, `<article>`), ARIA labels on icon-only buttons, and `aria-live="polite"` region for stream generation updates.
