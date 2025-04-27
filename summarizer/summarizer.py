import os
import requests

class Summarizer:
    def __init__(self):
        self.summarizer_api_url = "https://api-inference.huggingface.co/models/Aadityaramrame/carecompanion-summarizer"
        self.translation_api_url = "https://carecompanion-summarizer.onrender.com/translate"  # your render endpoint
        self.api_token = os.getenv("API_KEY")
        if not self.api_token:
            raise ValueError("Hugging Face API Key not found in environment variables.")
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    def clean_text(self, text: str) -> str:
        return ' '.join(text.replace('\n', ' ').split())

    def format_summary(self, summary: str) -> str:
        summary = summary.strip()
        if summary and not summary[0].isupper():
            summary = summary[0].upper() + summary[1:]
        if "expected to recover within" in summary and not summary.endswith("days."):
            summary = summary.rstrip('. ')
            summary += " 7–10 days."
        if "antibiotic" in summary.lower() and "supportive" in summary.lower() and "treatment" not in summary.lower():
            summary += " Treatment includes antibiotics and supportive care."
        return summary

    def translate_text(self, text: str, target_lang: str) -> str:
        """Translate text using your deployed Render API."""
        try:
            payload = {"text": text, "target_lang": target_lang}
            response = requests.post(self.translation_api_url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("translated_text", text)
        except Exception as e:
            return f"Translation failed: {str(e)}"

    def summarize_text(self, text: str, target_lang: str = 'en') -> str:
        try:
            cleaned_text = self.clean_text(text)

            # Translate to English first if needed
            if target_lang != 'en':
                cleaned_text = self.translate_text(cleaned_text, "en")

            payload = {
                "inputs": f"summarize the clinical case with diagnosis, comorbidities, and treatment plan: {cleaned_text}"
            }
            response = requests.post(self.summarizer_api_url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            response_data = response.json()

            if isinstance(response_data, list) and "generated_text" in response_data[0]:
                summary = response_data[0]["generated_text"]
            else:
                return "Unexpected response format from Hugging Face API."

            formatted_summary = self.format_summary(summary)

            # Translate back to target language if needed
            if target_lang != 'en':
                formatted_summary = self.translate_text(formatted_summary, target_lang)

            return formatted_summary

        except requests.exceptions.Timeout:
            return "Summarization request timed out."
        except requests.exceptions.RequestException as e:
            return f"Summarization request failed: {str(e)}"
        except Exception as e:
            return f"An error occurred during summarization: {str(e)}"
