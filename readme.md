# OpenAI Text-to-Speech Web App

A lightweight web application that converts text to natural-sounding speech using the [OpenAI TTS API](https://platform.openai.com/docs/guides/text-to-speech). Built with **Flask** (Python) and plain **HTML/CSS/JS** — no heavy frontend frameworks.

---

## ✨ Features

- **10 voices** — Alloy, Ash, Ballad, Coral, Echo, Fable, Nova, Onyx, Sage, Shimmer
- **Voice instructions** — guide tone, accent, pacing, and emotion
- **Two quality tiers** — `tts-1` (fast) and `tts-1-hd` (high fidelity)
- **MP3 & WAV** output formats
- **In-browser playback** with one-click download
- **No temp files** — audio is streamed in-memory
- **Dark-themed UI** with glassmorphism and micro-animations

---

## 📋 Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.9 or newer |
| pip | Latest recommended |
| OpenAI API key | [Get one here](https://platform.openai.com/api-keys) |

---

## 🚀 Setup & Installation

### 1. Clone or download this project

```bash
cd Text-to-speech
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your OpenAI API key

Copy the example file and fill in your key:

```bash
copy .env.example .env        # Windows
# cp .env.example .env        # macOS / Linux
```

Then edit `.env`:

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> **⚠️ Never commit your `.env` file to version control.** The key should remain private.

Alternatively, export the variable directly:

```bash
# PowerShell
$env:OPENAI_API_KEY = "sk-..."

# Bash
export OPENAI_API_KEY="sk-..."
```

### 5. Run the application

```bash
python app.py
```

The server starts at **http://127.0.0.1:5000**. Open that URL in your browser.

---

## 🎯 Usage

1. **Enter text** in the main text area.
2. *(Optional)* Add **voice instructions** to control tone, accent, or emotion.
3. Pick a **voice** from the dropdown.
4. Choose **MP3** or **WAV** format.
5. Select the **model** (`tts-1` for speed, `tts-1-hd` for quality).
6. Click **Generate Speech**.
7. Listen in-browser or click **⬇ Download**.

---

## 📁 Project Structure

```
Text-to-speech/
├── app.py                  # Flask backend & API endpoint
├── requirements.txt        # Python dependencies
├── .env.example            # Template for your API key
├── agent.md                # Agent build process & architecture
├── readme.md               # This file
├── static/
│   └── style.css           # Stylesheet (dark theme)
└── templates/
    └── index.html          # Frontend UI
```

---

## 🔧 API Endpoint

### `POST /api/tts`

**Request body** (JSON):

```json
{
  "text": "Hello, world!",
  "instructions": "Speak warmly and slowly.",
  "voice": "nova",
  "format": "mp3",
  "model": "tts-1"
}
```

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `text` | string | ✅ | — | Text to convert to speech |
| `instructions` | string | ❌ | `""` | Tone / style guidance |
| `voice` | string | ❌ | `alloy` | TTS voice name |
| `format` | string | ❌ | `mp3` | `mp3` or `wav` |
| `model` | string | ❌ | `tts-1` | `tts-1` or `tts-1-hd` |

**Response:** Binary audio stream (`audio/mpeg` or `audio/wav`).

---

## ⚠️ Troubleshooting

| Issue | Solution |
|---|---|
| `OPENAI_API_KEY is not set` warning | Set the key in `.env` or as an environment variable |
| `401 Unauthorized` from OpenAI | Check that your API key is valid and has TTS access |
| No audio plays | Check browser console for errors; ensure the key is funded |
| Port 5000 in use | Run with `python app.py` after changing the port in `app.py` |

---

## 📄 License

This project is provided as-is for educational and personal use. The OpenAI API is subject to [OpenAI's usage policies](https://openai.com/policies/usage-policies).
