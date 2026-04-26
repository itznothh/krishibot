import os
import requests

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

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
    if not GROQ_API_KEY:
        return "⚠️ Image analysis not configured. Please set GROQ_API_KEY."
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": VISION_PROMPT
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 800,
                "temperature": 0.3
            },
            timeout=30
        )
        data = response.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            error = data.get("error", {}).get("message", str(data))
            return f"⚠️ Analysis failed: {error}"
    except requests.exceptions.Timeout:
        return "⏳ Analysis timed out. Please try again."
    except Exception as e:
        return f"❌ Could not analyze image: {str(e)}"