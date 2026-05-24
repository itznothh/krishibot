"""
KrishiBot - Main Flask Application
Uses AI-powered intent classification instead of brittle keyword matching.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import base64
import requests as req

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
# WhatsApp Session Storage (persistent location memory)
# ---------------------------------------------------------------------------

SESSIONS_FILE = '/tmp/wa_sessions.json'

def load_sessions():
    try:
        with open(SESSIONS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_sessions(sessions):
    try:
        with open(SESSIONS_FILE, 'w') as f:
            json.dump(sessions, f)
    except Exception as e:
        print(f"[session] Save error: {e}")

def get_user_location(sender):
    sessions = load_sessions()
    user = sessions.get(sender, {})
    lat = user.get('lat')
    lon = user.get('lon')
    return lat, lon

def set_user_location(sender, lat, lon):
    sessions = load_sessions()
    if sender not in sessions:
        sessions[sender] = {}
    sessions[sender]['lat'] = lat
    sessions[sender]['lon'] = lon
    save_sessions(sessions)
    print(f"[session] Saved location for {sender}: {lat}, {lon}")


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
            temperature=0,
            messages=[
                {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                {"role": "user",   "content": message},
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

        # ── Language instruction injected into every AI call ───────────────
        lang_instruction = {
            'hi': 'IMPORTANT: You must reply entirely in Hindi (Devanagari script). Do not use English except for technical crop/chemical names.',
            'kn': 'IMPORTANT: You must reply entirely in Kannada script. Do not use English except for technical crop/chemical names.',
            'en': 'Reply in clear simple English suitable for a farmer.',
        }
        context['language'] = language
        context['language_instruction'] = lang_instruction.get(language, lang_instruction['en'])

        intent = classify_intent(message)

        if intent == "weather":
            if lat and lon:
                weather_data = get_weather(float(lat), float(lon))
                if "error" in weather_data:
                    return jsonify({"status": "error", "message": weather_data["error"]})

                msg_lower = message.lower()
                if any(w in msg_lower for w in ['rain', 'barish', 'rainfall', 'chances', 'will it rain']):
                    prompt = (
                        f"{context['language_instruction']}\n"
                        f"Based on this weather data: {weather_data}, what are the rain chances? "
                        "Give a short 2-3 line farmer-friendly answer."
                    )
                else:
                    prompt = (
                        f"{context['language_instruction']}\n"
                        f"Based on this weather data: {weather_data}, give a short 2-3 line "
                        "farmer-friendly tip on how this weather affects farming today "
                        "(e.g. irrigation, spraying, harvesting advice)."
                    )
                weather_data["farming_advice"] = get_ai_response(prompt, context)
                return jsonify({"status": "weather", "data": weather_data})
            else:
                no_loc_msg = {
                    'hi': '📍 कृपया मौसम की जानकारी के लिए अपना स्थान साझा करें।',
                    'kn': '📍 ಹವಾಮಾನ ಮಾಹಿತಿಗಾಗಿ ದಯವಿಟ್ಟು ನಿಮ್ಮ ಸ್ಥಳವನ್ನು ಹಂಚಿಕೊಳ್ಳಿ.',
                    'en': '📍 Please share your location to get weather information.',
                }
                return jsonify({
                    "status": "needs_location",
                    "message": no_loc_msg.get(language, no_loc_msg['en'])
                })

        elif intent == "pest":
            response = get_pest_advice(message, language=language)
            return jsonify({"status": "pest_advice", "message": response})

        elif intent == "crop":
            response = recommend_crops(message, context, language=language)
            return jsonify({"status": "crop_advice", "message": response})

        elif intent == "fertilizer":
            response = get_fertilizer_advice(message, language=language)
            return jsonify({"status": "fertilizer", "message": response})

        else:
            response = get_ai_response(message, context)
            return jsonify({"status": "ai_response", "message": response})

    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500


# ---------------------------------------------------------------------------
# Image Analysis Route (Gemini Vision)
# ---------------------------------------------------------------------------

@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    try:
        # Accept both FormData (from web app) and JSON (legacy)
        if request.content_type and 'multipart/form-data' in request.content_type:
            image_file = request.files.get('image')
            language   = request.form.get('language', 'en')
            if not image_file:
                return jsonify({"error": "No image file provided"}), 400
            image_bytes  = image_file.read()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            mime_type    = image_file.content_type or 'image/jpeg'
        else:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            image_base64 = data.get('image')
            mime_type    = data.get('mime_type', 'image/jpeg')
            language     = data.get('language', 'en')
            if not image_base64:
                return jsonify({"error": "No image provided"}), 400

        lang_instruction = {
            'hi': 'IMPORTANT: Reply entirely in Hindi (Devanagari script).',
            'kn': 'IMPORTANT: Reply entirely in Kannada script.',
            'en': '',
        }.get(language, '')

        result = analyze_crop_image(image_base64, mime_type)
        return jsonify({"status": "image_analysis", "message": result})

    except Exception as e:
        return jsonify({"status": "error", "message": f"Image analysis error: {str(e)}"}), 500


# ---------------------------------------------------------------------------
# WhatsApp Webhook (Twilio)
# ---------------------------------------------------------------------------

@app.route('/whatsapp', methods=['POST'])
def whatsapp():
    try:
        from twilio.twiml.messaging_response import MessagingResponse
        import requests as req

        incoming_msg = request.form.get('Body', '').strip()
        sender = request.form.get('From', '')
        num_media = int(request.form.get('NumMedia', 0))
        latitude = request.form.get('Latitude', '')
        longitude = request.form.get('Longitude', '')

        resp = MessagingResponse()

        # ── Handle image sent on WhatsApp ──────────────────────────────────
        if num_media > 0:
            media_url = request.form.get('MediaUrl0', '')
            media_type = request.form.get('MediaContentType0', 'image/jpeg')

            if 'image' in media_type:
                account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
                auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
                img_response = req.get(media_url, auth=(account_sid, auth_token), timeout=15)
                image_base64 = base64.b64encode(img_response.content).decode('utf-8')
                result = analyze_crop_image(image_base64, media_type)
                result = result.replace('**', '*').replace('# ', '').replace('## ', '')
                resp.message("🔬 *Disease Scanner*\n\n" + result)
            else:
                resp.message("⚠️ Please send an image of your crop for disease analysis.")
            return str(resp)

        # ── Handle location shared on WhatsApp ─────────────────────────────
        if latitude and longitude:
            weather_data = get_weather(float(latitude), float(longitude))
            if "error" in weather_data:
                resp.message("❌ Could not fetch weather. Please try again.")
                return str(resp)
            prompt = (
                f"Based on this weather data: {weather_data}, give a short 2-3 line "
                "farmer-friendly tip on how this weather affects farming today."
            )
            weather_data["farming_advice"] = get_ai_response(prompt, {})
            reply = (
                f"🌦️ *Weather Update*\n\n"
                f"📍 *Location:* {weather_data.get('location', 'Your area')}\n"
                f"🌡️ *Temperature:* {weather_data.get('temperature')}°C\n"
                f"💧 *Humidity:* {weather_data.get('humidity')}%\n"
                f"🌤️ *Condition:* {weather_data.get('condition')}\n"
                f"🌬️ *Wind:* {weather_data.get('wind_speed')} m/s\n\n"
                f"🌾 *Farming Advice:*\n{weather_data.get('farming_advice')}"
            )
            resp.message(reply)
            return str(resp)

        # ── Handle text message ────────────────────────────────────────────
        if not incoming_msg:
            resp.message(
                "Namaste! 🙏 Welcome to *KrishiBot*\n\n"
                "I can help you with:\n"
                "🌾 Crop advice\n"
                "🐛 Pest & disease\n"
                "🧪 Fertilizer guidance\n"
                "🌦️ Weather — *share your location* for real-time data\n"
                "📷 Disease scan — *send a crop photo*\n\n"
                "Just ask anything in English, Hindi or Kannada!"
            )
            return str(resp)

        # ── Weather by city name ───────────────────────────────────────────
        context = {}
        intent = classify_intent(incoming_msg)

        if intent == "weather":
            reply = (
                "🌦️ *Weather Feature*\n\n"
                "Share your *location* on WhatsApp for real-time weather:\n"
                "📎 Attachment → Location → Send\n\n"
                "Or visit: https://krishibot-flame.vercel.app"
            )

        elif intent == "pest":
            reply = get_pest_advice(incoming_msg)

        elif intent == "crop":
            reply = recommend_crops(incoming_msg, context)

        elif intent == "fertilizer":
            reply = get_fertilizer_advice(incoming_msg)

        else:
            reply = get_ai_response(incoming_msg, context)

        # Clean markdown for WhatsApp format
        reply = reply.replace('**', '*').replace('# ', '').replace('## ', '')

        resp.message(reply)
        return str(resp)

    except Exception as e:
        resp = MessagingResponse()
        resp.message("Sorry, something went wrong. Please try again. 🙏")
        return str(resp)


# ---------------------------------------------------------------------------
# Schemes & Loans Route
# ---------------------------------------------------------------------------

@app.route('/schemes', methods=['POST'])
def schemes():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        prompt = data.get('prompt', '').strip()
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        groq_key = os.environ.get("GROQ_API_KEY", "")
        if not groq_key:
            return jsonify({"error": "GROQ_API_KEY not set"}), 500

        response = req.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are KrishiBot, an expert on Indian government agricultural schemes, "
                            "loans, subsidies, and crop insurance. Give accurate, specific, and helpful "
                            "answers with actual numbers, amounts, and application steps. "
                            "Always be farmer-friendly and practical."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1024,
                "temperature": 0.4
            },
            timeout=30
        )
        result = response.json()
        if "choices" in result:
            text = result["choices"][0]["message"]["content"]
            return jsonify({"result": text})
        else:
            return jsonify({"error": result.get("error", {}).get("message", "Unknown error")}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# Mandi Price Routes (Agmarknet / data.gov.in)
# ---------------------------------------------------------------------------

AGMARKNET_BASE = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
AGMARKNET_KEY  = "579b464db66ec23bdd000001cdd3946e44ce4aab0b09b0b94bef91d8"

@app.route('/mandi/markets', methods=['GET'])
def mandi_markets():
    state = request.args.get('state', 'Karnataka')
    try:
        res = req.get(AGMARKNET_BASE, params={
            'api-key': AGMARKNET_KEY,
            'format': 'json',
            'filters[state]': state,
            'limit': 500,
        }, timeout=30)
        data = res.json()
        records = data.get('records', [])
        markets = sorted(set(r['market'] for r in records if r.get('market')))
        return jsonify({'markets': markets})
    except Exception as e:
        return jsonify({'markets': [], 'error': str(e)})


@app.route('/mandi/prices', methods=['GET'])
def mandi_prices():
    state  = request.args.get('state', 'Karnataka')
    market = request.args.get('market', '')
    date   = request.args.get('date', '')

    agmark_date = ''
    if date:
        try:
            from datetime import datetime
            d = datetime.strptime(date, '%Y-%m-%d')
            agmark_date = d.strftime('%d/%m/%Y')
        except:
            pass

    try:
        params = {
            'api-key': AGMARKNET_KEY,
            'format': 'json',
            'filters[state]': state,
            'limit': 500,
        }
        if market:
            params['filters[market]'] = market
        if agmark_date:
            params['filters[arrival_date]'] = agmark_date

        res = req.get(AGMARKNET_BASE, params=params, timeout=30)
        data = res.json()
        records = data.get('records', [])

        prices = []
        for r in records:
            try:
                prices.append({
                    'commodity':   r.get('commodity', ''),
                    'variety':     r.get('variety', ''),
                    'unit':        'quintal',
                    'min_price':   float(r.get('min_price', 0)),
                    'max_price':   float(r.get('max_price', 0)),
                    'modal_price': float(r.get('modal_price', 0)),
                    'date':        r.get('arrival_date', ''),
                    'trend':       None,
                })
            except:
                continue

        prices.sort(key=lambda x: x['commodity'])
        return jsonify({'prices': prices, 'count': len(prices)})

    except Exception as e:
        return jsonify({'prices': [], 'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
