"""
KrishiBot - Main Flask Application
Uses AI-powered intent classification instead of brittle keyword matching.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import base64

from modules.weather import get_weather
from modules.crop_recommender import recommend_crops
from modules.pest_advisor import get_pest_advice
from modules.fertilizer import get_fertilizer_advice
from modules.ai_assistant import get_ai_response
from modules.language import detect_language, translate_response
from modules.image_analyzer import analyze_crop_image

app = Flask(__name__)
CORS(app)


# ---------------------------------------------------------------------------
# Intent classifier — imported from intent_classifier.py to avoid circular imports
# ---------------------------------------------------------------------------

from intent_classifier import classify_intent


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

        if lat and lon:
            context['location_status'] = f"User's GPS location is available (lat={lat}, lon={lon}). Location was successfully shared via the app."
        else:
            context['location_status'] = "User has not shared GPS location yet. They can click the 📍 button to share it."

        intent = classify_intent(message)

        if intent == "weather":
            if lat and lon:
                weather_data = get_weather(float(lat), float(lon))
                if "error" in weather_data:
                    return jsonify({"status": "error", "message": weather_data["error"]})

                msg_lower = message.lower()
                if any(w in msg_lower for w in ['rain', 'barish', 'rainfall', 'chances', 'will it rain']):
                    prompt = (
                        f"Based on this weather data: {weather_data}, what are the rain chances? "
                        "Give a short 2-3 line farmer-friendly answer."
                    )
                else:
                    prompt = (
                        f"Based on this weather data: {weather_data}, give a short 2-3 line "
                        "farmer-friendly tip on how this weather affects farming today "
                        "(e.g. irrigation, spraying, harvesting advice)."
                    )
                weather_data["farming_advice"] = get_ai_response(prompt, context)
                return jsonify({"status": "weather", "data": weather_data})
            else:
                return jsonify({
                    "status": "needs_location",
                    "message": "📍 Please share your location to get weather information."
                })

        elif intent == "pest":
            response = get_pest_advice(message)
            return jsonify({"status": "pest_advice", "message": response})

        elif intent == "crop":
            response = recommend_crops(message, context)
            return jsonify({"status": "crop_advice", "message": response})

        elif intent == "fertilizer":
            response = get_fertilizer_advice(message)
            return jsonify({"status": "fertilizer", "message": response})

        else:
            response = get_ai_response(message, context)
            return jsonify({"status": "ai_response", "message": response})

    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500


# ---------------------------------------------------------------------------
# NEW: Image Analysis Route (Gemini Vision) — added without changing above
# ---------------------------------------------------------------------------

@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        image_base64 = data.get('image')
        mime_type = data.get('mime_type', 'image/jpeg')

        if not image_base64:
            return jsonify({"error": "No image provided"}), 400

        result = analyze_crop_image(image_base64, mime_type)
        return jsonify({"status": "image_analysis", "message": result})

    except Exception as e:
        return jsonify({"status": "error", "message": f"Image analysis error: {str(e)}"}), 500




# ---------------------------------------------------------------------------
# WhatsApp Webhook Routes — added below, nothing above changed
# ---------------------------------------------------------------------------

from whatsapp_handler import process_whatsapp_message, send_whatsapp_message

WHATSAPP_VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN", "krishibot_secret_123")


@app.route('/webhook', methods=['GET'])
def whatsapp_verify():
    """Meta calls this to verify your webhook."""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if mode == 'subscribe' and token == WHATSAPP_VERIFY_TOKEN:
        print("[WhatsApp] Webhook verified!")
        return challenge, 200
    return "Forbidden", 403


@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    """Receives incoming WhatsApp messages from Meta."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "no data"}), 200

        entry = data.get("entry", [])
        if not entry:
            return jsonify({"status": "no entry"}), 200

        changes = entry[0].get("changes", [])
        if not changes:
            return jsonify({"status": "no changes"}), 200

        value = changes[0].get("value", {})
        messages = value.get("messages", [])
        if not messages:
            return jsonify({"status": "ok"}), 200

        message_obj = messages[0]
        phone = message_obj.get("from", "")
        if not phone:
            return jsonify({"status": "no phone"}), 200

        print(f"[WhatsApp] Message from {phone}")
        reply = process_whatsapp_message(phone, message_obj)
        send_whatsapp_message(phone, reply)
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print(f"[WhatsApp] Webhook error: {str(e)}")
        return jsonify({"status": "error"}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
