"""
KrishiBot - Main Flask Application
Uses AI-powered intent classification instead of brittle keyword matching.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge
import os
import json
import base64
import re
import requests as req
from urllib.parse import urlsplit
from twilio.request_validator import RequestValidator

from modules.weather import get_weather, validate_coordinates
from modules.crop_recommender import recommend_crops
from modules.pest_advisor import get_pest_advice
from modules.fertilizer import get_fertilizer_advice
from modules.ai_assistant import AIProviderError, get_ai_response
from modules.conversation import normalize_history
from modules.image_analyzer import ImageAnalysisError, analyze_crop_image
from modules.rate_limiter import enforce_limit, rate_limit

app = Flask(__name__)
configured_origins = os.environ.get("CORS_ORIGINS", "").strip()
cors_origins = [origin.strip() for origin in configured_origins.split(",") if origin.strip()] if configured_origins else [
    "http://localhost:5173", "http://127.0.0.1:5173", "https://krishibot-flame.vercel.app"
]
CORS(app, resources={r"/*": {"origins": cors_origins}})
MAX_REQUEST_BYTES = 10 * 1024 * 1024
MAX_CHAT_CHARS = 4000
MAX_PROMPT_CHARS = 8000
MAX_IMAGE_BYTES = 8 * 1024 * 1024
app.config["MAX_CONTENT_LENGTH"] = MAX_REQUEST_BYTES


@app.errorhandler(RequestEntityTooLarge)
def request_too_large(_error):
    return jsonify({"error": "Request exceeds the allowed size limit."}), 413


def _json_body():
    if not request.is_json:
        return None, (jsonify({"error": "Content-Type must be application/json."}), 415)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, (jsonify({"error": "Request body must be a JSON object."}), 400)
    return data, None


def _public_whatsapp_url():
    """Return the configured public callback URL used by Twilio to sign webhooks."""
    value = os.environ.get("TWILIO_WEBHOOK_URL", "").strip()
    try:
        parsed = urlsplit(value)
        if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
                or parsed.path != "/whatsapp" or parsed.fragment):
            return None
        return value
    except ValueError:
        return None


def _valid_twilio_signature():
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
    public_url = _public_whatsapp_url()
    signature = request.headers.get("X-Twilio-Signature", "")
    if not auth_token or not public_url or not signature:
        return False
    try:
        return RequestValidator(auth_token).validate(public_url, request.form, signature)
    except RequestEntityTooLarge:
        raise
    except Exception:
        return False


def _is_twilio_media_url(media_url, account_sid):
    """Accept only this account's HTTPS Twilio message media resource URL."""
    try:
        parsed = urlsplit(media_url)
        if (parsed.scheme != "https" or parsed.hostname != "api.twilio.com"
                or parsed.port not in (None, 443) or parsed.username or parsed.password
                or parsed.query or parsed.fragment):
            return False
        segments = parsed.path.split("/")
        return (
            len(segments) == 8 and segments[1:4] == ["2010-04-01", "Accounts", account_sid]
            and segments[4] == "Messages"
            and re.fullmatch(r"(?:SM|MM)[0-9a-fA-F]{32}", segments[5]) is not None
            and segments[6] == "Media"
            and re.fullmatch(r"ME[0-9a-fA-F]{32}", segments[7]) is not None
        )
    except (TypeError, ValueError):
        return False


def _image_type_matches(image_bytes, mime_type):
    signatures = {
        "image/jpeg": lambda data: data.startswith(b"\xff\xd8\xff"),
        "image/png": lambda data: data.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/gif": lambda data: data.startswith((b"GIF87a", b"GIF89a")),
        "image/webp": lambda data: len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP",
    }
    if not isinstance(mime_type, str):
        return False
    check = signatures.get(mime_type.split(";", 1)[0].strip().lower())
    return bool(image_bytes and check and check(image_bytes))


