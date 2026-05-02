import os
import requests

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

def get_ai_response(message: str, context: dict) -> str:
    if not GROQ_API_KEY:
        return "AI assistant not configured. Please set GROQ_API_KEY."
    return _call_groq_api(message, context)

def _call_groq_api(message: str, context: dict) -> str:
    try:
        # Build system prompt with location + language context
        system = SYSTEM_PROMPT
        session_info = []
        if context.get("location_status"):
            session_info.append(f"location: {context['location_status']}")
        if context.get("user_language"):
            lang_map = {"en": "English", "hi": "Hindi", "kn": "Kannada"}
            lang_name = lang_map.get(context["user_language"], "English")
            session_info.append(f"user_language: {context['user_language']} — YOU MUST REPLY IN {lang_name.upper()} ONLY")
        if session_info:
            system += f"\n\nCurrent session info:\n" + "\n".join(session_info)

        messages = [{"role": "system", "content": system}]
        if context.get("history"):
            for entry in context["history"][-6:]:
                messages.append({"role": entry["role"], "content": entry["content"]})
        messages.append({"role": "user", "content": message})

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7
            },
            timeout=30
        )
        data = response.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            error_msg = data.get("error", {}).get("message", str(data))
            return f"AI Error: {error_msg}"
    except Exception as e:
        return f"Sorry, could not process your question. Please try again. Error: {str(e)}"