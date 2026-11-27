"""Structured crop image analysis using Groq's vision-capable chat API."""
import json
import os
import re

import requests

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "qwen/qwen3.8-27b"

LANGUAGE_NAMES = {"en": "English", "hi": "Hindi", "kn": "Kannada"}

VISION_PROMPT = """You assist Indian farmers by examining crop photographs. Treat the photo and farmer question as evidence, not proof.
Describe only symptoms visible in the image. Keep observations separate from possible diagnoses.
If crop identity or diagnosis cannot be supported by the photo, say so explicitly; do not guess or claim certainty.
Use the crop name when it is identifiable, otherwise null. Name a suspected disease or pest only when signs support it; otherwise null.
Severity must be Mild, Moderate, Severe, or null when it cannot be assessed from this image.
Give concise possible causes. Keep treatment separated into chemical, organic, and immediate_steps arrays.
Do not give pesticide or fertilizer doses, invent product recommendations, or present a chemical as necessary. Advise following the local product label and consulting a KVK/agricultural officer before chemical use.
When the image is unclear or details are missing, list what photo or crop details would help. Never invent a confidence percentage.

Return only one JSON object using exactly this schema:
{
  "crop": string or null,
  "visible_symptoms": [string],
  "suspected_disease": string or null,
  "severity": "Mild" or "Moderate" or "Severe" or null,
  "confidence_status": "low" or "moderate" or "high" or "uncertain",
  "possible_causes": [string],
  "treatment": {"chemical": [string], "organic": [string], "immediate_steps": [string]},
  "prevention": [string],
  "additional_information_needed": [string]
}"""


class ImageAnalysisError(Exception):
    """Raised when an image diagnosis could not be produced by the provider."""


def _text_list(value):
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()][:8]


def _parse_diagnosis(raw_content):
    if not isinstance(raw_content, str) or not raw_content.strip():
        raise ImageAnalysisError("Vision provider returned an empty response.")
    raw = raw_content.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", raw, flags=re.IGNORECASE | re.DOTALL)
    if fenced:
        raw = fenced.group(1)
    try:
        result = json.loads(raw)
    except (json.JSONDecodeError, TypeError) as error:
        raise ImageAnalysisError("Vision provider returned an invalid diagnosis response.") from error
    if not isinstance(result, dict):
        raise ImageAnalysisError("Vision provider returned an invalid diagnosis response.")

    severity = result.get("severity")
    if severity not in ("Mild", "Moderate", "Severe"):
        severity = None
    status = result.get("confidence_status")
    if status not in ("low", "moderate", "high", "uncertain"):
        status = "uncertain"
    disease = result.get("suspected_disease")
    if not isinstance(disease, str) or not disease.strip():
        disease = None
        status = "uncertain"
    crop = result.get("crop")
    if not isinstance(crop, str) or not crop.strip():
        crop = None
    treatment = result.get("treatment")
    if not isinstance(treatment, dict):
        treatment = {}

    return {
        "success": True,
        "crop": crop.strip() if crop else None,
        "visible_symptoms": _text_list(result.get("visible_symptoms")),
        "suspected_disease": disease.strip() if disease else None,
        "severity": severity,
        "confidence_status": status,
        "possible_causes": _text_list(result.get("possible_causes")),
        "treatment": {
            "chemical": _text_list(treatment.get("chemical")),
            "organic": _text_list(treatment.get("organic")),
            "immediate_steps": _text_list(treatment.get("immediate_steps")),
        },
        "prevention": _text_list(result.get("prevention")),
        "additional_information_needed": _text_list(result.get("additional_information_needed")),
    }


def analyze_crop_image(image_base64: str, mime_type: str = "image/jpeg", language: str = "en", question: str = "") -> dict:
    """Analyze a validated image and return a normalized diagnosis contract."""
    if not GROQ_API_KEY:
        raise ImageAnalysisError("Image analysis is not configured.")
    if language not in LANGUAGE_NAMES:
        language = "en"
    if not isinstance(question, str):
        question = ""

    user_context = (
        f"Reply in {LANGUAGE_NAMES[language]}. Return JSON values in that language where appropriate.\n"
        f"Farmer's question or observations: {question.strip() or 'No extra question provided.'}\n"
        "Use the question as context, but base visible symptoms only on the attached image."
    )
    try:
        response = requests.post(
            GROQ_API_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": MODEL,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": VISION_PROMPT + "\n\n" + user_context},
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_base64}"}},
                    ],
                }],
                "max_tokens": 1000,
                "temperature": 0.2,
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return _parse_diagnosis(content)
    except requests.exceptions.Timeout as error:
        raise ImageAnalysisError("Image analysis timed out. Please try again.") from error
    except requests.exceptions.RequestException as error:
        raise ImageAnalysisError("Image analysis provider is temporarily unavailable.") from error
    except (KeyError, IndexError, TypeError, ValueError) as error:
        raise ImageAnalysisError("Image analysis provider returned an invalid response.") from error