def _image_diagnosis_text(diagnosis):
    """Render the structured result as simple text for the WhatsApp channel."""
    lines = []
    if diagnosis.get("crop"):
        lines.append(f"Crop: {diagnosis['crop']}")
    if diagnosis.get("visible_symptoms"):
        lines.append("Visible symptoms: " + "; ".join(diagnosis["visible_symptoms"]))
    lines.append("Suspected issue: " + (diagnosis.get("suspected_disease") or "Uncertain from this image"))
    lines.append("Assessment: " + diagnosis.get("confidence_status", "uncertain"))
    if diagnosis.get("severity"):
        lines.append("Severity: " + diagnosis["severity"])
    for section, key in (("Immediate steps", "immediate_steps"), ("Organic options", "organic"),
                         ("Chemical options", "chemical")):
        items = diagnosis.get("treatment", {}).get(key, [])
        if items:
            lines.append(section + ": " + "; ".join(items))
    if diagnosis.get("prevention"):
        lines.append("Prevention: " + "; ".join(diagnosis["prevention"]))
    if diagnosis.get("additional_information_needed"):
        lines.append("To narrow this down: " + "; ".join(diagnosis["additional_information_needed"]))
    lines.append("Photo-based guidance is preliminary. Confirm diagnosis and treatment with your local KVK/agricultural officer.")
    return "\n".join(lines)


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
    except Exception:
        print("[session] Save failed.")

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


# ---------------------------------------------------------------------------
# AI-powered intent classifier
# ---------------------------------------------------------------------------

INTENT_SYSTEM_PROMPT = """You classify a farmer's current message into exactly one intent:
weather (weather, rain, forecast, temperature, humidity),
pest (pests, insects, disease, symptoms, crop damage or treatment),
crop (crop selection or recommendations),
fertilizer (fertilizers, nutrients, NPK, manure),
general (other farming questions, greetings, or unclear messages).
Use recent conversation context to resolve short follow-ups. Do not infer a specialist intent from an unrelated old topic. If context and message do not establish a clear topic, return general with low confidence.
Return only JSON: {"intent":"pest","confidence":"high"}. Confidence must be high or low.
"""


def classify_intent(message: str, history=None, language="en") -> dict:
    """Classify using a bounded recent transcript; safely fall back on provider errors."""
    try:
        from groq import Groq
        key = os.environ.get("GROQ_API_KEY", "")
        if not key:
            raise RuntimeError("provider key missing")
        client = Groq(api_key=key)
        transcript = normalize_history(history, current_message=message)
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            max_tokens=60,
            temperature=0,
            messages=[
                {"role":"system", "content":INTENT_SYSTEM_PROMPT},
                {"role":"user", "content":"Selected response language: " + language + "\nRecent conversation: " + json.dumps(transcript, ensure_ascii=False) + "\nCurrent message: " + message},
            ],
        )
        raw = response.choices[0].message.content.strip().removeprefix("```json").removesuffix("```").strip()
        data = json.loads(raw)
        intent = data.get("intent") if isinstance(data, dict) else None
        confidence = data.get("confidence") if isinstance(data, dict) else None
        if intent not in ("weather", "pest", "crop", "fertilizer", "general"):
            return {"intent":_fallback_intent(message, history), "confidence":"low"}
        return {"intent":intent, "confidence":confidence if confidence in ("high", "low") else "low"}
    except Exception:
        print("[intent_classifier] Request failed; using bounded local context fallback.")
        return {"intent":_fallback_intent(message, history), "confidence":"low"}


def _fallback_intent(message, history=None):
    terms = {
        "weather": ("weather", "temperature", "humidity", "forecast", "rain", "बारिश", "मौसम", "ಹವಾಮಾನ", "ಮಳೆ"),
        "fertilizer": ("fertilizer", "manure", "npk", "nutrient", "urea", "खाद", "उर्वरक", "ಗೊಬ್ಬರ"),
        "pest": ("pest", "disease", "spots", "yellowing", "aphid", "insect", "कीट", "रोग", "ಕೀಟ", "ರೋಗ"),
        "crop": ("which crop", "what to grow", "crop recommendation", "season", "soil type", "black soil", "sandy soil", "loamy soil", "clay soil", "red soil", "kharif", "rabi", "zaid", "कौन सी फसल", "ಯಾವ ಬೆಳೆ"),
    }
    def match(text):
        for intent, keywords in terms.items():
            if any(keyword in text for keyword in keywords):
                return intent
        return None

    current_intent = match(message.lower())
    if current_intent:
        return current_intent
    for turn in reversed(normalize_history(history, message)):
        if turn["role"] == "user":
            history_intent = match(turn["content"].lower())
            if history_intent:
                return history_intent
    return "general"


