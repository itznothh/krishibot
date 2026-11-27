"""OpenWeatherMap current conditions and cautious, rule-based farm guidance."""
from datetime import datetime, timezone
import math
import os

import requests

OPENWEATHER_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


def validate_coordinates(lat, lon):
    """Return numeric coordinates, including valid zeroes, or raise ValueError."""
    if lat is None or lon is None or isinstance(lat, bool) or isinstance(lon, bool):
        raise ValueError("Share a location or enter valid latitude and longitude.")
    try:
        lat, lon = float(lat), float(lon)
    except (TypeError, ValueError):
        raise ValueError("Latitude and longitude must be numbers.")
    if not math.isfinite(lat) or not math.isfinite(lon):
        raise ValueError("Latitude and longitude must be finite numbers.")
    if not -90 <= lat <= 90 or not -180 <= lon <= 180:
        raise ValueError("Latitude must be between -90 and 90 and longitude between -180 and 180.")
    return lat, lon


def get_weather(lat, lon):
    try:
        lat, lon = validate_coordinates(lat, lon)
    except ValueError as error:
        return {"error": str(error)}
    if not OPENWEATHER_KEY:
        return {"error": "Weather service is not configured. Please try again later."}

    try:
        response = requests.get(
            OPENWEATHER_URL,
            params={"lat": lat, "lon": lon, "appid": OPENWEATHER_KEY, "units": "metric"},
            timeout=10,
        )
        if response.status_code != 200:
            return {"error": "Weather service could not retrieve current conditions."}
        data = response.json()
        main = data["main"]
        conditions = data["weather"]
        wind = data.get("wind", {})
        if not isinstance(main, dict) or not isinstance(conditions, list) or not conditions or not isinstance(conditions[0], dict):
            return {"error": "Weather service returned incomplete current conditions."}
        temperature = float(main["temp"])
        humidity = int(main["humidity"])
        wind_speed = float(wind["speed"]) if wind.get("speed") is not None else None
        if not (math.isfinite(temperature) and 0 <= humidity <= 100 and (wind_speed is None or math.isfinite(wind_speed))):
            return {"error": "Weather service returned invalid current conditions."}
        condition = str(conditions[0].get("main") or "Unknown")
        description = str(conditions[0].get("description") or condition).capitalize()
        observed_at = data.get("dt")
        observed_iso = datetime.fromtimestamp(observed_at, timezone.utc).isoformat() if isinstance(observed_at, (int, float)) else None
        result = {
            "location": str(data.get("name") or "Your location"),
            "city": str(data.get("name") or "Your location"),
            "temperature": round(temperature, 1),
            "condition": condition,
            "description": description,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "farming_advice": _get_farming_advice(condition, temperature, humidity, wind_speed, data.get("rain", {})),
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "observed_at": observed_iso,
            "source": "OpenWeatherMap",
            "data_type": "current",
        }
        return result
    except requests.exceptions.Timeout:
        return {"error": "Weather request timed out. Please try again."}
    except requests.exceptions.RequestException:
        return {"error": "Weather service is temporarily unavailable."}
    except (KeyError, TypeError, ValueError, OverflowError):
        return {"error": "Weather service returned invalid current conditions."}


def _get_farming_advice(condition, temperature, humidity, wind_speed, rain):
    condition = condition.lower()
    advice = []
    rain_amount = 0.0
    if isinstance(rain, dict):
        for period in ("1h", "3h"):
            try:
                rain_amount = max(rain_amount, float(rain.get(period, 0) or 0))
            except (TypeError, ValueError):
                pass
    if "thunderstorm" in condition:
        advice.append("Thunderstorms are occurring now. Avoid exposed field work and check drainage and crop support after the storm.")
    elif "rain" in condition or rain_amount >= 7.5:
        advice.append("Rain is reported in current conditions. Check field drainage, avoid unnecessary irrigation, and inspect for waterlogging after rain.")
    if humidity >= 80:
        advice.append("Humidity is high; some fungal diseases can spread more readily in humid conditions. Scout crops for symptoms; humidity alone does not confirm disease.")
    if temperature >= 35:
        advice.append("High temperature can stress crops. Check soil moisture and irrigate when appropriate, preferably during cooler hours; avoid overwatering.")
    if wind_speed is not None and wind_speed >= 8:
        advice.append("Winds are strong enough to increase spray drift. Avoid spraying in strong or gusty wind and follow the product label and local guidance.")
    if "snow" in condition or temperature < 5:
        advice.append("Cold conditions may harm sensitive crops. Check local crop guidance and protect vulnerable plants where practical.")
    if not advice:
        advice.append("No strong weather-related precaution is indicated by these current readings. Continue routine crop scouting and follow local conditions.")
    return " ".join(advice)
