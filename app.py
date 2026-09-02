"""
OpenAI Text-to-Speech Web Application
======================================
A lightweight Flask application that generates speech audio from text
using OpenAI's TTS API. Supports multiple voices, output formats,
and optional voice-instruction prompts.
"""

import io
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_file
from openai import OpenAI

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
load_dotenv()  # Load .env file if present

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print(
        "\n⚠️  WARNING: OPENAI_API_KEY is not set. "
        "Set it as an environment variable or add it to a .env file.\n"
    )

client = OpenAI(api_key=OPENAI_API_KEY)

# Allowed voices and formats (used for validation)
ALLOWED_VOICES = {"alloy", "ash", "ballad", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"}
ALLOWED_FORMATS = {"mp3", "wav"}
ALLOWED_MODELS = {"gpt-4o-mini-tts", "gpt-4o-tts"}

# MIME mapping for audio formats
MIME_TYPES = {
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Serve the main HTML page."""
    return render_template("index.html")


@app.route("/api/tts", methods=["POST"])
def text_to_speech():
    """
    Generate speech from text via the OpenAI TTS API.

    Expects JSON body:
        text            (str)  – The main text to be spoken.
        instructions    (str)  – Optional voice instructions / tone guidance.
        voice           (str)  – One of the allowed OpenAI TTS voices.
        format          (str)  – Output format: "mp3" or "wav".
        model           (str)  – TTS model: "tts-1" or "tts-1-hd".
    """
    if not OPENAI_API_KEY:
        return jsonify({"error": "Server OPENAI_API_KEY is not configured."}), 500

    data = request.get_json(silent=True) or {}

    # --- Validate inputs ---
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "Text is required."}), 400

    instructions = (data.get("instructions") or "").strip()
    voice = data.get("voice", "alloy").lower()
    fmt = data.get("format", "mp3").lower()
    model = data.get("model", "gpt-4o-mini-tts")

    if voice not in ALLOWED_VOICES:
        return jsonify({"error": f"Invalid voice. Choose from: {', '.join(sorted(ALLOWED_VOICES))}"}), 400
    if fmt not in ALLOWED_FORMATS:
        return jsonify({"error": f"Invalid format. Choose from: {', '.join(sorted(ALLOWED_FORMATS))}"}), 400
    if model not in ALLOWED_MODELS:
        return jsonify({"error": f"Invalid model. Choose from: {', '.join(sorted(ALLOWED_MODELS))}"}), 400

    # --- Call OpenAI TTS API ---
    try:
        api_params = {
            "model": model,
            "voice": voice,
            "input": text,
            "response_format": fmt,
        }

        # Pass voice instructions if provided
        if instructions:
            api_params["instructions"] = instructions

        response = client.audio.speech.create(**api_params)

        # Stream the response into an in-memory buffer (no temp files)
        audio_buffer = io.BytesIO()
        for chunk in response.iter_bytes(chunk_size=4096):
            audio_buffer.write(chunk)
        audio_buffer.seek(0)

        return send_file(
            audio_buffer,
            mimetype=MIME_TYPES[fmt],
            as_attachment=False,
            download_name=f"speech.{fmt}",
        )

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
