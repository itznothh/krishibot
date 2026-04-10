import os
import requests

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

QUICK_ANSWERS = {
    "hello": "Namaste! 🙏 I'm KrishiBot, your farming assistant. Ask me anything about crops, weather, pests, or fertilizers!",
    "hi": "Namaste! 🙏 I'm KrishiBot, your farming assistant. Ask me anything about crops, weather, pests, or fertilizers!",
    "help": (
        "I can help you with:\n"
        "🌦️ **Weather** — type 'weather'\n"
        "🌾 **Crops** — 'What to grow in kharif season?'\n"
        "🐛 **Pests** — 'My wheat has aphids'\n"
        "🧪 **Fertilizer** — 'Fertilizer for rice'\n"
        "💬 **Any farming question** — just ask!\n\n"
        "📞 Kisan Call Center: **1800-180-1551** (Free, 24x7)"
    ),
}

SYSTEM_PROMPT = """You are KrishiBot, a friendly and knowledgeable farming assistant for Indian farmers.
Help farmers with practical advice on crops, soil, pests, irrigation, fertilizers, and government schemes.
Give SHORT, CLEAR, PRACTICAL answers (max 150 words). Use simple language.
Use bullet points for steps. Focus on Indian farming context."""

def get_ai_response(message: str, context: dict) -> str:
    msg_lower = message.lower().strip()

    for key, answer in QUICK_ANSWERS.items():
        if key in msg_lower:
            return answer

    if GROQ_API_KEY:
        return _call_groq_api(message)
    else:
        return _fallback_response(message)

def _call_groq_api(message: str) -> str:
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": message}
                ],
                "max_tokens": 400
            },
            timeout=15
        )
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return _fallback_response(message)

def _fallback_response(message: str) -> str:
    msg_lower = message.lower()

    if any(w in msg_lower for w in ["yellow", "yellowish", "pale"]):
        return (
            "🌿 **Yellow Leaves — Common Causes:**\n"
            "1. **Nitrogen deficiency** — Apply urea (1–2% spray)\n"
            "2. **Iron deficiency** — Spray ferrous sulfate 0.5%\n"
            "3. **Overwatering** — Reduce irrigation, improve drainage\n"
            "4. **Viral disease** — Remove infected plants, control insects\n\n"
            "💡 Do a soil test to confirm the exact cause."
        )

    if any(w in msg_lower for w in ["yield", "production", "increase"]):
        return (
            "🌾 **Tips to Increase Crop Yield:**\n"
            "1. Use certified, high-yielding variety seeds\n"
            "2. Test your soil and apply fertilizers as recommended\n"
            "3. Use drip/sprinkler irrigation\n"
            "4. Timely pest management\n\n"
            "📞 Call Kisan Helpline 1800-180-1551"
        )

    return (
        "🌾 Ask me about:\n"
        "• **Weather** (share your location)\n"
        "• **Crop recommendations** (mention soil type + season)\n"
        "• **Pests** (describe symptoms)\n"
        "• **Fertilizers** (mention crop name)\n\n"
        "📞 **Kisan Call Center: 1800-180-1551** (Free, 24x7)"
    )