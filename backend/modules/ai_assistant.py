import os
import requests

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

SYSTEM_PROMPT = """You are KrishiBot, an expert farming assistant for Indian farmers.
Answer ANY farming related question clearly and practically.
- Crop cultivation, soil health, pest control, fertilizers
- Weather based farming advice
- Government schemes, market prices
- Organic farming, irrigation
- Animal husbandry, dairy farming
- Any other farming topic

Rules:
- Answer in the SAME language the farmer uses (Hindi, Kannada, English)
- Keep answers practical and simple
- Use bullet points for steps
- Give specific quantities and measurements
- Be encouraging and supportive
- If asked in Hindi, reply in Hindi. If Kannada, reply in Kannada.
- Never say you cannot answer a farming question
- For non-farming questions, politely redirect to farming topics"""

def get_ai_response(message: str, context: dict) -> str:
    if not GROQ_API_KEY:
        return "⚠️ AI assistant not configured. Please set GROQ_API_KEY."
    return _call_groq_api(message, context)

def _call_groq_api(message: str, context: dict) -> str:
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add conversation history for context
        if context.get("history"):
            for entry in context["history"][-6:]:
                messages.append({
                    "role": entry["role"],
                    "content": entry["content"]
                })
        
        messages.append({"role": "user", "content": message})

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-8b-8192",
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7
            },
            timeout=15
        )
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Sorry, could not process your question. Please try again. Error: {str(e)}"