def _ambiguous_follow_up(message):
    text = re.sub(r"[^\w\s]", "", message.lower()).strip()
    vague = {"yes", "no", "maybe", "ok", "okay", "what about it", "what about that", "tell me more", "help", "and then", "what should i do", "what do i do", "फिर", "हाँ", "ಹೌದು"}
    words = text.split()
    confirmation = words[0] in ("yes", "no", "okay", "ok", "maybe", "हाँ", "ಹೌದು") if words else False
    return text in vague or (confirmation and len(words) <= 8) or (len(words) <= 3 and any(word in words for word in ("it", "that", "those", "them", "यह", "ಅದು")))


def _clarification_message(language):
    return {
        "en":"I’m not sure which farming topic you mean. Are you asking about weather, crop choice, pests or disease, or fertilizer?",
        "hi":"मुझे स्पष्ट नहीं है कि आप किस खेती के विषय के बारे में पूछ रहे हैं। क्या यह मौसम, फसल चयन, कीट या रोग, अथवा खाद के बारे में है?",
        "kn":"ನೀವು ಯಾವ ಕೃಷಿ ವಿಷಯದ ಬಗ್ಗೆ ಕೇಳುತ್ತಿದ್ದೀರಿ ಎಂಬುದು ಸ್ಪಷ್ಟವಾಗಿಲ್ಲ. ಇದು ಹವಾಮಾನ, ಬೆಳೆ ಆಯ್ಕೆ, ಕೀಟ ಅಥವಾ ರೋಗ, ಅಥವಾ ಗೊಬ್ಬರದ ಬಗ್ಗೆವೇ?",
    }.get(language, "I’m not sure which farming topic you mean. Could you clarify?")


def _localized_provider_error(language, configured=False):
    messages = {
        "en": "The AI service is not configured. Please try again later." if configured else "The AI service is temporarily unavailable. Please try again.",
        "hi": "AI सेवा अभी कॉन्फ़िगर नहीं है। कृपया बाद में फिर कोशिश करें।" if configured else "AI सेवा अभी उपलब्ध नहीं है। कृपया फिर कोशिश करें।",
        "kn": "AI ಸೇವೆಯನ್ನು ಇನ್ನೂ ಹೊಂದಿಸಿಲ್ಲ. ದಯವಿಟ್ಟು ನಂತರ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ." if configured else "AI ಸೇವೆ ತಾತ್ಕಾಲಿಕವಾಗಿ ಲಭ್ಯವಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
    }
    return messages.get(language, messages["en"])


def _intent_name(classification):
    if isinstance(classification, dict):
        value = classification.get("intent", "general")
    else:
        value = classification
    return value if value in ("weather", "pest", "crop", "fertilizer", "general") else "general"

# Routes
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return jsonify({"message": "KrishiBot API is running!", "version": "3.0"})


@app.route('/health')
def health():
    return jsonify({"status": "ok"})


