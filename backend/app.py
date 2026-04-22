"""
KrishiBot - Main Flask Application
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from modules.weather import get_weather
from modules.crop_recommender import recommend_crops
from modules.pest_advisor import get_pest_advice
from modules.fertilizer import get_fertilizer_advice
from modules.ai_assistant import get_ai_response
from modules.language import detect_language, translate_response

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return jsonify({"message": "KrishiBot API is running!", "version": "2.0"})

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

        msg_lower = message.lower()

        # Weather intent
        if any(w in msg_lower for w in ['weather', 'rain', 'temperature', 'humidity', 'forecast', 'mausam', 'barish', 'havamaan']):
            if lat and lon:
                weather_data = get_weather(float(lat), float(lon))
                if "error" in weather_data:
                    return jsonify({"status": "error", "message": weather_data["error"]})
                # If asking specifically about rain, add AI interpretation
                if any(w in msg_lower for w in ['rain', 'barish', 'rainfall', 'chances', 'will it rain']):
                    ai_msg = get_ai_response(
                        f"Based on this weather data: {weather_data}, what are the rain chances? Give a short 2-3 line farmer-friendly answer.",
                        context
                    )
                    weather_data["farming_advice"] = ai_msg
                return jsonify({"status": "weather", "data": weather_data})
            else:
                return jsonify({"status": "needs_location", "message": "📍 Please share your location to get weather information."})

        # Pest intent — check BEFORE crop
        elif any(w in msg_lower for w in ['pest', 'insect', 'bug', 'disease', 'fungus', 'aphid', 'worm', 'keeda', 'rog', 'bimari', 'neem', 'caterpillar', 'blight', 'rust', 'mildew', 'thrips', 'whitefly']):
            response = get_pest_advice(message)
            return jsonify({"status": "pest_advice", "message": response})

        # Crop recommendation intent
        elif any(w in msg_lower for w in ['crop', 'grow', 'plant', 'seed', 'kharif', 'rabi', 'zaid', 'fasal', 'ugao', 'soil', 'loamy', 'sandy', 'black soil', 'clay']):
            response = recommend_crops(message, context)
            return jsonify({"status": "crop_advice", "message": response})

        # Fertilizer intent
        elif any(w in msg_lower for w in ['fertilizer', 'fertiliser', 'npk', 'urea', 'dap', 'manure', 'khad', 'nitrogen', 'phosphorus', 'potassium', 'organic']):
            response = get_fertilizer_advice(message)
            return jsonify({"status": "fertilizer", "message": response})

        # AI assistant for everything else
        else:
            response = get_ai_response(message, context)
            return jsonify({"status": "ai_response", "message": response})

    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)