"""
KrishiBot - WhatsApp Cloud API Handler
Place this file in your backend/ folder alongside app.py
"""
import os
import requests

WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "")

def get_whatsapp_url():
    return f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

# In-memory session store
user_sessions = {}

def get_session(phone: str) -> dict:
    if phone not in user_sessions:
        user_sessions[phone] = {"lat": None, "lon": None, "history": []}
    return user_sessions[phone]

def update_history(phone: str, role: str, content: str):
    session = get_session(phone)
    session["history"].append({"role": role, "content": content})
    if len(session["history"]) > 10:
        session["history"] = session["history"][-10:]

def send_whatsapp_message(to: str, text: str):
    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        print("[WhatsApp] Missing WHATSAPP_TOKEN or PHONE_NUMBER_ID")
        return
    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
    for chunk in chunks:
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": chunk}
        }
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        try:
            resp = requests.post(get_whatsapp_url(), headers=headers, json=payload, timeout=10)
            if resp.status_code != 200:
                print(f"[WhatsApp] Send error: {resp.status_code} — {resp.text}")
        except Exception as e:
            print(f"[WhatsApp] Exception: {e}")

def format_weather_for_whatsapp(weather_data: dict) -> str:
    try:
        lines = ["🌤️ *Weather Report*\n"]
        if "city" in weather_data:
            lines.append(f"📍 *Location:* {weather_data['city']}")
        if "temperature" in weather_data:
            lines.append(f"🌡️ *Temperature:* {weather_data['temperature']}°C")
        if "humidity" in weather_data:
            lines.append(f"💧 *Humidity:* {weather_data['humidity']}%")
        if "description" in weather_data:
            lines.append(f"☁️ *Conditions:* {weather_data['description'].title()}")
        if "wind_speed" in weather_data:
            lines.append(f"💨 *Wind:* {weather_data['wind_speed']} km/h")
        if "rainfall" in weather_data:
            lines.append(f"🌧️ *Rainfall:* {weather_data['rainfall']} mm")
        if weather_data.get("farming_advice"):
            lines.append(f"\n🌾 *Farming Advice:*\n{weather_data['farming_advice']}")
        lines.append("\n📞 *Kisan Helpline: 1800-180-1551* (Free · 24x7)")
        return "\n".join(lines)
    except Exception:
        return "🌤️ Could not format weather. Please try again."

def process_whatsapp_message(phone: str, message_obj: dict) -> str:
    from app import classify_intent
    from modules.weather import get_weather
    from modules.crop_recommender import recommend_crops
    from modules.pest_advisor import get_pest_advice
    from modules.fertilizer import get_fertilizer_advice
    from modules.ai_assistant import get_ai_response

    session = get_session(phone)
    msg_type = message_obj.get("type", "text")

    if msg_type == "location":
        loc = message_obj.get("location", {})
        lat = loc.get("latitude")
        lon = loc.get("longitude")
        if lat and lon:
            session["lat"] = lat
            session["lon"] = lon
            return (
                "✅ *Location received!*\n\n"
                "Now you can ask me:\n"
                "• 'What's the weather today?'\n"
                "• 'Will it rain tomorrow?'\n"
                "• 'Is it good for spraying today?'\n\n"
                "🌾 What would you like to know?"
            )
        return "❌ Could not read location. Please try sharing again."

    if msg_type != "text":
        return "🌾 I support text and location messages. Type your farming question!"

    text = message_obj.get("text", {}).get("body", "").strip()
    if not text:
        return "Please type your farming question. I'm here to help! 🌱"

    update_history(phone, "user", text)
    lat = session.get("lat")
    lon = session.get("lon")

    context = {
        "history": session.get("history", []),
        "location_status": (
            f"User's GPS location is available (lat={lat}, lon={lon})."
            if lat and lon else
            "User has not shared GPS location yet."
        )
    }

    intent = classify_intent(text)

    if intent == "weather":
        if lat and lon:
            weather_data = get_weather(float(lat), float(lon))
            if "error" in weather_data:
                reply = f"❌ Could not fetch weather: {weather_data['error']}"
            else:
                msg_lower = text.lower()
                if any(w in msg_lower for w in ['rain', 'barish', 'rainfall', 'chances', 'will it rain']):
                    prompt = f"Based on this weather data: {weather_data}, what are the rain chances? Give a short 2-3 line farmer-friendly answer."
                else:
                    prompt = f"Based on this weather data: {weather_data}, give a short 2-3 line farmer-friendly tip on how this weather affects farming today."
                weather_data["farming_advice"] = get_ai_response(prompt, context)
                reply = format_weather_for_whatsapp(weather_data)
        else:
            reply = (
                "📍 *I need your location for weather info!*\n\n"
                "Please share your location:\n"
                "1. Tap 📎 attachment icon\n"
                "2. Select *Location*\n"
                "3. Tap *Send Your Current Location*"
            )
    elif intent == "pest":
        reply = get_pest_advice(text)
        reply += "\n\n📞 *Kisan Helpline: 1800-180-1551* (Free · 24x7)"
    elif intent == "crop":
        reply = recommend_crops(text, context)
        reply += "\n\n📞 *Kisan Helpline: 1800-180-1551* (Free · 24x7)"
    elif intent == "fertilizer":
        reply = get_fertilizer_advice(text)
        reply += "\n\n📞 *Kisan Helpline: 1800-180-1551* (Free · 24x7)"
    else:
        reply = get_ai_response(text, context)
        reply += "\n\n📞 *Kisan Helpline: 1800-180-1551* (Free · 24x7)"

    update_history(phone, "assistant", reply)
    return reply
