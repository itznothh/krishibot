"""
KrishiBot - Smart Farming Assistant
Main Flask Application Entry Point
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

from modules.weather import get_weather_data, get_farming_weather_advice
from modules.crop_recommender import recommend_crops
from modules.pest_advisor import get_pest_advice
from modules.fertilizer import get_fertilizer_advice
from modules.ai_assistant import get_ai_response
from modules.language import translate_response, detect_language, SUPPORTED_LANGUAGES

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)  # Allow cross-origin requests for frontend

# ──────────────────────────────────────────────
# Serve Frontend
# ──────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory("../frontend", "index.html")


# ──────────────────────────────────────────────
# Main Chat Endpoint
# ──────────────────────────────────────────────
@app.route("/chat", methods=["POST"])
def chat():
    """
    Central chat endpoint. Routes messages to appropriate modules.

    Expected JSON body:
    {
        "message": "user query text",
        "language": "en" | "hi" | "kn",     (optional, default: "en")
        "lat": 12.9716,                       (optional)
        "lon": 77.5946,                       (optional)
        "context": {}                         (optional session context)
    }
    """
    try:
        data = request.get_json(force=True)
        user_message = data.get("message", "").strip()
        language = data.get("language", "en")
        lat = data.get("lat")
        lon = data.get("lon")
        context = data.get("context", {})

        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400

        # Detect intent and route to correct module
        response_data = route_message(user_message, language, lat, lon, context)

        # Translate response if language is not English
        if language != "en" and language in SUPPORTED_LANGUAGES:
            response_data["message"] = translate_response(
                response_data["message"], language
            )

        return jsonify(response_data)

    except Exception as e:
        return jsonify({
            "message": f"An error occurred: {str(e)}",
            "module": "error",
            "status": "error"
        }), 500


def route_message(message: str, language: str, lat, lon, context: dict) -> dict:
    """Detect intent from message and route to appropriate module."""
    msg_lower = message.lower()

    # ── Weather intent ──
    weather_keywords = ["weather", "rain", "temperature", "forecast", "humidity",
                        "मौसम", "बारिश", "ಹವಾಮಾನ", "ಮಳೆ"]
    if any(kw in msg_lower for kw in weather_keywords):
        if lat and lon:
            weather = get_weather_data(lat, lon)
            advice = get_farming_weather_advice(weather)
            return {
                "message": format_weather_response(weather, advice),
                "module": "weather",
                "data": weather,
                "status": "success"
            }
        else:
            return {
                "message": "Please share your location so I can fetch the current weather for your area. You can click the 📍 location button.",
                "module": "weather",
                "status": "needs_location"
            }

    # ── Crop Recommendation intent ──
    crop_keywords = ["crop", "grow", "plant", "sow", "seed", "which crop", "kharif",
                     "rabi", "फसल", "बुवाई", "ಬೆಳೆ", "ಬಿತ್ತನೆ"]
    if any(kw in msg_lower for kw in crop_keywords):
        recommendation = recommend_crops(message, context)
        return {
            "message": recommendation["message"],
            "module": "crop",
            "data": recommendation.get("crops", []),
            "status": "success"
        }

    # ── Pest & Disease intent ──
    pest_keywords = ["pest", "insect", "disease", "bug", "worm", "fungus", "blight",
                     "yellow leaves", "spots", "कीट", "रोग", "ಕೀಟ", "ರೋಗ"]
    if any(kw in msg_lower for kw in pest_keywords):
        advice = get_pest_advice(message)
        return {
            "message": advice["message"],
            "module": "pest",
            "data": advice.get("remedies", []),
            "status": "success"
        }

    # ── Fertilizer intent ──
    fertilizer_keywords = ["fertilizer", "manure", "npk", "urea", "nutrient",
                           "खाद", "उर्वरक", "ಗೊಬ್ಬರ", "ರಸಗೊಬ್ಬರ"]
    if any(kw in msg_lower for kw in fertilizer_keywords):
        advice = get_fertilizer_advice(message, context)
        return {
            "message": advice["message"],
            "module": "fertilizer",
            "data": advice.get("recommendations", []),
            "status": "success"
        }

    # ── Default: AI General Knowledge Assistant ──
    ai_response = get_ai_response(message, context)
    return {
        "message": ai_response,
        "module": "ai",
        "status": "success"
    }


def format_weather_response(weather: dict, advice: str) -> str:
    if "error" in weather:
        return f"Could not fetch weather: {weather['error']}"
    return (
        f"🌤️ **Weather Update**\n"
        f"📍 Location: {weather.get('location', 'Your area')}\n"
        f"🌡️ Temperature: {weather.get('temp', 'N/A')}°C\n"
        f"💧 Humidity: {weather.get('humidity', 'N/A')}%\n"
        f"🌬️ Condition: {weather.get('description', 'N/A').title()}\n"
        f"🌧️ Rain Chance: {weather.get('rain_chance', 'N/A')}%\n\n"
        f"🌾 **Farming Advice:**\n{advice}"
    )


# ──────────────────────────────────────────────
# Individual Module Endpoints (for direct use)
# ──────────────────────────────────────────────
@app.route("/weather", methods=["GET"])
def weather_endpoint():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    if not lat or not lon:
        return jsonify({"error": "lat and lon required"}), 400
    data = get_weather_data(lat, lon)
    advice = get_farming_weather_advice(data)
    return jsonify({"weather": data, "advice": advice})


@app.route("/crops", methods=["POST"])
def crops_endpoint():
    data = request.get_json(force=True)
    result = recommend_crops(data.get("message", ""), data.get("context", {}))
    return jsonify(result)


@app.route("/pest", methods=["POST"])
def pest_endpoint():
    data = request.get_json(force=True)
    result = get_pest_advice(data.get("message", ""))
    return jsonify(result)


@app.route("/fertilizer", methods=["POST"])
def fertilizer_endpoint():
    data = request.get_json(force=True)
    result = get_fertilizer_advice(data.get("message", ""), data.get("context", {}))
    return jsonify(result)


@app.route("/languages", methods=["GET"])
def languages_endpoint():
    return jsonify({"supported_languages": SUPPORTED_LANGUAGES})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "KrishiBot API", "version": "1.0.0"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "true").lower() == "true"
    print(f"🌾 KrishiBot starting on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
