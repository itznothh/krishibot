import io
import json
import os
import unittest
from unittest.mock import Mock, patch

from twilio.request_validator import RequestValidator

import app as api
from modules.rate_limiter import limiter


class WhatsAppSecurityTests(unittest.TestCase):
    public_url = "https://krishibot.example/whatsapp"
    auth_token = "unit-test-token"
    account_sid = "AC" + "a" * 32
    message_sid = "SM" + "b" * 32
    media_sid = "ME" + "c" * 32

    def setUp(self):
        limiter.clear()
        self.environment = patch.dict(os.environ, {
            "TWILIO_AUTH_TOKEN": self.auth_token,
            "TWILIO_ACCOUNT_SID": self.account_sid,
            "TWILIO_WEBHOOK_URL": self.public_url,
        })
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.client = api.app.test_client()

    def post_signed(self, fields, signature=None):
        if signature is None:
            signature = RequestValidator(self.auth_token).compute_signature(self.public_url, fields)
        return self.client.post(
            "/whatsapp", data=fields,
            headers={"X-Twilio-Signature": signature},
        )

    def test_missing_configuration_and_signatures_are_rejected(self):
        with patch.dict(os.environ, {"TWILIO_WEBHOOK_URL": ""}):
            response = self.client.post("/whatsapp", data={"Body": "hello"})
        self.assertEqual(response.status_code, 503)

        response = self.client.post("/whatsapp", data={"Body": "hello"})
        self.assertEqual(response.status_code, 403)

        response = self.post_signed({"Body": "hello"}, signature="invalid")
        self.assertEqual(response.status_code, 403)

    def test_signed_text_message_still_reaches_chat_handler(self):
        fields = {"Body": "hello", "From": "whatsapp:+10000000000", "NumMedia": "0"}
        with patch.object(api, "classify_intent", return_value="general"), \
                patch.object(api, "get_ai_response", return_value="Hello farmer"):
            response = self.post_signed(fields)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Hello farmer", response.get_data(as_text=True))

    def test_signed_whatsapp_requests_are_limited_per_sender(self):
        fields = {"Body": "hello", "From": "whatsapp:+10000000000", "NumMedia": "0"}
        with patch.dict(os.environ, {"RATE_LIMIT_WHATSAPP_PER_MINUTE": "1"}), \
                patch.object(api, "classify_intent", return_value="general"), \
                patch.object(api, "get_ai_response", return_value="Hello farmer"):
            first = self.post_signed(fields)
            second = self.post_signed(fields)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 429)
        self.assertEqual(second.get_json()["error"], "rate_limit_exceeded")

    def test_untrusted_media_url_is_rejected_before_fetch(self):
        fields = {
            "Body": "", "From": "whatsapp:+10000000000", "NumMedia": "1",
            "MediaContentType0": "image/jpeg",
            "MediaUrl0": "https://attacker.example/collect",
        }
        with patch("requests.get") as fetch:
            response = self.post_signed(fields)
        self.assertEqual(response.status_code, 400)
        fetch.assert_not_called()

    def test_missing_account_configuration_does_not_fetch_media(self):
        url = (
            "https://api.twilio.com/2010-04-01/Accounts/" + self.account_sid
            + "/Messages/" + self.message_sid + "/Media/" + self.media_sid
        )
        fields = {
            "Body": "", "From": "whatsapp:+10000000000", "NumMedia": "1",
            "MediaContentType0": "image/png", "MediaUrl0": url,
        }
        with patch.dict(os.environ, {"TWILIO_ACCOUNT_SID": ""}), patch("requests.get") as fetch:
            response = self.post_signed(fields)
        self.assertEqual(response.status_code, 503)
        fetch.assert_not_called()

    def test_redirect_from_twilio_media_is_not_followed(self):
        url = (
            "https://api.twilio.com/2010-04-01/Accounts/" + self.account_sid
            + "/Messages/" + self.message_sid + "/Media/" + self.media_sid
        )
        fields = {
            "Body": "", "From": "whatsapp:+10000000000", "NumMedia": "1",
            "MediaContentType0": "image/png", "MediaUrl0": url,
        }
        redirect = Mock(status_code=302, headers={"Location": "https://attacker.example/file"})
        with patch("requests.get", return_value=redirect) as fetch:
            response = self.post_signed(fields)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(fetch.call_count, 1)
        self.assertFalse(fetch.call_args.kwargs["allow_redirects"])
        self.assertEqual(fetch.call_args.kwargs["auth"], (self.account_sid, self.auth_token))
        redirect.close.assert_called_once()

    def test_valid_twilio_media_url_keeps_image_flow_working(self):
        url = (
            "https://api.twilio.com/2010-04-01/Accounts/" + self.account_sid
            + "/Messages/" + self.message_sid + "/Media/" + self.media_sid
        )
        png_bytes = b"\x89PNG\r\n\x1a\n" + b"unit-test-image"
        media = Mock(
            status_code=200,
            headers={"Content-Type": "image/png", "Content-Length": str(len(png_bytes))},
            raw=io.BytesIO(png_bytes),
        )
        fields = {
            "Body": "", "From": "whatsapp:+10000000000", "NumMedia": "1",
            "MediaContentType0": "image/png", "MediaUrl0": url,
        }
        with patch("requests.get", return_value=media) as fetch, \
                patch.object(api, "analyze_crop_image", return_value={
                    "success": True, "crop": "Tomato", "visible_symptoms": ["Leaf spots"],
                    "suspected_disease": "Possible leaf spot", "severity": "Mild",
                    "confidence_status": "moderate", "possible_causes": [],
                    "treatment": {"chemical": [], "organic": [], "immediate_steps": []},
                    "prevention": [], "additional_information_needed": [],
                }):
            response = self.post_signed(fields)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Possible leaf spot", response.get_data(as_text=True))
        fetch.assert_called_once()

    def test_bad_image_content_type_and_oversized_chat_are_rejected(self):
        response = self.client.post(
            "/analyze-image",
            data={"image": (io.BytesIO(b"not-an-image"), "crop.jpg", "image/jpeg")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 415)

        response = self.client.post("/chat", json={"message": "x" * (api.MAX_CHAT_CHARS + 1)})
        self.assertEqual(response.status_code, 413)


class ImageDiagnosisTests(unittest.TestCase):
    def setUp(self):
        limiter.clear()
        self.client = api.app.test_client()
        self.png = b"\x89PNG\r\n\x1a\n" + b"test-image"

    def mock_provider(self, diagnosis, status_code=200):
        response = Mock()
        response.status_code = status_code
        response.raise_for_status = Mock()
        response.json.return_value = {"choices": [{"message": {"content": json.dumps(diagnosis)}}]}
        if status_code >= 400:
            import requests
            response.raise_for_status.side_effect = requests.HTTPError("provider failure")
        return response

    def payload(self, **overrides):
        value = {
            "crop": "Tomato",
            "visible_symptoms": ["Small brown spots on lower leaves"],
            "suspected_disease": "Possible early blight",
            "severity": "Mild",
            "confidence_status": "moderate",
            "possible_causes": ["Fungal infection"],
            "treatment": {"chemical": [], "organic": ["Remove severely affected leaves"], "immediate_steps": ["Photograph both sides of leaves"]},
            "prevention": ["Avoid wetting foliage"],
            "additional_information_needed": [],
        }
        value.update(overrides)
        return value

    def post_image_with_provider(self, diagnosis, question="What are these spots?", language="hi"):
        with patch("modules.image_analyzer.GROQ_API_KEY", "unit-test-key"), \
                patch("modules.image_analyzer.requests.post", return_value=self.mock_provider(diagnosis)) as provider:
            response = self.client.post(
                "/analyze-image",
                data={"image": (io.BytesIO(self.png), "leaf.png", "image/png"), "message": question, "language": language},
                content_type="multipart/form-data",
            )
        return response, provider

    def test_missing_invalid_and_oversized_images_are_rejected(self):
        missing = self.client.post("/analyze-image", data={}, content_type="multipart/form-data")
        self.assertEqual(missing.status_code, 400)

        invalid = self.client.post(
            "/analyze-image", data={"image": (io.BytesIO(b"not image"), "leaf.jpg", "image/jpeg")},
            content_type="multipart/form-data",
        )
        self.assertEqual(invalid.status_code, 415)

        oversized = self.client.post(
            "/analyze-image",
            data={"image": (io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"x" * api.MAX_IMAGE_BYTES), "large.png", "image/png")},
            content_type="multipart/form-data",
        )
        self.assertEqual(oversized.status_code, 413)

    def test_success_returns_structured_diagnosis_and_forwards_question_and_language(self):
        response, provider = self.post_image_with_provider(self.payload(), "Why are the lower leaves spotted?", "hi")
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["status"], "image_analysis")
        self.assertEqual(body["diagnosis"]["crop"], "Tomato")
        self.assertTrue(body["diagnosis"]["success"])
        prompt = provider.call_args.kwargs["json"]["messages"][0]["content"][0]["text"]
        self.assertIn("Hindi", prompt)
        self.assertIn("Why are the lower leaves spotted?", prompt)

    def test_insufficient_visual_evidence_returns_uncertain_diagnosis(self):
        uncertain = self.payload(
            crop=None, suspected_disease=None, severity=None, confidence_status="uncertain",
            visible_symptoms=["Image is too blurry to assess leaf markings"],
            additional_information_needed=["Send a sharper close-up of both sides of the leaf"],
        )
        response, _ = self.post_image_with_provider(uncertain)
        self.assertEqual(response.status_code, 200)
        diagnosis = response.get_json()["diagnosis"]
        self.assertTrue(diagnosis["success"])
        self.assertEqual(diagnosis["confidence_status"], "uncertain")
        self.assertIsNone(diagnosis["suspected_disease"])

    def test_provider_failure_is_not_a_successful_diagnosis(self):
        with patch("modules.image_analyzer.GROQ_API_KEY", "unit-test-key"), \
                patch("modules.image_analyzer.requests.post", return_value=self.mock_provider({}, status_code=503)):
            response = self.client.post(
                "/analyze-image",
                data={"image": (io.BytesIO(self.png), "leaf.png", "image/png")},
                content_type="multipart/form-data",
            )
        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.get_json()["status"], "error")
        self.assertNotIn("diagnosis", response.get_json())

    def test_missing_provider_configuration_returns_service_unavailable(self):
        with patch("modules.image_analyzer.GROQ_API_KEY", ""):
            response = self.client.post(
                "/analyze-image",
                data={"image": (io.BytesIO(self.png), "leaf.png", "image/png")},
                content_type="multipart/form-data",
            )
        self.assertEqual(response.status_code, 503)

        original_limit = api.app.config["MAX_CONTENT_LENGTH"]
        try:
            api.app.config["MAX_CONTENT_LENGTH"] = 64
            response = self.client.post(
                "/chat", data='{"message":"' + ("x" * 200) + '"}',
                content_type="application/json",
            )
        finally:
            api.app.config["MAX_CONTENT_LENGTH"] = original_limit
        self.assertEqual(response.status_code, 413)


if __name__ == "__main__":
    unittest.main()