@app.route('/chat', methods=['POST'])
@rate_limit("chat")
def chat():
    try:
        data, error_response = _json_body()
        if error_response:
            return error_response

        message = data.get('message', '')
        if not isinstance(message, str):
            return jsonify({"error": "Message must be text."}), 400
        message = message.strip()
        if len(message) > MAX_CHAT_CHARS:
            return jsonify({"error": f"Message exceeds the {MAX_CHAT_CHARS}-character limit."}), 413
        language = data.get('language', 'en')
        if language not in ('en', 'hi', 'kn'):
            language = 'en'
        context = data.get('context', {})
        if not isinstance(context, dict):
            context = {}
        context['history'] = normalize_history(context.get('history'), current_message=message)
        lat = data.get('lat')
        lon = data.get('lon')

        if not message:
            return jsonify({"error": "No message provided"}), 400

        if lat is not None and lon is not None:
            context['location_status'] = f"User's GPS location is available (lat={lat}, lon={lon}). Location was successfully shared via the app."
        elif lat is not None or lon is not None:
            return jsonify({"status": "error", "message": "Latitude and longitude must be provided together."}), 400
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

        classification = classify_intent(message, context['history'], language)
        if isinstance(classification, str):  # supports older integrations and simple test doubles
            classification = {"intent":classification, "confidence":"high"}
        if not isinstance(classification, dict):
            classification = {"intent":"general", "confidence":"low"}
        intent = classification.get("intent", "general")
        confidence = classification.get("confidence", "low")
        if intent not in ("weather", "pest", "crop", "fertilizer", "general"):
            intent, confidence = "general", "low"
        if confidence not in ("high", "low"):
            confidence = "low"
        if _ambiguous_follow_up(message):
            inferred_intent = _fallback_intent(message, context['history']) if context['history'] else "general"
            if inferred_intent in ("weather", "pest", "crop", "fertilizer"):
                intent = inferred_intent
            elif confidence == "low" or re.sub(r"[^\w\s]", "", message.lower()).strip() in {
                "yes", "no", "maybe", "ok", "okay", "what about it", "what about that", "tell me more", "help", "and then", "what should i do", "what do i do", "फिर", "हाँ", "ಹೌದು"
            }:
                return jsonify({"status":"clarification", "message":_clarification_message(language)})

        if intent == "weather":
            limited = enforce_limit("weather")
            if limited is not None:
                return limited
            if lat is not None and lon is not None:
                try:
                    lat, lon = validate_coordinates(lat, lon)
                except ValueError as error:
                    return jsonify({"status": "error", "message": str(error)}), 400
                weather_data = get_weather(lat, lon)
                if "error" in weather_data:
                    status_code = 503 if "not configured" in weather_data["error"].lower() else 502
                    return jsonify({"status": "error", "message": weather_data["error"]}), status_code
                return jsonify({"status": "weather", "data": weather_data})
            elif lat is not None or lon is not None:
                return jsonify({"status": "error", "message": "Latitude and longitude must be provided together."}), 400
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
            response = get_pest_advice(message, language=language, context=context)
            return jsonify({"status": "pest_advice", "message": response})

        elif intent == "crop":
            response = recommend_crops(message, context, language=language)
            return jsonify({"status": "crop_advice", "message": response})

        elif intent == "fertilizer":
            response = get_fertilizer_advice(message, language=language, context=context)
            return jsonify({"status": "fertilizer", "message": response})

        else:
            response = get_ai_response(message, context, language=language)
            return jsonify({"status": "ai_response", "message": response})

    except RequestEntityTooLarge:
        raise
    except AIProviderError as error:
        configured = "not configured" in str(error).lower()
        return jsonify({"status":"error", "code":"ai_provider_error", "message":_localized_provider_error(language, configured)}), 503 if configured else 502
    except Exception:
        return jsonify({"status": "error", "message": "We could not process that request. Please try again."}), 500


# ---------------------------------------------------------------------------
# Image Analysis Route (Groq Vision)
# ---------------------------------------------------------------------------

