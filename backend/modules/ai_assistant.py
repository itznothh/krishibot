import os
import requests
from modules.conversation import normalize_history

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

SYSTEM_PROMPT = """You are KrishiBot, an expert farming assistant for Indian farmers.
Answer ANY farming related question clearly and practically.
Topics: crops, soil, pests, fertilizers, weather, government schemes, market prices, irrigation, organic farming, animal husbandry.
Rules:
- ALWAYS reply in the language specified by the user_language field in session info below. This overrides everything else.
- If user_language is "en" → reply in English only
- If user_language is "hi" → reply in Hindi only
- If user_language is "kn" → reply in Kannada only
- If user_language is not set, detect language from the farmer's message
- Keep answers practical and simple
- Use bullet points for steps
- Give specific quantities and measurements
- Be encouraging and supportive
- Never say you cannot answer a farming question
- For non-farming questions, politely redirect to farming topics
- Always read the conversation history carefully to understand what the farmer is referring to
- If the farmer says things like "did u got?", "did you get it?", "mila?", "got it?" — they are confirming or asking about the PREVIOUS conversation, respond based on that context
- NEVER ask the farmer to share location, city, district or state — the app handles location automatically via a button"""

# Keep answers useful without encouraging the model to invent farm-specific facts.
SYSTEM_PROMPT += """
- Start with the direct answer, then give a short practical next step.
- Tailor advice to details the farmer actually gave; if a missing detail changes the recommendation, ask one focused follow-up question.
- Never invent live weather, mandi prices, scheme deadlines, or local rules. Say when current/local verification is needed.
- For pesticide or fertilizer advice, distinguish general guidance from a confirmed diagnosis; do not recommend a banned/restricted product or invent a dose. Ask the farmer to follow the product label and local agricultural officer/KVK guidance.
- Use metric units and state the basis (per litre, acre, or hectare) for any quantity.
- Keep ordinary replies concise; use numbered steps only when there is an actual procedure.
"""

LANG_ENFORCEMENT = {
    "en": "FINAL INSTRUCTION: Your entire response MUST be in English only. Do not use Hindi or Kannada.",
    "hi": "अंतिम निर्देश: आपका पूरा उत्तर केवल हिंदी में होना चाहिए। एक भी अंग्रेजी या कन्नड़ शब्द का प्रयोग न करें।",
    "kn": "ಅಂತಿಮ ಸೂಚನೆ: ನಿಮ್ಮ ಸಂಪೂರ್ಣ ಉತ್ತರ ಕೇವಲ ಕನ್ನಡದಲ್ಲಿ ಇರಬೇಕು. ಇಂಗ್ಲಿಷ್ ಅಥವಾ ಹಿಂದಿ ಬಳಸಬೇಡಿ.",
}

class AIProviderError(Exception):
    """Raised when Groq cannot provide a valid assistant response."""


def get_ai_response(message: str, context: dict, language: str = None) -> str:
    if not GROQ_API_KEY:
        raise AIProviderError("AI service is not configured.")
    context = dict(context) if isinstance(context, dict) else {}
    if language:
        context = dict(context)
        context["language"] = language
    return _call_groq_api(message, context)


def translate_specialist_response(text: str, language: str) -> str:
    if language == "en":
        return text
    if language not in ("hi", "kn"):
        language = "en"
    if not GROQ_API_KEY:
        raise AIProviderError("AI service is not configured.")
    lang_name = "Hindi" if language == "hi" else "Kannada"
    return _call_groq_api(
        text,
        {"language": language, "translation_only": True, "language_name": lang_name},
    )


def answer_specialist_follow_up(message: str, context: dict, language: str, specialist: str) -> str:
    specialist_context = dict(context) if isinstance(context, dict) else {}
    specialist_context["specialist"] = specialist
    specialist_context["language"] = language
    return get_ai_response(message, specialist_context, language=language)

def _call_groq_api(message: str, context: dict) -> str:
    try:
        system = SYSTEM_PROMPT

        session_info = []
        if context.get("location_status"):
            session_info.append(f"location: {context['location_status']}")

        # Fix: read "language" key (set by app.py); fall back to "user_language" for legacy
        lang = context.get("language") or context.get("user_language") or "en"
        lang_map = {"en": "English", "hi": "Hindi", "kn": "Kannada"}
        lang_name = lang_map.get(lang, "English")
        session_info.append(
            f"user_language: {lang} — YOU MUST REPLY IN {lang_name.upper()} ONLY"
        )

        system += "\n\nCurrent session info:\n" + "\n".join(session_info)
        system += "\n\n" + LANG_ENFORCEMENT.get(lang, LANG_ENFORCEMENT["en"])
        specialist = context.get("specialist")
        if specialist:
            system += (
                f"\n\nYou are answering a follow-up as the KrishiBot {specialist} specialist. "
                "Use the bounded conversation history to resolve references and retain crop, soil, "
                "season, pest, symptom, and growth-stage details already provided. Do not ask the "
                "farmer to repeat known details. Ask one focused question only when a missing detail "
                "materially changes the guidance. Do not invent measurements or diagnoses."
            )
        if context.get("translation_only"):
            system = (
                f"Translate the user content faithfully into {context.get('language_name', 'English')}. "
                "Preserve all agricultural meaning, names, and quantities. Return only the translation.\n\n"
                + LANG_ENFORCEMENT.get(lang, LANG_ENFORCEMENT["en"])
            )

        messages = [{"role": "system", "content": system}]
        for entry in normalize_history(context.get("history"), current_message=message):
            messages.append({"role": entry["role"], "content": entry["content"]})
        messages.append({"role": "user", "content": message})

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-oss-120b",
                "messages": messages,
                "max_tokens": 900 if context.get("translation_only") else 500,
                "temperature": 0.35
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        if not isinstance(content, str) or not content.strip():
            raise AIProviderError("AI service returned an empty response.")
        return content.strip()
    except AIProviderError:
        raise
    except requests.exceptions.RequestException as error:
        raise AIProviderError("AI service is temporarily unavailable.") from error
    except (KeyError, IndexError, TypeError, ValueError) as error:
        raise AIProviderError("AI service returned an invalid response.") from error
