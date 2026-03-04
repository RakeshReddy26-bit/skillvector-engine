from dotenv import load_dotenv
load_dotenv()
import os
import logging
from anthropic import Anthropic

logger = logging.getLogger(__name__)
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SUPPORTED_LANGUAGES = {
    "de": "German",
    "fr": "French", 
    "es": "Spanish",
    "it": "Italian",
    "pt": "Portuguese",
    "nl": "Dutch",
    "pl": "Polish",
    "en": "English"
}

def detect_language(text: str) -> str:
    """Detect language of text. Returns language code like 'de', 'en', 'fr'"""
    try:
        sample = text[:500]
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=10,
            messages=[{
                "role": "user",
                "content": f"Detect the language of this text. Reply with ONLY the 2-letter ISO code (en, de, fr, es, it, pt, nl, pl). Text: {sample}"
            }]
        )
        lang = response.content[0].text.strip().lower()[:2]
        return lang if lang in SUPPORTED_LANGUAGES else "en"
    except Exception as e:
        logger.error(f"Language detection failed: {e}")
        return "en"


def translate_to_english(text: str, source_lang: str) -> str:
    """Translate text to English using Claude Haiku (fast + cheap)"""
    if source_lang == "en":
        return text
    
    lang_name = SUPPORTED_LANGUAGES.get(source_lang, "Unknown")
    
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": f"""Translate this {lang_name} resume to English.
Keep all technical terms, job titles, company names, and skills exactly as they are.
Only translate the descriptive text.
Output ONLY the translated text, nothing else.

Resume:
{text}"""
            }]
        )
        translated = response.content[0].text.strip()
        logger.info(f"Translated resume from {lang_name} to English ({len(text)} -> {len(translated)} chars)")
        return translated
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        return text


def process_resume_language(resume_text: str) -> dict:
    """
    Detect language and translate if needed.
    Returns dict with translated text and metadata.
    """
    lang = detect_language(resume_text)
    
    if lang == "en":
        return {
            "text": resume_text,
            "original_language": "en",
            "translated": False,
            "language_name": "English"
        }
    
    translated = translate_to_english(resume_text, lang)
    return {
        "text": translated,
        "original_language": lang,
        "translated": True,
        "language_name": SUPPORTED_LANGUAGES.get(lang, "Unknown")
    }
