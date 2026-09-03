"""
Text-to-Speech backend — dual-engine support.

Engines:
  1. OpenAI API  — cloud-based TTS via the openai package.
  2. Local Qwen3 — on-device voice cloning via the qwen-tts package
                   using the Qwen3-TTS-12Hz-0.6B-Base model.
"""

import io
import os
import tempfile

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_file
from openai import OpenAI

load_dotenv()

app = Flask(__name__)

# ---------------------------------------------------------------------------
# OpenAI configuration
# ---------------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY is not set. Add it to your .env file.")

client = OpenAI(api_key=OPENAI_API_KEY)

ALLOWED_VOICES = {"alloy", "ash", "ballad", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"}
ALLOWED_FORMATS = {"mp3", "wav"}
ALLOWED_MODELS = {"gpt-4o-mini-tts", "gpt-4o-tts"}

MIME_TYPES = {
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
}

# ---------------------------------------------------------------------------
# Local Qwen3-TTS model loading
# ---------------------------------------------------------------------------
# The model is loaded once at startup. If the required packages are missing or
# the model cannot be downloaded / loaded, a warning is printed and the local
# engine will be unavailable (the app continues to work with OpenAI only).
# ---------------------------------------------------------------------------
qwen3_model = None

try:
    import torch
    import soundfile as sf
    from qwen_tts import Qwen3TTSModel

    _device = "cuda:0" if torch.cuda.is_available() else "cpu"
    _dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32

    qwen3_model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
        device_map=_device,
        dtype=_dtype,
    )
    print(f"✓ Qwen3-TTS model loaded successfully on {_device}")

except Exception as exc:
    print(f"WARNING: Could not load Qwen3-TTS model: {exc}")
    print("  The 'Local Qwen3-TTS' engine will be unavailable.")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/tts", methods=["POST"])
def text_to_speech():
    """
    Unified TTS endpoint.

    Accepts multipart/form-data with the following fields:
      - engine:          "openai" (default) | "qwen3"
      - text:            The text to synthesise (required).
      - instructions:    Voice-style instructions (OpenAI) or reference-audio
                         transcript (Qwen3). Optional but recommended.
      - voice:           OpenAI voice name (ignored for Qwen3).
      - format:          "mp3" | "wav" (OpenAI only; Qwen3 always returns WAV).
      - model:           OpenAI model name (ignored for Qwen3).
      - reference_audio: Audio file for voice cloning (Qwen3 only).
    """

    # --- Read common form fields -------------------------------------------
    engine = (request.form.get("engine") or "openai").strip().lower()
    text = (request.form.get("text") or "").strip()
    instructions = (request.form.get("instructions") or "").strip()

    if not text:
        return jsonify({"error": "Text is required."}), 400

    # -----------------------------------------------------------------------
    # ENGINE: OpenAI API
    # -----------------------------------------------------------------------
    if engine == "openai":
        if not OPENAI_API_KEY:
            return jsonify({"error": "Server OPENAI_API_KEY is not configured."}), 500

        voice = (request.form.get("voice") or "alloy").lower()
        fmt = (request.form.get("format") or "mp3").lower()
        model = request.form.get("model") or "gpt-4o-mini-tts"

        if voice not in ALLOWED_VOICES:
            return jsonify({"error": f"Invalid voice. Choose from: {', '.join(sorted(ALLOWED_VOICES))}"}), 400
        if fmt not in ALLOWED_FORMATS:
            return jsonify({"error": f"Invalid format. Choose from: {', '.join(sorted(ALLOWED_FORMATS))}"}), 400
        if model not in ALLOWED_MODELS:
            return jsonify({"error": f"Invalid model. Choose from: {', '.join(sorted(ALLOWED_MODELS))}"}), 400

        try:
            api_params = {
                "model": model,
                "voice": voice,
                "input": text,
                "response_format": fmt,
            }

            if instructions:
                api_params["instructions"] = instructions

            response = client.audio.speech.create(**api_params)

            # Stream OpenAI response into an in-memory buffer
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

    # -----------------------------------------------------------------------
    # ENGINE: Local Qwen3-TTS (voice cloning)
    # -----------------------------------------------------------------------
    elif engine == "qwen3":
        if qwen3_model is None:
            return jsonify({
                "error": "The Qwen3-TTS model is not loaded. "
                         "Check the server logs for details."
            }), 503

        # The reference audio file is required for voice cloning
        ref_file = request.files.get("reference_audio")
        if ref_file is None or ref_file.filename == "":
            return jsonify({"error": "A reference audio file is required for voice cloning."}), 400

        tmp_path = None
        try:
            # Save the uploaded reference audio to a secure temp file
            suffix = os.path.splitext(ref_file.filename)[1] or ".wav"
            tmp_fd, tmp_path = tempfile.mkstemp(suffix=suffix)
            os.close(tmp_fd)  # close the file descriptor; we only need the path
            ref_file.save(tmp_path)

            # ----- Local model inference (voice cloning) -----
            wavs, sample_rate = qwen3_model.generate_voice_clone(
                text=text,
                language="English",
                ref_audio=tmp_path,
                ref_text=instructions if instructions else None,
            )

            # Write the generated waveform to an in-memory WAV buffer
            audio_buffer = io.BytesIO()
            sf.write(audio_buffer, wavs[0], sample_rate, format="WAV")
            audio_buffer.seek(0)

            return send_file(
                audio_buffer,
                mimetype="audio/wav",
                as_attachment=False,
                download_name="speech.wav",
            )

        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

        finally:
            # Always clean up the temporary reference audio file
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

    # -----------------------------------------------------------------------
    # Unknown engine
    # -----------------------------------------------------------------------
    else:
        return jsonify({"error": f"Unknown engine: '{engine}'. Use 'openai' or 'qwen3'."}), 400


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
