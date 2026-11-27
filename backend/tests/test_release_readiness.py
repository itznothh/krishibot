import unittest
import io
import os
from unittest.mock import Mock, patch

import app as api
from modules.rate_limiter import limiter


class ReleaseReadinessTests(unittest.TestCase):
    def setUp(self):
        limiter.clear()
        self.client = api.app.test_client()

    def test_mandi_routes_report_missing_provider_key_without_external_request(self):
        with patch.object(api, "AGMARKNET_KEY", ""), patch.object(api.req, "get") as get:
            markets = self.client.get("/mandi/markets")
            prices = self.client.get("/mandi/prices")
        self.assertEqual(markets.status_code, 503)
        self.assertEqual(prices.status_code, 503)
        get.assert_not_called()
        self.assertNotIn("api-key", markets.get_data(as_text=True))

    def test_mandi_provider_errors_are_sanitized(self):
        response = Mock()
        response.raise_for_status.side_effect = RuntimeError("provider URL contains secret")
        with patch.object(api, "AGMARKNET_KEY", "test-key"), patch.object(api.req, "get", return_value=response):
            markets = self.client.get("/mandi/markets")
            prices = self.client.get("/mandi/prices")
        self.assertEqual(markets.status_code, 502)
        self.assertEqual(prices.status_code, 502)
        self.assertNotIn("secret", markets.get_data(as_text=True))
        self.assertNotIn("secret", prices.get_data(as_text=True))

    def test_health_route_and_cors_allow_configured_frontend_only(self):
        health = self.client.get("/health", headers={"Origin":"https://krishibot-flame.vercel.app"})
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.get_json(), {"status":"ok"})
        self.assertEqual(health.headers.get("Access-Control-Allow-Origin"), "https://krishibot-flame.vercel.app")

        blocked = self.client.get("/health", headers={"Origin":"https://untrusted.invalid"})
        self.assertIsNone(blocked.headers.get("Access-Control-Allow-Origin"))

    def test_schemes_provider_missing_key_and_failures_are_safe(self):
        with patch.dict(os.environ, {"GROQ_API_KEY":""}), patch.object(api.req, "post") as post:
            missing = self.client.post("/schemes", json={"prompt":"Tell me about PM-KISAN"})
        self.assertEqual(missing.status_code, 503)
        post.assert_not_called()

        provider_response = Mock()
        provider_response.raise_for_status.side_effect = RuntimeError("private provider details")
        with patch.dict(os.environ, {"GROQ_API_KEY":"unit-test-key"}), patch.object(api.req, "post", return_value=provider_response):
            failure = self.client.post("/schemes", json={"prompt":"Tell me about PM-KISAN"})
        self.assertEqual(failure.status_code, 502)
        self.assertNotIn("private provider details", failure.get_data(as_text=True))

    def test_unexpected_image_provider_exceptions_do_not_leak_details(self):
        png = b"\x89PNG\r\n\x1a\n" + b"test-image"
        with patch.object(api, "analyze_crop_image", side_effect=RuntimeError("secret provider detail")):
            response = self.client.post(
                "/analyze-image",
                data={"image":(io.BytesIO(png), "leaf.png", "image/png")},
                content_type="multipart/form-data",
            )
        self.assertEqual(response.status_code, 500)
        self.assertNotIn("secret provider detail", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
