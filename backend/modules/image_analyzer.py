import os
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

VISION_PROMPT = """You are an expert agricultural plant pathologist and crop doctor.
A farmer has shared a photo of their crop. Analyze the image carefully and provide:

1. **What you see** — describe the crop and visible symptoms
2. **Disease/Pest Identification** — name the disease, pest, or deficiency (if any)
3. **Severity** — Mild / Moderate / Severe
4. **Cause** — what causes this problem
5. **Treatment** — step-by-step remedy (include both chemical and organic options)
6. **Prevention** — how to avoid this in future

If the image is NOT a crop or plant, politely say so and ask for a crop photo.
Keep the response practical, simple, and farmer-friendly.
Use bullet points and short sentences."""

def analyze_crop_image(image_base64: str, mime_type: str = "image/jpeg") -> str:
    if not GEMINI_API_KEY:
        return "⚠️ Image analysis is not configured. Please set GEMINI_API_KEY."
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{
                "parts": [
                    {"text": VISION_PROMPT},
                    {"inline_data": {"mime_type": mime_type, "data": image_base64}}
                ]
            }],
            "generationConfig": {"maxOutputTokens": 800, "temperature": 0.3}
        }
        response = requests.post(url, json=payload, timeout=30)
        data = response.json()
        if response.status_code != 200:
            error = data.get("error", {}).get("message", "Unknown error")
            return f"⚠️ Image analysis failed: {error}"
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except requests.exceptions.Timeout:
        return "⏳ Image analysis timed out. Please try again with a smaller image."
    except Exception as e:
        return f"❌ Could not analyze image: {str(e)}"