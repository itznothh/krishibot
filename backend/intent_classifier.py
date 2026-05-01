"""
KrishiBot - Intent Classifier
Separate module to avoid circular imports between app.py and whatsapp_handler.py
"""
import os
import json


INTENT_SYSTEM_PROMPT = """You are an intent classifier for KrishiBot, an AI farming assistant.

Given a farmer's message, classify it into EXACTLY ONE of these intents:
- "weather"      : asking about weather, rain, forecast, temperature, humidity
- "pest"         : asking about pests, insects, diseases, fungus, crop damage, treatment
- "crop"         : asking what crops to grow, crop recommendations, planting advice
- "fertilizer"   : asking about fertilizers, nutrients, NPK, manure, soil nutrition
- "general"      : everything else — soil testing, government schemes, market prices,
                   irrigation, farming tips, greetings, ambiguous or multi-topic questions

Rules:
- If the message is ambiguous (e.g., "soil test", "help", "what should I do?"), classify as "general"
- If the message mentions BOTH pests AND crops, classify as "pest"
- If the message mentions BOTH fertilizer AND crops, classify as "fertilizer"
- Never force a message into crop/pest/fertilizer just because a related word appears
- Respond ONLY with a JSON object like: {"intent": "weather", "confidence": "high"}
- confidence is "high" or "low"
"""


def classify_intent(message: str) -> str:
    """
    Use Groq/llama to classify the user's intent.
    Falls back to 'general' on any error so the bot never crashes.
    """
    try:
        from groq import Groq
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=60,
            temperature=0,
            messages=[
                {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
        )
        raw = resp.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)
        intent = data.get("intent", "general")
        if intent not in ("weather", "pest", "crop", "fertilizer", "general"):
            return "general"
        return intent
    except Exception as e:
        print(f"[intent_classifier] Error: {e} — falling back to 'general'")
        return "general"
