"""
KrishiBot - Main Flask Application
Uses AI-powered intent classification instead of brittle keyword matching.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json

from modules.weather import get_weather
from modules.crop_recommender import recommend_crops
from modules.pest_advisor import get_pest_advice
from modules.fertilizer import get_fertilizer_advice
from modules.ai_assistant import get_ai_response
from modules.language import detect_language, translate_response

app = Flask(__name__)
CORS(app)


# ---------------------------------------------------------------------------
# AI-powered intent classifier
# ---------------------------------------------------------------------------

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
            temperature=0,          # Deterministic for classification
            messages=[
                {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                {"role": "user",   "content": message},
            ],
        )
        raw = resp.choices[0].message.content.strip()
        # Strip markdown fences if present
        raw = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)
        intent = data.get("intent", "general")
        # Validate intent is one of the known values
        if intent not in ("weather", "pest", "crop", "fertilizer", "general"):
            return "general"
        return intent
    except Exception as e:
        print(f"[intent_classifier] Error: {e} — falling back to 'general'")
        return "general"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return jsonify({"message": "KrishiBot API is running!", "version": "3.0"})


@app.route('/health')
def health():
    return jsonify({"status": "ok"})


@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        message = data.get('message', '').strip()
        language = data.get('language', 'en')
        context = data.get('context', {})
        lat = data.get('lat')
        lon = data.get('lon')

        if not message:
            return jsonify({"error": "No message provided"}), 400

        # --- AI intent classification ---
        intent = classify_intent(message)

        # ---- Weather ----
        if intent == "weather":
            if lat and lon:
                weather_data = get_weather(float(lat), float(lon))
                if "error" in weather_data:
                    return jsonify({"status": "error", "message": weather_data["error"]})

                # Enrich rain-specific questions with AI commentary
                msg_lower = message.lower()
                if any(w in msg_lower for w in ['rain', 'barish', 'rainfall', 'chances', 'will it rain']):
                    ai_msg = get_ai_response(
                        f"Based on this weather data: {weather_data}, what are the rain chances? "
                        "Give a short 2-3 line farmer-friendly answer.",
                        context
                    )
                    weather_data["farming_advice"] = ai_msg

                return jsonify({"status": "weather", "data": weather_data})
            else:
                return jsonify({
                    "status": "needs_location",
                    "message": "📍 Please share your location to get weather information."
                })

        # ---- Pest / Disease ----
        elif intent == "pest":
            response = get_pest_advice(message)
            return jsonify({"status": "pest_advice", "message": response})

        # ---- Crop Recommendation ----
        elif intent == "crop":
            response = recommend_crops(message, context)
            return jsonify({"status": "crop_advice", "message": response})

        # ---- Fertilizer ----
        elif intent == "fertilizer":
            response = get_fertilizer_advice(message)
            return jsonify({"status": "fertilizer", "message": response})

        # ---- General / Ambiguous — full AI assistant ----
        else:
            response = get_ai_response(message, context)
            return jsonify({"status": "ai_response", "message": response})

    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)