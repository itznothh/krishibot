"""
KrishiBot - Multi-Language Support Module
Supports English, Hindi, and Kannada.
Designed for easy extension to more languages.
"""

import requests
import os

# Supported languages registry
SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "native": "English", "flag": "🇬🇧"},
    "hi": {"name": "Hindi", "native": "हिंदी", "flag": "🇮🇳"},
    "kn": {"name": "Kannada", "native": "ಕನ್ನಡ", "flag": "🏳️"},
}

# LibreTranslate or MyMemory API for translation
# Using MyMemory (free, no key required for basic use)
TRANSLATION_API = "https://api.mymemory.translated.net/get"

# Static phrase translations (fast, no API needed)
STATIC_TRANSLATIONS = {
    "hi": {
        "Namaste": "नमस्ते",
        "Weather Update": "मौसम अपडेट",
        "Farming Advice": "खेती सलाह",
        "Recommended Crops": "सुझाई गई फसलें",
        "Fertilizer Guide": "उर्वरक मार्गदर्शिका",
        "Organic Remedies": "जैविक उपचार",
        "Chemical Remedies": "रासायनिक उपचार",
        "Prevention": "रोकथाम",
        "Temperature": "तापमान",
        "Humidity": "नमी",
        "Rain Chance": "बारिश की संभावना",
        "Pro Tip": "विशेषज्ञ सुझाव",
    },
    "kn": {
        "Namaste": "ನಮಸ್ಕಾರ",
        "Weather Update": "ಹವಾಮಾನ ಅಪ್ಡೇಟ್",
        "Farming Advice": "ಕೃಷಿ ಸಲಹೆ",
        "Recommended Crops": "ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳೆಗಳು",
        "Fertilizer Guide": "ಗೊಬ್ಬರ ಮಾರ್ಗದರ್ಶಿ",
        "Organic Remedies": "ಸಾವಯವ ಪರಿಹಾರಗಳು",
        "Chemical Remedies": "ರಾಸಾಯನಿಕ ಪರಿಹಾರಗಳು",
        "Prevention": "ತಡೆಗಟ್ಟುವಿಕೆ",
        "Temperature": "ತಾಪಮಾನ",
        "Humidity": "ತೇವಾಂಶ",
        "Rain Chance": "ಮಳೆ ಸಂಭಾವ್ಯತೆ",
        "Pro Tip": "ತಜ್ಞ ಸಲಹೆ",
    }
}

# Language target codes for MyMemory API
LANG_CODES = {
    "hi": "hi",
    "kn": "kn",
    "en": "en",
}


def translate_response(text: str, target_lang: str) -> str:
    """
    Translate response text to target language.
    Tries static lookup first, then falls back to API.
    """
    if target_lang == "en" or target_lang not in SUPPORTED_LANGUAGES:
        return text  # No translation needed

    # For short responses, use API
    try:
        translated = _translate_via_api(text, target_lang)
        if translated:
            return translated
    except Exception:
        pass

    # Fallback: return original with language note
    lang_name = SUPPORTED_LANGUAGES[target_lang]["native"]
    return f"{text}\n\n_[Translation to {lang_name} unavailable offline]_"


def _translate_via_api(text: str, target_lang: str) -> str | None:
    """Call MyMemory translation API (free tier)."""
    if len(text) > 500:
        # Split long text and translate in parts
        parts = _split_text(text, 500)
        translated_parts = []
        for part in parts:
            t = _call_mymemory(part, target_lang)
            translated_parts.append(t if t else part)
        return "\n".join(translated_parts)
    return _call_mymemory(text, target_lang)


def _call_mymemory(text: str, target_lang: str) -> str | None:
    """Make actual API call to MyMemory."""
    try:
        params = {
            "q": text,
            "langpair": f"en|{LANG_CODES[target_lang]}",
            "de": "krishibot@farming.ai"  # Required for free tier
        }
        resp = requests.get(TRANSLATION_API, params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json()

        if data.get("responseStatus") == 200:
            translated = data["responseData"]["translatedText"]
            # MyMemory sometimes returns "PLEASE SELECT TWO DISTINCT LANGUAGES"
            if "PLEASE SELECT" not in translated and len(translated) > 0:
                return translated
    except Exception:
        pass
    return None


def detect_language(text: str) -> str:
    """
    Simple language detection based on character ranges.
    Devanagari (Hindi): U+0900–U+097F
    Kannada: U+0C80–U+0CFF
    """
    for char in text:
        code = ord(char)
        if 0x0900 <= code <= 0x097F:
            return "hi"
        if 0x0C80 <= code <= 0x0CFF:
            return "kn"
    return "en"


def _split_text(text: str, max_len: int) -> list:
    """Split text into chunks at sentence boundaries."""
    parts = []
    current = ""
    for line in text.split("\n"):
        if len(current) + len(line) < max_len:
            current += line + "\n"
        else:
            if current:
                parts.append(current.strip())
            current = line + "\n"
    if current:
        parts.append(current.strip())
    return parts


# ──────────────────────────────────────────────
# Future: Add More Languages
# ──────────────────────────────────────────────
# To add a new language:
# 1. Add entry to SUPPORTED_LANGUAGES dict
# 2. Add key phrases to STATIC_TRANSLATIONS
# 3. Add language code to LANG_CODES
# That's it! MyMemory API handles the rest.
#
# Upcoming: Tamil (ta), Telugu (te), Marathi (mr), Punjabi (pa)
