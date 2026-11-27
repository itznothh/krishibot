import unittest
from unittest.mock import Mock, patch

import app as api
from modules import weather
from modules.rate_limiter import limiter


class WeatherTests(unittest.TestCase):
    def setUp(self):
        limiter.clear()
        self.client = api.app.test_client()

    def weather_response(self):
        response = Mock(status_code=200)
        response.json.return_value = {
            "name": "Farm Town", "dt": 1700000000,
            "main": {"temp": 36.4, "humidity": 86},
            "weather": [{"main": "Rain", "description": "light rain"}],
            "wind": {"speed": 9.2}, "rain": {"1h": 9.0},
        }
        return response

    def test_coordinates_accept_zero_and_reject_missing_malformed_and_out_of_range(self):
        self.assertEqual(weather.validate_coordinates(0, 0), (0.0, 0.0))
        for lat, lon in [(None, 2), (1, None), ("north", 2), (91, 2), (1, 181), (float("nan"), 2)]:
            with self.subTest(lat=lat, lon=lon), self.assertRaises(ValueError):
                weather.validate_coordinates(lat, lon)

    def test_weather_api_maps_fields_advisory_timestamp_and_current_label(self):
        with patch.object(weather, "OPENWEATHER_KEY", "unit-test-key"), patch.object(weather.requests, "get", return_value=self.weather_response()) as get:
            result = weather.get_weather(0, 0)
        self.assertEqual(result["location"], "Farm Town")
        self.assertEqual(result["city"], "Farm Town")
        self.assertEqual(result["condition"], "Rain")
        self.assertEqual(result["description"], "Light rain")
        self.assertIn("Humidity is high", result["farming_advice"])
        self.assertIn("drainage", result["farming_advice"])
        self.assertIn("spray drift", result["farming_advice"])
        self.assertEqual(result["data_type"], "current")
        self.assertEqual(result["source"], "OpenWeatherMap")
        self.assertTrue(result["retrieved_at"].startswith("20"))
        self.assertEqual(result["observed_at"], "2023-11-14T22:13:20+00:00")
        self.assertEqual(get.call_args.kwargs["params"]["lat"], 0.0)
        self.assertEqual(get.call_args.kwargs["params"]["lon"], 0.0)

    def test_missing_key_and_api_failure_return_safe_errors(self):
        with patch.object(weather, "OPENWEATHER_KEY", ""):
            self.assertIn("not configured", weather.get_weather(0, 0)["error"])
        failed = Mock(status_code=401)
        with patch.object(weather, "OPENWEATHER_KEY", "unit-test-key"), patch.object(weather.requests, "get", return_value=failed):
            self.assertIn("could not retrieve", weather.get_weather(1, 2)["error"])

    def test_chat_weather_route_accepts_zero_and_returns_mapping(self):
        with patch.object(api, "classify_intent", return_value="weather"), patch.object(api, "get_weather", return_value={"location":"Equator", "city":"Equator", "temperature":20, "condition":"Clouds", "description":"Overcast", "humidity":50, "wind_speed":0, "farming_advice":"Scout crops.", "retrieved_at":"2025-01-01T00:00:00+00:00", "source":"OpenWeatherMap", "data_type":"current"}) as get:
            response = self.client.post("/chat", json={"message":"weather today", "lat":0, "lon":0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["data"]["location"], "Equator")
        self.assertEqual(response.get_json()["data"]["data_type"], "current")
        get.assert_called_once_with(0.0, 0.0)

    def test_missing_and_invalid_coordinates_return_client_errors(self):
        with patch.object(api, "classify_intent", return_value="weather"):
            missing = self.client.post("/chat", json={"message":"weather"})
            partial = self.client.post("/chat", json={"message":"weather", "lat":0})
            invalid = self.client.post("/chat", json={"message":"weather", "lat":91, "lon":0})
        self.assertEqual(missing.get_json()["status"], "needs_location")
        self.assertEqual(partial.status_code, 400)
        self.assertEqual(invalid.status_code, 400)

    def test_missing_key_and_provider_failure_use_service_error_statuses(self):
        with patch.object(api, "classify_intent", return_value="weather"), patch.object(api, "get_weather", return_value={"error":"Weather service is not configured."}):
            no_key = self.client.post("/chat", json={"message":"weather", "lat":0, "lon":0})
        with patch.object(api, "classify_intent", return_value="weather"), patch.object(api, "get_weather", return_value={"error":"Weather service could not retrieve current conditions."}):
            provider_error = self.client.post("/chat", json={"message":"weather", "lat":0, "lon":0})
        self.assertEqual(no_key.status_code, 503)
        self.assertEqual(provider_error.status_code, 502)


if __name__ == "__main__":
    unittest.main()
