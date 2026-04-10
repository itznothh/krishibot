import requests
import os

OPENWEATHER_KEY = os.environ.get("OPENWEATHER_API_KEY", "")

def get_weather(lat: float, lon: float) -> dict:
    if not OPENWEATHER_KEY:
        return {"error": "Weather API key not configured."}
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}&units=metric"
        response = requests.get(url, timeout=10)
        data = response.json()

        if response.status_code != 200:
            return {"error": f"Weather fetch failed: {data.get('message', 'Unknown error')}"}

        weather = {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "condition": data["weather"][0]["description"].capitalize(),
            "wind_speed": data["wind"]["speed"],
            "location": data.get("name", "Your location"),
            "farming_advice": _get_farming_advice(data)
        }
        return weather

    except Exception as e:
        return {"error": f"Could not fetch weather: {str(e)}"}

def _get_farming_advice(data: dict) -> str:
    condition = data["weather"][0]["main"].lower()
    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]

    advice = []

    if "rain" in condition:
        advice.append("🌧️ Rain expected — skip irrigation today, ensure proper drainage.")
    elif "clear" in condition and temp > 35:
        advice.append("☀️ Hot and dry — irrigate crops early morning or evening.")
    elif "cloud" in condition:
        advice.append("⛅ Cloudy conditions — good time for spraying pesticides.")

    if humidity > 80:
        advice.append("💧 High humidity — watch for fungal diseases like blight.")
    elif humidity < 30:
        advice.append("🏜️ Low humidity — increase irrigation frequency.")

    if temp < 10:
        advice.append("🥶 Cold weather — protect sensitive crops from frost.")
    elif temp > 40:
        advice.append("🔥 Extreme heat — use mulching to retain soil moisture.")

    return " ".join(advice) if advice else "🌱 Weather looks suitable for regular farming activities."