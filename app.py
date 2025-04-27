from flask import Flask, request, jsonify
from summarizer.summarizer import Summarizer
import os

app = Flask(__name__)
summarizer = Summarizer()

@app.route("/", methods=["GET"])
def home():
    return "CareCompanion Summarizer API is running."

@app.route("/summarize", methods=["POST"])
def summarize():
    try:
        data = request.get_json(force=True)  # force=True ensures it parses JSON even if content-type is off
    except Exception as e:
        return jsonify({"error": f"Invalid JSON: {str(e)}"}), 400

    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' field"}), 400

    text = data["text"]
    target_lang = data.get("target_lang", "en")

    try:
        summary = summarizer.summarize_text(text, target_lang)
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": f"Summarization failed: {str(e)}"}), 500

@app.route("/translate", methods=["POST"])
def translate():
    try:
        data = request.get_json(force=True)
    except Exception as e:
        return jsonify({"error": f"Invalid JSON: {str(e)}"}), 400

    if not data or "text" not in data or "target_lang" not in data:
        return jsonify({"error": "Missing 'text' or 'target_lang' field"}), 400

    text = data["text"]
    target_lang = data["target_lang"]

    try:
        translated_text = summarizer.translate_text(text, target_lang)
        return jsonify({"translated_text": translated_text})
    except Exception as e:
        return jsonify({"error": f"Translation failed: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
