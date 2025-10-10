from flask import Flask, request, jsonify, send_file

import zipfile
from wrapper.model import XTTSWrapper
from wrapper.helper import paragraph_to_audio
from wrapper.constants import DEFAULT_SAMPLE_RATE, DEFAULT_OUTPUT_FILE_LENGTH

from io import BytesIO


app = Flask(__name__)

# Init the TTS model
wrapper = XTTSWrapper(
    model_dir="models/viXTTS",
    audio_path="models/viXTTS/vi_sample.wav"
)


@app.route("/paragraph_to_sentence_audios", methods=["POST"])
def paragraph_to_sentence_audios():
    # Accept JSON; fall back to form or query string gracefully
    data = request.get_json(silent=True) or {}
    if not data and request.form:
        data = request.form.to_dict()
    if not data and request.args:
        data = request.args.to_dict()

    text = (data.get("text") or "").strip()
    language = (data.get("language") or "vi").strip()

    print(f"Processing text: [{text}] with language: [{language}]")

    if not text:
        return jsonify({
            "error": "No text provided. Send JSON with {'text': '...'}",
            "hint": "Use header 'Content-Type: application/json'."
        }), 400

    # Generate audios
    try:
        audio_map = paragraph_to_audio(
            wrapper, text, language)  # {name: np.ndarray[int16]}
    except Exception as e:
        return jsonify({"error": "Failed to synthesize audio", "detail": str(e)}), 500

    if not audio_map:
        return jsonify({"error": "No audio generated"}), 500

    # Build a ZIP in memory (no disk writes)
    zip_buf = BytesIO()
    with zipfile.ZipFile(zip_buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for audio_name, audio in audio_map.items():
            # sanitize & truncate file name
            safe_name = "".join(
                c for c in audio_name if c.isalnum() or c in ("-", "_", " ")).strip()
            safe_name = (safe_name or "audio")[
                :DEFAULT_OUTPUT_FILE_LENGTH] + ".wav"

            # write a wav into a memory buffer
            wav_buf = BytesIO()
            # scipy.io.wavfile.write supports file-like objects
            from scipy.io import wavfile
            wavfile.write(wav_buf, DEFAULT_SAMPLE_RATE, audio)
            zf.writestr(safe_name, wav_buf.getvalue())

    zip_buf.seek(0)
    return send_file(
        zip_buf,
        mimetype="application/zip",
        as_attachment=True,
        download_name="audio_files.zip",
        max_age=0
    )


@app.route("/health", methods=["GET"])
def health():
    return "200"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
