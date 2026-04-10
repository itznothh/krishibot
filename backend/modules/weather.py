"""
KrishiBot - Weather Module
Uses Open-Meteo API — 100% FREE, no API key required.
https://open-meteo.com/
"""

import requests

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODE_URL    = "https://nominatim.openstreetmap.org/reverse"  # Free reverse geocoding

WMO_CODES = {
    0:  "Clear sky ☀️",        1: "Mainly clear 🌤️",
    2:  "Partly cloudy ⛅",    3: "Overcast ☁️",
    45: "Foggy 🌫️",           48: "Icy fog 🌫️",
    51: "Light drizzle 🌦️",   53: "Drizzle 🌦️",       55: "Heavy drizzle 🌧️",
    61: "Light rain 🌧️",      63: "Rain 🌧️",           65: "Heavy rain 🌧️",
    71: "Light snow 🌨️",      73: "Snow 🌨️",           75: "Heavy snow ❄️",
    80: "Rain showers 🌦️",    81: "Showers 🌦️",        82: "Violent showers ⛈️",
    95: "Thunderstorm ⛈️",    96: "Hail storm ⛈️",     99: "Heavy hail ⛈️",
}


def get_weather_data(lat: float, lon: float) -> dict:
    """
    Fetch real-time weather from Open-Meteo (no API key needed).
    Returns farming-relevant weather fields.
    """
    try:
        params = {
            "latitude":  lat,
            "longitude": lon,
            "current":   [
                "temperature_2m", "relative_humidity_2m",
                "weather_code", "wind_speed_10m",
                "precipitation", "cloud_cover"
            ],
            "hourly":    ["precipitation_probability"],
            "forecast_days": 1,
            "timezone":  "Asia/Kolkata"
        }
        resp = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        resp.raise_for_status()
        d = resp.json()
        cur = d["current"]

        # Rain probability: max over next 6 hours
        hourly_pop = d.get("hourly", {}).get("precipitation_probability", [0])
        rain_chance = max(hourly_pop[:6]) if hourly_pop else 0

        # Reverse geocode for location name (free via Nominatim)
        location = _reverse_geocode(lat, lon)

        code = cur.get("weather_code", 0)
        return {
            "location":    location,
            "temp":        round(cur["temperature_2m"], 1),
            "humidity":    cur["relative_humidity_2m"],
            "description": WMO_CODES.get(code, "Unknown"),
            "wind_speed":  round(cur["wind_speed_10m"], 1),
            "rain_chance": rain_chance,
            "rain_mm":     cur.get("precipitation", 0),
            "clouds":      cur.get("cloud_cover", 0),
            "weather_code": code,
        }

    except requests.exceptions.ConnectionError:
        return {"error": "Network error. Please check your internet connection."}
    except requests.exceptions.Timeout:
        return {"error": "Weather service timed out. Please try again."}
    except Exception as e:
        return {"error": f"Weather fetch failed: {str(e)}"}


def _reverse_geocode(lat: float, lon: float) -> str:
    """Get human-readable location name using Nominatim (free, no key)."""
    try:
        resp = requests.get(
            GEOCODE_URL,
            params={"lat": lat, "lon": lon, "format": "json"},
            headers={"User-Agent": "KrishiBot/1.0"},
            timeout=5
        )
        data = resp.json()
        addr = data.get("address", {})
        # Build short location: village/town + district + state
        parts = [
            addr.get("village") or addr.get("town") or addr.get("city") or addr.get("suburb"),
            addr.get("district") or addr.get("county"),
            addr.get("state")
        ]
        return ", ".join(p for p in parts if p) or "Your Location"
    except Exception:
        return "Your Location"


def get_farming_weather_advice(weather: dict) -> str:
    """Generate practical farming advice from weather data."""
    if "error" in weather:
        return "Unable to generate advice without weather data."

    advice = []
    temp        = weather.get("temp", 25)
    humidity    = weather.get("humidity", 60)
    rain_chance = weather.get("rain_chance", 0)
    wind_speed  = weather.get("wind_speed", 0)
    code        = weather.get("weather_code", 0)

    # Irrigation advice
    if rain_chance >= 70:
        advice.append(f"🚫 Skip irrigation today — high rain chance ({rain_chance}%). Save water!")
    elif rain_chance >= 40:
        advice.append(f"⚠️ Light irrigation only — moderate rain expected ({rain_chance}%).")
    elif humidity < 40 and temp > 32:
        advice.append("💧 Water your crops today — hot and dry. Best time: early morning or evening.")
    else:
        advice.append("✅ Normal irrigation schedule is fine today.")

    # Temperature
    if temp > 38:
        advice.append("🌡️ Extreme heat! Cover young seedlings and add mulch to retain moisture.")
    elif temp > 32:
        advice.append("☀️ High temperature — avoid applying fertilizers today (may burn crops).")
    elif temp < 10:
        advice.append("🥶 Cold weather — protect frost-sensitive crops with row covers or mulch.")
    elif 18 <= temp <= 28:
        advice.append("🌱 Ideal temperature for most crops. Great day for field work!")

    # Wind
    if wind_speed > 10:
        advice.append("💨 Strong winds — avoid spraying pesticides/fertilizers (drift risk).")

    # Humidity
    if humidity > 85:
        advice.append("🍄 High humidity — increased fungal disease risk. Inspect crops closely.")

    # Storm
    if code >= 95:
        advice.append("⛈️ Thunderstorm expected — stay indoors and secure farming equipment.")

    return "\n".join(advice) or "Normal farming conditions. Have a productive day! 🌾"
