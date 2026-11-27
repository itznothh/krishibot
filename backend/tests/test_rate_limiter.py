import os
import unittest
from unittest.mock import patch

import app as api
from modules.rate_limiter import _client_address, limiter


class RateLimitTests(unittest.TestCase):
    def setUp(self):
        limiter.clear()
        self.client = api.app.test_client()

    def tearDown(self):
        limiter.clear()

    def test_allowed_request_reaches_existing_endpoint(self):
        response = self.client.post("/schemes", json={"prompt": "PM-KISAN"})
        # Missing provider credentials are a normal endpoint response; the
        # request was allowed through the limiter.
        self.assertEqual(response.status_code, 503)
        self.assertNotEqual(response.get_json().get("error"), "rate_limit_exceeded")

    def test_limit_returns_safe_429_and_retry_after(self):
        with patch.dict(os.environ, {"RATE_LIMIT_SCHEMES_PER_MINUTE": "1", "GROQ_API_KEY": ""}):
            first = self.client.post("/schemes", json={"prompt": "PM-KISAN"})
            second = self.client.post("/schemes", json={"prompt": "PM-KISAN"})
        self.assertEqual(first.status_code, 503)
        self.assertEqual(second.status_code, 429)
        self.assertEqual(second.get_json()["error"], "rate_limit_exceeded")
        self.assertIn("Retry-After", second.headers)
        self.assertNotIn("GROQ_API_KEY", second.get_data(as_text=True))

    def test_limits_are_isolated_by_endpoint(self):
        with patch.dict(os.environ, {"RATE_LIMIT_SCHEMES_PER_MINUTE": "1"}):
            schemes = self.client.post("/schemes", json={"prompt": "PM-KISAN"})
            image = self.client.post("/analyze-image", json={})
            schemes_again = self.client.post("/schemes", json={"prompt": "PM-KISAN"})
        self.assertNotEqual(schemes.status_code, 429)
        self.assertEqual(image.status_code, 400)
        self.assertEqual(schemes_again.status_code, 429)

    def test_forwarded_headers_are_ignored_unless_hop_count_is_configured(self):
        with api.app.test_request_context(
            "/", environ_base={"REMOTE_ADDR": "192.0.2.8"},
            headers={"X-Forwarded-For": "198.51.100.10"},
        ):
            with patch.dict(os.environ, {"RATE_LIMIT_TRUSTED_PROXY_HOPS": "0"}):
                self.assertEqual(_client_address(), "192.0.2.8")
            with patch.dict(os.environ, {"RATE_LIMIT_TRUSTED_PROXY_HOPS": "1"}):
                self.assertEqual(_client_address(), "198.51.100.10")

        # Walk back from the trusted proxy hops, rather than taking the
        # leftmost caller-supplied value in an append-style XFF chain.
        with api.app.test_request_context(
            "/", environ_base={"REMOTE_ADDR": "192.0.2.8"},
            headers={"X-Forwarded-For": "203.0.113.99, 198.51.100.10, 192.0.2.7"},
        ):
            with patch.dict(os.environ, {"RATE_LIMIT_TRUSTED_PROXY_HOPS": "2"}):
                self.assertEqual(_client_address(), "198.51.100.10")


if __name__ == "__main__":
    unittest.main()
