import io
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_file
from openai import OpenAI

load_dotenv()

app = Flask(__name__)

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


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/tts", methods=["POST"])
def text_to_speech():
    if not OPENAI_API_KEY:
        return jsonify({"error": "Server OPENAI_API_KEY is not configured."}), 500

    data = request.get_json(silent=True) or {}

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


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