@app.route('/analyze-image', methods=['POST'])
@rate_limit("image")
def analyze_image():
    try:
        # Accept both FormData (from web app) and JSON (legacy)
        if request.content_type and 'multipart/form-data' in request.content_type:
            image_file = request.files.get('image')
            language   = request.form.get('language', 'en')
            question = request.form.get('message', '')
            if not image_file:
                return jsonify({"error": "No image file provided"}), 400
            mime_type = image_file.content_type or ''
            image_bytes = image_file.stream.read(MAX_IMAGE_BYTES + 1)
        else:
            data, error_response = _json_body()
            if error_response:
                return error_response
            image_base64 = data.get('image')
            mime_type    = data.get('mime_type', 'image/jpeg')
            language     = data.get('language', 'en')
            question = data.get('message', data.get('question', ''))
            if not isinstance(image_base64, str) or not image_base64:
                return jsonify({"error": "No image provided"}), 400
            if len(image_base64) > ((MAX_IMAGE_BYTES + 2) // 3) * 4:
                return jsonify({"error": "Image exceeds the 8 MB limit."}), 413
            try:
                image_bytes = base64.b64decode(image_base64, validate=True)
            except (ValueError, base64.binascii.Error):
                return jsonify({"error": "Image must be valid base64 data."}), 400

        if language not in ('en', 'hi', 'kn'):
            language = 'en'
        if not isinstance(question, str):
            return jsonify({"error": "Question must be text."}), 400
        if len(question) > MAX_CHAT_CHARS:
            return jsonify({"error": f"Question exceeds the {MAX_CHAT_CHARS}-character limit."}), 413

        if len(image_bytes) > MAX_IMAGE_BYTES:
            return jsonify({"error": "Image exceeds the 8 MB limit."}), 413
        if not _image_type_matches(image_bytes, mime_type):
            return jsonify({"error": "Upload a valid JPEG, PNG, GIF, or WebP image."}), 415
        image_base64 = base64.b64encode(image_bytes).decode('ascii')

        result = analyze_crop_image(image_base64, mime_type, language=language, question=question)
        return jsonify({"status": "image_analysis", "diagnosis": result})

    except RequestEntityTooLarge:
        raise
    except ImageAnalysisError as error:
        status_code = 503 if "not configured" in str(error).lower() else 502
        return jsonify({"status": "error", "error": "image_analysis_failed", "message": str(error)}), status_code
    except Exception:
        return jsonify({"status": "error", "error": "image_analysis_failed", "message": "Image analysis could not be completed. Please try again."}), 500


# ---------------------------------------------------------------------------
# WhatsApp Webhook (Twilio)
# ---------------------------------------------------------------------------

@app.route('/whatsapp', methods=['POST'])
def whatsapp():
    try:
        from twilio.twiml.messaging_response import MessagingResponse
        import requests as req

        if not os.environ.get('TWILIO_AUTH_TOKEN') or not _public_whatsapp_url():
            return jsonify({"error": "WhatsApp webhook is not configured."}), 503
        if not _valid_twilio_signature():
            return jsonify({"error": "Invalid Twilio signature."}), 403

        sender = request.form.get('From', '')
        # The signed sender field provides a stable per-farmer identity for
        # Twilio, whose webhook infrastructure may be shared by many users.
        sender_identity = sender if re.fullmatch(r"whatsapp:\+\d{7,15}", sender) else None
        limited = enforce_limit("whatsapp", identity=sender_identity)
        if limited is not None:
            return limited

        incoming_msg = request.form.get('Body', '').strip()
        try:
            num_media = int(request.form.get('NumMedia', 0))
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid media count."}), 400
        if num_media < 0 or num_media > 10:
            return jsonify({"error": "Invalid media count."}), 400
        latitude = request.form.get('Latitude') or None
        longitude = request.form.get('Longitude') or None

        resp = MessagingResponse()

        # ── Handle image sent on WhatsApp ──────────────────────────────────
        if num_media > 0:
            media_url = request.form.get('MediaUrl0', '')
            media_type = request.form.get('MediaContentType0', 'image/jpeg')

            if 'image' in media_type:
                account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
                auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
                if not account_sid or not auth_token:
                    resp.message("WhatsApp image analysis is not configured. Please contact support.")
                    return str(resp), 503
                if not _is_twilio_media_url(media_url, account_sid):
                    resp.message("The image link could not be verified. Please send the crop photo again.")
                    return str(resp), 400
                try:
                    img_response = req.get(
                        media_url, auth=(account_sid, auth_token), timeout=15,
                        allow_redirects=False, stream=True
                    )
                    if 300 <= img_response.status_code < 400:
                        img_response.close()
                        resp.message("The image link could not be downloaded safely. Please send it again.")
                        return str(resp), 400
                    img_response.raise_for_status()
                    response_type = img_response.headers.get('Content-Type', '').split(';', 1)[0].strip().lower()
                    content_length = img_response.headers.get('Content-Length')
                    if content_length and int(content_length) > MAX_IMAGE_BYTES:
                        img_response.close()
                        resp.message("The image is too large. Please send an image under 8 MB.")
                        return str(resp), 413
                    image_bytes = img_response.raw.read(MAX_IMAGE_BYTES + 1)
                    img_response.close()
                except Exception:
                    resp.message("Could not download the image from Twilio. Please send it again.")
                    return str(resp), 502
                if len(image_bytes) > MAX_IMAGE_BYTES:
                    resp.message("The image is too large. Please send an image under 8 MB.")
                    return str(resp), 413
                if not _image_type_matches(image_bytes, response_type):
                    resp.message("The downloaded file was not a supported image. Please send a JPEG, PNG, GIF, or WebP photo.")
                    return str(resp), 415
                image_base64 = base64.b64encode(image_bytes).decode('ascii')
                result = analyze_crop_image(image_base64, response_type, language="en", question=incoming_msg)
                result = _image_diagnosis_text(result)
                resp.message("🔬 *Disease Scanner*\n\n" + result)
            else:
                resp.message("⚠️ Please send an image of your crop for disease analysis.")
            return str(resp)

        # ── Handle location shared on WhatsApp ─────────────────────────────
        if latitude is not None and longitude is not None:
            weather_data = get_weather(latitude, longitude)
            if "error" in weather_data:
                resp.message("❌ Could not fetch weather. Please try again.")
                return str(resp)
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
        intent = _intent_name(classify_intent(incoming_msg, context.get("history"), "en"))

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

    except RequestEntityTooLarge:
        raise
    except AIProviderError as error:
        resp = MessagingResponse()
        configured = "not configured" in str(error).lower()
        resp.message(_localized_provider_error("en", configured))
        return str(resp), 503 if configured else 502
    except Exception:
        resp = MessagingResponse()
        resp.message("Sorry, something went wrong. Please try again. 🙏")
        return str(resp)


# ---------------------------------------------------------------------------
# Schemes & Loans Route
# ---------------------------------------------------------------------------

@app.route('/schemes', methods=['POST'])
@rate_limit("schemes")
def schemes():
    try:
        data, error_response = _json_body()
        if error_response:
            return error_response

        prompt = data.get('prompt', '')
        if not isinstance(prompt, str):
            return jsonify({"error": "Prompt must be text."}), 400
        prompt = prompt.strip()
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        if len(prompt) > MAX_PROMPT_CHARS:
            return jsonify({"error": f"Prompt exceeds the {MAX_PROMPT_CHARS}-character limit."}), 413

        groq_key = os.environ.get("GROQ_API_KEY", "")
        if not groq_key:
            return jsonify({"status":"error", "error":"ai_provider_unconfigured", "message":"AI service is not configured. Please try again later."}), 503

        response = req.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-oss-120b",
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
        response.raise_for_status()
        result = response.json()
        if "choices" in result:
            text = result["choices"][0]["message"]["content"]
            if not isinstance(text, str) or not text.strip():
                return jsonify({"status":"error", "error":"ai_provider_invalid_response", "message":"AI service returned an invalid response."}), 502
            return jsonify({"result": text})
        else:
            return jsonify({"status":"error", "error":"ai_provider_invalid_response", "message":"AI service returned an invalid response."}), 502

    except RequestEntityTooLarge:
        raise
    except Exception:
        return jsonify({"status":"error", "error":"ai_provider_unavailable", "message":"AI service is temporarily unavailable. Please try again."}), 502


# ---------------------------------------------------------------------------
# Mandi Price Routes (Agmarknet / data.gov.in)
# ---------------------------------------------------------------------------

AGMARKNET_BASE = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
AGMARKNET_KEY = os.environ.get("AGMARKNET_API_KEY", "")

@app.route('/mandi/markets', methods=['GET'])
@rate_limit("mandi_markets")
def mandi_markets():
    state = request.args.get('state', 'Karnataka')
    if not AGMARKNET_KEY:
        return jsonify({'markets': [], 'error': 'Mandi data service is not configured.'}), 503
    try:
        res = req.get(AGMARKNET_BASE, params={
            'api-key': AGMARKNET_KEY,
            'format': 'json',
            'filters[state]': state,
            'limit': 500,
        }, timeout=30)
        res.raise_for_status()
        data = res.json()
        records = data.get('records', [])
        markets = sorted(set(r['market'] for r in records if r.get('market')))
        return jsonify({'markets': markets})
    except Exception:
        return jsonify({'markets': [], 'error': 'Mandi data service is temporarily unavailable.'}), 502


@app.route('/mandi/prices', methods=['GET'])
@rate_limit("mandi_prices")
def mandi_prices():
    state  = request.args.get('state', 'Karnataka')
    market = request.args.get('market', '')
    date   = request.args.get('date', '')

    if not AGMARKNET_KEY:
        return jsonify({'prices': [], 'error': 'Mandi data service is not configured.'}), 503

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
        res.raise_for_status()
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

    except Exception:
        return jsonify({'prices': [], 'error': 'Mandi data service is temporarily unavailable.'}), 502


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
