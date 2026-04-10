"""
KrishiBot - AI Knowledge Assistant Module
Uses Claude (Anthropic API) for general farming queries.
"""

import requests
import os

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

SYSTEM_PROMPT = """You are KrishiBot, a friendly and knowledgeable farming assistant for Indian farmers.
Your job is to help farmers with practical advice on:
- Crop cultivation, farming techniques
- Soil health and management
- Pest and disease identification
- Irrigation and water management
- Government schemes and subsidies for farmers
- Market prices and selling advice
- Organic and sustainable farming

Guidelines:
- Give SHORT, CLEAR, PRACTICAL answers (maximum 150 words)
- Use simple language that rural farmers can understand
- Use bullet points for steps or lists
- Include specific measurements and quantities when relevant
- Mention if they should consult a local agricultural officer for serious issues
- Be encouraging and supportive — farming is hard work!
- When relevant, mention free resources like Kisan Call Center (1800-180-1551)
- Focus on Indian farming context, crops, and conditions
- Don't give overly complex scientific explanations — keep it actionable
"""

QUICK_ANSWERS = {
    "hello": "Namaste! 🙏 I'm KrishiBot, your farming assistant. Ask me anything about crops, weather, pests, or fertilizers!",
    "hi": "Namaste! 🙏 I'm KrishiBot, your farming assistant. Ask me anything about crops, weather, pests, or fertilizers!",
    "help": (
        "I can help you with:\n"
        "🌦️ **Weather** — type 'weather' (share location)\n"
        "🌾 **Crops** — 'What to grow in kharif season?'\n"
        "🐛 **Pests** — 'My wheat has aphids'\n"
        "🧪 **Fertilizer** — 'Fertilizer for rice'\n"
        "💬 **Any farming question** — just ask!\n\n"
        "📞 Kisan Call Center: **1800-180-1551** (Free, 24x7)"
    ),
    "kisan call center": "📞 **Kisan Call Center: 1800-180-1551**\nFree helpline available 24x7 in 22 languages. Connect with agricultural experts for free advice!",
    "pm kisan": (
        "**PM-KISAN Scheme:**\n"
        "• ₹6,000/year to eligible farmers (3 installments of ₹2,000)\n"
        "• Register at: pmkisan.gov.in\n"
        "• Need: Aadhaar, Bank Account, Land Records\n"
        "• Check status: pmkisan.gov.in/Beneficiarystatus.aspx"
    ),
}


def get_ai_response(message: str, context: dict) -> str:
    """
    Get AI response for general farming questions.
    First checks quick answer database, then calls Claude API.
    """
    msg_lower = message.lower().strip()

    # Check quick answers
    for key, answer in QUICK_ANSWERS.items():
        if key in msg_lower:
            return answer

    # Call Claude API if key is available
    if ANTHROPIC_API_KEY:
        return _call_claude_api(message, context)
    else:
        return _fallback_response(message)


def _call_claude_api(message: str, context: dict) -> str:
    """Call Anthropic Claude API for farming assistance."""
    try:
        # Build conversation history from context
        messages = []

        # Add recent context if available
        if context.get("history"):
            for entry in context["history"][-4:]:  # Last 2 exchanges
                messages.append({"role": entry["role"], "content": entry["content"]})

        messages.append({"role": "user", "content": message})

        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-haiku-4-5-20251001",  # Fast and cost-effective
                "max_tokens": 400,
                "system": SYSTEM_PROMPT,
                "messages": messages
            },
            timeout=15
        )
        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"]

    except requests.exceptions.Timeout:
        return "⏳ The AI assistant is taking too long. Please try again in a moment."
    except requests.exceptions.ConnectionError:
        return _fallback_response(message)
    except Exception as e:
        return _fallback_response(message)


def _fallback_response(message: str) -> str:
    """
    Fallback responses when API is unavailable.
    Rule-based responses for very common questions.
    """
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
            "3. Ensure proper plant spacing for each crop\n"
            "4. Use drip/sprinkler irrigation (saves water, improves yield)\n"
            "5. Timely pest management — don't delay treatment\n"
            "6. Harvest at the right maturity stage\n\n"
            "📞 Call Kisan Helpline 1800-180-1551 for expert advice"
        )

    if any(w in msg_lower for w in ["irrigation", "water", "watering"]):
        return (
            "💧 **Irrigation Best Practices:**\n"
            "• Water in early morning or evening — reduces evaporation\n"
            "• Drip irrigation saves 40–50% water vs flood irrigation\n"
            "• Check soil moisture — don't overwater (causes root rot)\n"
            "• Critical irrigation stages vary by crop:\n"
            "  - Rice: Always flooded in early stages\n"
            "  - Wheat: CRI stage (21 days) + jointing + grain filling\n"
            "  - Cotton: At flowering and boll development"
        )

    if any(w in msg_lower for w in ["organic", "natural farming", "zero budget"]):
        return (
            "🌱 **Natural Farming Basics:**\n"
            "1. **Jeevamrit** — Cow dung + urine + jaggery + pulse flour + soil\n"
            "2. **Beejamrit** — Seed treatment with cow dung solution\n"
            "3. **Mulching** — Reduces weeds, retains moisture\n"
            "4. **Crop rotation** — Legumes fix nitrogen naturally\n"
            "5. **Composting** — Turn kitchen/crop waste into fertilizer\n\n"
            "📚 Learn Zero Budget Natural Farming: zbnf.in"
        )

    # Generic fallback
    return (
        "🌾 I received your question. For the best answer, please set your **ANTHROPIC_API_KEY** to enable the full AI assistant.\n\n"
        "In the meantime, you can ask me about:\n"
        "• **Weather** (share your location)\n"
        "• **Crop recommendations** (mention soil type + season)\n"
        "• **Pests** (describe symptoms)\n"
        "• **Fertilizers** (mention crop name)\n\n"
        "📞 **Kisan Call Center: 1800-180-1551** (Free, 24x7)"
    )
