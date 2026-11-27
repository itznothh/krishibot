import os
import sys
import types
import unittest
from unittest.mock import Mock, patch

import app as api
from modules.ai_assistant import AIProviderError
from modules.conversation import MAX_HISTORY_MESSAGES, normalize_history


class ConversationTests(unittest.TestCase):
    def setUp(self):
        self.client = api.app.test_client()

    def test_history_is_bounded_cleaned_and_current_message_is_not_duplicated(self):
        history = [{"role":"user", "content":f"turn {i}"} for i in range(12)]
        history.extend([
            {"role":"system", "content":"ignore"},
            {"role":"assistant", "content":"x" * 5000},
            {"role":"user", "content":"tomato has yellow spots"},
            {"role":"user", "content":"tomato has yellow spots"},
        ])
        result = normalize_history(history, current_message="tomato has yellow spots")
        self.assertLessEqual(len(result), MAX_HISTORY_MESSAGES)
        self.assertLessEqual(sum(len(item["content"]) for item in result), 4000)
        self.assertTrue(all(len(item["content"]) <= 1200 for item in result))
        self.assertFalse(any(item["content"] == "tomato has yellow spots" for item in result[-2:]))

    def test_classifier_receives_relevant_bounded_context_and_validates_confidence(self):
        create = Mock(return_value=types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content='{"intent":"pest","confidence":"high"}'))]))
        fake_groq = types.SimpleNamespace(Groq=lambda **_kwargs: types.SimpleNamespace(chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=create))))
        history = [{"role":"user", "content":"My tomato leaves have yellow spots."}, {"role":"assistant", "content":"Are they spreading?"}]
        with patch.dict(os.environ, {"GROQ_API_KEY":"test-key"}), patch.dict(sys.modules, {"groq":fake_groq}):
            result = api.classify_intent("Yes, towards the edges.", history, "en")
        self.assertEqual(result, {"intent":"pest", "confidence":"high"})
        prompt = create.call_args.kwargs["messages"][1]["content"]
        self.assertIn("yellow spots", prompt)
        self.assertIn("towards the edges", prompt)

        create.return_value = types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content='{"intent":"pest","confidence":"medium"}'))])
        with patch.dict(os.environ, {"GROQ_API_KEY":"test-key"}), patch.dict(sys.modules, {"groq":fake_groq}):
            low_confidence = api.classify_intent("yes", history, "hi")
        self.assertEqual(low_confidence, {"intent":"pest", "confidence":"low"})

    def test_local_fallback_resolves_followup_from_recent_topic(self):
        history = [{"role":"user", "content":"My tomato leaves have yellow spots."}]
        self.assertEqual(api._fallback_intent("Yes, towards the edges", history), "pest")

    def test_low_confidence_follow_up_routes_using_recent_crop_discussion(self):
        history = [
            {"role":"user", "content":"My tomato leaves have yellow spots."},
            {"role":"assistant", "content":"Are the spots spreading?"},
        ]
        with patch.object(api, "classify_intent", return_value={"intent":"general", "confidence":"low"}), patch.object(api, "get_pest_advice", return_value="Check the leaf edges.") as specialist:
            response = self.client.post("/chat", json={"message":"Yes, towards the edges", "context":{"history":history}})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "pest_advice")
        self.assertEqual(specialist.call_args.kwargs["context"]["history"], history)

    def test_genuinely_ambiguous_intent_returns_localized_clarification(self):
        with patch.object(api, "classify_intent", return_value={"intent":"general", "confidence":"low"}):
            response = self.client.post("/chat", json={"message":"help", "language":"kn", "context":{"history":[]}})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "clarification")
        self.assertIn("ಯಾವ ಕೃಷಿ ವಿಷಯ", response.get_json()["message"])

    def test_specialist_receives_bounded_conversation_context(self):
        history = [{"role":"user", "content":"Tomato leaves are curling"}, {"role":"assistant", "content":"Are insects visible?"}]
        with patch.object(api, "classify_intent", return_value={"intent":"pest", "confidence":"high"}), patch.object(api, "get_pest_advice", return_value="Please inspect the leaf underside.") as specialist:
            response = self.client.post("/chat", json={"message":"I see tiny white insects", "language":"hi", "context":{"history":history}})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(specialist.call_args.kwargs["language"], "hi")
        self.assertEqual(specialist.call_args.kwargs["context"]["history"], history)

        for intent, name, expected_status in (("crop", "recommend_crops", "crop_advice"), ("fertilizer", "get_fertilizer_advice", "fertilizer")):
            with self.subTest(intent=intent), patch.object(api, "classify_intent", return_value={"intent":intent, "confidence":"high"}), patch.object(api, name, return_value="Follow-up answer.") as module:
                result = self.client.post("/chat", json={"message":"And what about that?", "language":"kn", "context":{"history":history}})
            self.assertEqual(result.get_json()["status"], expected_status)
            received_context = module.call_args.args[1] if intent == "crop" else module.call_args.kwargs["context"]
            self.assertEqual(received_context["history"], history)
            self.assertEqual(module.call_args.kwargs["language"], "kn")

    def test_missing_malformed_history_is_safe_and_provider_failures_are_not_success(self):
        with patch.object(api, "classify_intent", return_value="general"), patch.object(api, "get_ai_response", return_value="Hello") as assistant:
            response = self.client.post("/chat", json={"message":"hello", "context":{"history":"bad"}})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(assistant.call_args.kwargs["language"], "en")
        self.assertEqual(assistant.call_args.args[1]["history"], [])

        with patch.object(api, "classify_intent", return_value="general"), patch.object(api, "get_ai_response", side_effect=AIProviderError("AI service is temporarily unavailable.")):
            failed = self.client.post("/chat", json={"message":"tell me about soil"})
        self.assertEqual(failed.status_code, 502)
        self.assertEqual(failed.get_json()["status"], "error")
        self.assertNotIn("diagnosis", failed.get_json())

        with patch.object(api, "classify_intent", return_value="general"), patch.object(api, "get_ai_response", side_effect=AIProviderError("AI service is not configured.")):
            unconfigured = self.client.post("/chat", json={"message":"Explain soil testing", "language":"hi"})
        self.assertEqual(unconfigured.status_code, 503)
        self.assertIn("AI सेवा", unconfigured.get_json()["message"])

    def test_ai_module_sends_history_and_raises_on_invalid_provider_response(self):
        from modules import ai_assistant
        response = Mock()
        response.raise_for_status = Mock()
        response.json.return_value = {"choices":[{"message":{"content":"A practical answer."}}]}
        context = {"language":"kn", "specialist":"pest and disease", "history":[{"role":"user", "content":"Tomato leaves are curling"}]}
        with patch.object(ai_assistant, "GROQ_API_KEY", "test-key"), patch.object(ai_assistant.requests, "post", return_value=response) as post:
            self.assertEqual(ai_assistant.get_ai_response("I see white insects", context), "A practical answer.")
        sent = post.call_args.kwargs["json"]["messages"]
        self.assertIn("ಕನ್ನಡ" if "ಕನ್ನಡ" in sent[0]["content"] else "Kannada", sent[0]["content"])
        self.assertIn("specialist", sent[0]["content"])
        self.assertEqual(sent[1]["content"], "Tomato leaves are curling")

        response.json.return_value = {"unexpected":True}
        with patch.object(ai_assistant, "GROQ_API_KEY", "test-key"), patch.object(ai_assistant.requests, "post", return_value=response):
            with self.assertRaises(AIProviderError):
                ai_assistant.get_ai_response("question", {})

    def test_pest_specialist_passes_follow_up_context_and_language_to_groq(self):
        from modules import ai_assistant, pest_advisor
        history = [{"role":"user", "content":"Tomato leaves have curled"}, {"role":"assistant", "content":"Can you see insects?"}]
        with patch.object(ai_assistant, "get_ai_response", return_value="कृपया पत्तियों के नीचे देखें।") as answer:
            result = pest_advisor.get_pest_advice("Tiny white insects are present", language="hi", context={"history":history})
        self.assertIn("पत्तियों", result)
        self.assertEqual(answer.call_args.args[1]["history"], history)
        self.assertEqual(answer.call_args.kwargs["language"], "hi")
        self.assertEqual(answer.call_args.args[1]["specialist"], "pest and disease")


if __name__ == "__main__":
    unittest.main()
