from flask import Flask, request, jsonify
from summarizer.translator_module import TextTranslator
import os

app = Flask(__name__)
translator = TextTranslator()

@app.route("/", methods=["GET"])
def home():
    return "CareCompanion Translation API is running."

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
        translated_text = translator.translate_from_english(text, target_lang) if target_lang != 'en' else translator.translate_to_english(text)
        return jsonify({"translated_text": translated_text})
    except Exception as e:
        return jsonify({"error": f"Translation failed: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
