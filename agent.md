# Agent Build Process and Architecture

## Overview

This document explains the decisions made when building the Text-to-Speech web application and describes how the different parts of the app work together. The app supports two engines: **OpenAI API** (cloud) and **Local Qwen3-TTS** (on-device voice cloning).

---

## Design Decisions

### Backend Framework

Flask was chosen as the backend framework because it is lightweight and simple. The app only needs to handle one route that accepts text (and optionally a file) and returns audio, which is a good fit for Flask. It also has built-in support for sending binary file responses, which is what we need for returning audio data.

### Dual-Engine Architecture

The app supports two TTS engines selectable by the user:

- **OpenAI API** — Cloud-based TTS using OpenAI's `gpt-4o-mini-tts` or `gpt-4o-tts` models. Requires an API key. Supports multiple voices, formats (MP3/WAV), and natural-language style instructions.
- **Local Qwen3-TTS** — On-device voice cloning using the `Qwen3-TTS-12Hz-0.6B-Base` model via the `qwen-tts` package. Requires no API key but needs the model weights downloaded locally. The user uploads a reference audio clip, and the model generates speech in the cloned voice.

The local model is loaded once at application startup. If it fails to load (e.g. missing packages or insufficient hardware), a warning is printed and the app continues to function with the OpenAI engine only.

### Frontend

The frontend is a single HTML file with a small amount of JavaScript and a separate CSS file. No frontend frameworks like React or Vue were used, keeping the project easy to understand and run without any build tools.

The UI dynamically shows or hides engine-specific controls. When OpenAI is selected, the voice, format, and model dropdowns are visible. When Qwen3 is selected, the reference audio file upload appears and the voice instructions field is relabelled to "Reference audio transcript".

### Voice Instructions / Reference Transcript

For OpenAI, the instructions field controls the tone and style of the generated speech. For Qwen3, the same field is repurposed as the reference audio transcript — the text spoken in the uploaded audio clip. This dual-purpose design avoids cluttering the UI with extra fields.

### Audio Handling

- **OpenAI**: Audio is streamed from the API into memory and sent to the browser. No files are saved to disk.
- **Qwen3**: The uploaded reference audio is saved to a temporary file (via Python's `tempfile` module), used for inference, and immediately deleted in a `finally` block. The generated audio is also kept in memory.

### Model Choices

#### OpenAI
- `gpt-4o-mini-tts` is fast and handles voice instructions well. It is the default.
- `gpt-4o-tts` produces the highest quality audio and also supports voice instructions fully.

#### Local
- `Qwen3-TTS-12Hz-0.6B-Base` is a lightweight (0.6B parameter) TTS model that supports voice cloning from a short reference audio clip (~3+ seconds recommended). It requires approximately 4 GB of VRAM on GPU, or runs on CPU with higher latency.

---

## Architecture

```
Simple-text-to-speech/
    app.py              Flask backend — dual-engine TTS endpoint
    requirements.txt    Python packages needed
    .env.example        Template for environment variables
    agent.md            This file
    readme.md           User setup and usage guide
    static/
        style.css       Stylesheet
    templates/
        index.html      Frontend page (engine selector, forms, JS logic)
```

### How a Request Works

#### OpenAI Engine
1. The user selects the "OpenAI API" engine, fills in the form, and clicks Generate Speech.
2. The browser sends the form data as `multipart/form-data` to the `/api/tts` endpoint.
3. Flask reads `engine=openai` from the form, validates the inputs, and calls the OpenAI audio API.
4. OpenAI returns the audio bytes, which Flask streams into memory.
5. Flask sends the audio back to the browser.
6. The browser plays the audio and enables the download link.

#### Qwen3 Engine (Voice Cloning)
1. The user selects the "Local Qwen3-TTS" engine, uploads a reference audio clip, types the transcript of the reference audio, types the text to generate, and clicks Generate Speech.
2. The browser sends the form data (including the audio file) as `multipart/form-data` to `/api/tts`.
3. Flask reads `engine=qwen3`, saves the reference audio to a secure temp file, and calls `qwen3_model.generate_voice_clone()`.
4. The model generates a waveform that mimics the voice in the reference clip.
5. Flask writes the waveform to an in-memory WAV buffer and sends it to the browser.
6. The temp file is deleted in a `finally` block.
7. The browser plays the audio and enables the download link.

### Core Principles

- Audio output is never written to disk (only the reference audio is temporarily saved).
- Temporary files are always cleaned up immediately after inference.
- All inputs are validated on the server before processing.
- Errors from either engine are caught and shown to the user in a readable way.
- The OpenAI API key is read from environment variables and never stored in the code.
- The local model is loaded with graceful error handling so the app never crashes on startup.

---

## Possible Future Improvements

- Add rate limiting so the app cannot be abused if made public.
- Add caching so the same request does not call the API twice.
- Support longer texts by splitting them into chunks before sending to the API.
- Stream audio to the browser in real time instead of waiting for the full file.
- Add a language dropdown for the Qwen3 engine (currently defaults to English).
- Support `flash_attention_2` for reduced VRAM usage when the dependency is installed.
