# Agent.md — Build Process & Architecture

## Overview

This document records the AI agent's decisions, reasoning, and the resulting architecture for the **OpenAI Text-to-Speech Web Application**.

---

## 1. Design Decisions

### 1.1 Backend Framework — Flask

**Choice:** Flask (over FastAPI, Django, etc.)

**Rationale:**
- The task explicitly calls for a *lightweight* application. Flask is the de-facto standard for simple Python web apps.
- Flask's built-in `send_file` makes streaming binary responses (audio) straightforward.
- No async requirement — the OpenAI SDK call is blocking and each request is independent, so Flask's synchronous model is perfectly adequate.
- Minimal boilerplate: a single `app.py` file contains all route logic.

### 1.2 Frontend — Static HTML + Vanilla JS + CSS

**Choice:** Single `index.html` template with inline `<script>` block and a separate `style.css`.

**Rationale:**
- The requirement explicitly prohibits heavy frontend frameworks.
- Inline JS avoids an extra HTTP request and keeps the codebase trivially simple.
- A dedicated CSS file keeps style rules maintainable while still being a single static asset.

### 1.3 Voice Instructions Handling

**Choice:** Pass voice instructions directly via the OpenAI `instructions` parameter.

**Rationale:**
- The OpenAI TTS API supports an `instructions` parameter that guides tone, accent, pacing, etc.
- This is cleaner than pre-processing through a separate LLM call — it avoids extra latency, cost, and complexity.
- If the field is left empty, the parameter is simply omitted from the API call.

### 1.4 Audio File Management — In-Memory Streaming

**Choice:** Buffer the OpenAI response into a `BytesIO` object and return it directly.

**Rationale:**
- No temporary files are written to disk, eliminating cleanup concerns entirely.
- Memory usage is bounded by the size of a single audio response (typically < 5 MB).
- Flask's `send_file` accepts file-like objects natively.

### 1.5 Supported Voices

All current OpenAI TTS voices are included:
`alloy`, `ash`, `ballad`, `coral`, `echo`, `fable`, `nova`, `onyx`, `sage`, `shimmer`.

### 1.6 Model Selection

Users can choose between:
- **tts-1** — Lower latency, suitable for real-time use.
- **tts-1-hd** — Higher audio fidelity.

---

## 2. Architecture

```
Text-to-speech/
├── app.py                  # Flask backend (routes + OpenAI integration)
├── requirements.txt        # Python dependencies
├── .env.example            # Template for environment variables
├── agent.md                # This file — build process documentation
├── readme.md               # User-facing setup & usage guide
├── static/
│   └── style.css           # Stylesheet
└── templates/
    └── index.html          # Frontend (HTML + inline JS)
```

### Request Flow

```
Browser                    Flask (app.py)                 OpenAI API
  │                            │                              │
  │  POST /api/tts (JSON)      │                              │
  │ ────────────────────────►  │                              │
  │                            │  audio.speech.create(...)    │
  │                            │ ────────────────────────────►│
  │                            │                              │
  │                            │  ◄── streaming audio bytes   │
  │                            │ ◄────────────────────────────│
  │                            │                              │
  │  ◄── audio/mpeg or wav     │                              │
  │ ◄──────────────────────────│                              │
  │                            │                              │
  │  (JS creates Blob URL,     │                              │
  │   sets <audio> src,        │                              │
  │   enables download link)   │                              │
```

### Key Design Principles

1. **Zero disk I/O for audio** — everything stays in memory.
2. **Input validation** — voice, format, and model are validated server-side against allow-lists.
3. **Graceful error handling** — backend exceptions are caught and returned as JSON; the frontend displays them in a styled toast.
4. **No frontend build step** — open `index.html` and go.
5. **Secure API key management** — key is read from environment variables, never hard-coded.

---

## 3. Trade-offs & Future Improvements

| Area | Current | Potential Improvement |
|---|---|---|
| Auth | None (local use) | Add API-key-per-user or session auth for deployment |
| Rate limiting | None | Add Flask-Limiter for public deployments |
| Caching | None | Cache identical requests (text+voice+model hash) |
| Long text | Single API call | Chunk text into segments for inputs > 4096 chars |
| Streaming playback | Full download then play | Stream audio chunks to browser via `ReadableStream` |
