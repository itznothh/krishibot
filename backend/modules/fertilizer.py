"""
KrishiBot - Fertilizer Recommendation Module
"""
import os
import requests

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

FERTILIZER_DATA = {
    "rice": {
        "npk": "N:120 | P:60 | K:60 kg/hectare",
        "chemical": [
            {"name": "Urea", "amount": "2.6 bags/acre", "when": "Split: 50% basal, 25% tillering, 25% panicle"},
            {"name": "DAP", "amount": "1.3 bags/acre", "when": "Basal application"},
            {"name": "MOP", "amount": "1 bag/acre", "when": "Basal application"}
        ],
        "organic": [
            {"name": "FYM (Farm Yard Manure)", "amount": "5 tonnes/acre", "when": "2-3 weeks before transplanting"},
            {"name": "Green Manure (Dhaincha)", "amount": "Plough in at flowering", "when": "Before transplanting"},
            {"name": "Azolla", "amount": "500 kg/acre", "when": "10-15 days after transplanting"}
        ],
        "tip": "Apply zinc sulfate 25kg/ha if zinc deficiency is seen (yellowing between leaf veins)."
    },
    "wheat": {
        "npk": "N:120 | P:60 | K:40 kg/hectare",
        "chemical": [
            {"name": "Urea", "amount": "2.6 bags/acre", "when": "50% basal + 50% at first irrigation (CRI stage)"},
            {"name": "DAP", "amount": "1.3 bags/acre", "when": "Basal application"},
            {"name": "MOP", "amount": "0.7 bags/acre", "when": "Basal application"}
        ],
        "organic": [
            {"name": "FYM", "amount": "4-5 tonnes/acre", "when": "3-4 weeks before sowing"},
            {"name": "Vermicompost", "amount": "2 tonnes/acre", "when": "At sowing"},
            {"name": "Bio-fertilizer (Azotobacter)", "amount": "Seed treatment", "when": "Before sowing"}
        ],
        "tip": "Apply sulfur 20kg/ha for better protein content in grain."
    },
    "cotton": {
        "npk": "N:80 | P:40 | K:40 kg/hectare",
        "chemical": [
            {"name": "Urea", "amount": "1.75 bags/acre", "when": "30 days, 60 days, 90 days after sowing (3 splits)"},
            {"name": "DAP", "amount": "1 bag/acre", "when": "Basal"},
            {"name": "MOP", "amount": "0.7 bag/acre", "when": "Basal"}
        ],
        "organic": [
            {"name": "FYM", "amount": "5 tonnes/acre", "when": "2 weeks before sowing"},
            {"name": "Neem Cake", "amount": "100 kg/acre", "when": "Mix in soil at sowing"},
            {"name": "Jeevamrit", "amount": "200 liters/acre", "when": "After each irrigation"}
        ],
        "tip": "Boron spray (0.1%) at flowering improves boll setting in cotton."
    },
    "maize": {
        "npk": "N:120 | P:60 | K:40 kg/hectare",
        "chemical": [
            {"name": "Urea", "amount": "2.6 bags/acre", "when": "1/3 basal, 1/3 at knee height, 1/3 at tasseling"},
            {"name": "DAP", "amount": "1.3 bags/acre", "when": "Basal"},
            {"name": "MOP", "amount": "0.7 bags/acre", "when": "Basal"}
        ],
        "organic": [
            {"name": "FYM", "amount": "4 tonnes/acre", "when": "Before sowing"},
            {"name": "Vermicompost", "amount": "1.5 tonnes/acre", "when": "At sowing"},
            {"name": "PSB (Phosphate Solubilizing Bacteria)", "amount": "Seed treatment", "when": "Before sowing"}
        ],
        "tip": "Zinc deficiency is common in maize — apply zinc sulfate 25kg/ha if needed."
    },
    "tomato": {
        "npk": "N:120 | P:80 | K:80 kg/hectare",
        "chemical": [
            {"name": "Urea", "amount": "2.6 bags/acre", "when": "Split in 3-4 doses during crop growth"},
            {"name": "DAP", "amount": "1.7 bags/acre", "when": "Basal"},
            {"name": "MOP", "amount": "1.3 bags/acre", "when": "Basal + at fruit development"}
        ],
        "organic": [
            {"name": "FYM/Compost", "amount": "6 tonnes/acre", "when": "Before transplanting"},
            {"name": "Vermicompost", "amount": "2 tonnes/acre", "when": "At transplanting"},
            {"name": "Calcium spray", "amount": "0.5% solution", "when": "At fruiting to prevent blossom end rot"}
        ],
        "tip": "Calcium and boron are critical for tomato fruit quality — don't skip micronutrients."
    },
    "groundnut": {
        "npk": "N:20 | P:40 | K:40 kg/hectare",
        "chemical": [
            {"name": "DAP", "amount": "0.9 bags/acre", "when": "Basal application"},
            {"name": "MOP", "amount": "0.7 bags/acre", "when": "Basal application"},
            {"name": "Gypsum", "amount": "100 kg/acre", "when": "At pegging stage — critical for pod development"}
        ],
        "organic": [
            {"name": "FYM", "amount": "4 tonnes/acre", "when": "Before sowing"},
            {"name": "Rhizobium inoculant", "amount": "Seed treatment", "when": "Before sowing — fixes nitrogen naturally"},
            {"name": "Neem Cake", "amount": "100 kg/acre", "when": "At sowing"}
        ],
        "tip": "Groundnut fixes its own nitrogen — avoid heavy urea. Gypsum is essential for good pod filling."
    },
    "sugarcane": {
        "npk": "N:250 | P:80 | K:100 kg/hectare",
        "chemical": [
            {"name": "Urea", "amount": "5.4 bags/acre", "when": "Split in 4 doses over the season"},
            {"name": "DAP", "amount": "1.7 bags/acre", "when": "Basal"},
            {"name": "MOP", "amount": "1.7 bags/acre", "when": "Basal + 3 months"}
        ],
        "organic": [
            {"name": "Pressmud", "amount": "5 tonnes/acre", "when": "Before planting"},
            {"name": "FYM", "amount": "8 tonnes/acre", "when": "Before planting"},
            {"name": "Trash mulching", "amount": "Cover field with dry leaves", "when": "After 3rd month — conserves moisture"}
        ],
        "tip": "Sugarcane responds well to ratoon management — proper fertilization in ratoon crop improves yield significantly."
    }
}

def _translate_via_groq(english_text: str, language: str) -> str:
    if not GROQ_API_KEY or language == "en":
        return english_text
    lang_name = "Hindi" if language == "hi" else "Kannada"
    enforcement = {
        "hi": "अंतिम निर्देश: पूरा उत्तर केवल हिंदी में दें।",
        "kn": "ಅಂತಿಮ ಸೂಚನೆ: ಸಂಪೂರ್ಣ ಉತ್ತರ ಕನ್ನಡದಲ್ಲಿ ನೀಡಿ.",
    }.get(language, "")
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": f"You are a farming expert. Translate the following fertilizer advice accurately to {lang_name}. Keep chemical names, quantities, and measurements as-is. {enforcement}"},
                    {"role": "user", "content": english_text}
                ],
                "max_tokens": 800,
                "temperature": 0.3
            },
            timeout=20
        )
        data = response.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
    except Exception:
        pass
    return english_text

def get_fertilizer_advice(message: str, language: str = "en") -> str:
    msg_lower = message.lower()

    for crop, data in FERTILIZER_DATA.items():
        if crop in msg_lower:
            chemical_list = "\n".join([
                f"  • **{f['name']}** — {f['amount']}\n    _{f['when']}_"
                for f in data["chemical"]
            ])
            organic_list = "\n".join([
                f"  • **{f['name']}** — {f['amount']}\n    _{f['when']}_"
                for f in data["organic"]
            ])
            english_response = (
                f"🧪 **Fertilizer Guide for {crop.capitalize()}**\n\n"
                f"📊 **Required NPK:** {data['npk']}\n\n"
                f"⚗️ **Chemical Fertilizers:**\n{chemical_list}\n\n"
                f"🌿 **Organic Options (Eco-friendly):**\n{organic_list}\n\n"
                f"💡 **Pro Tip:** {data['tip']}\n\n"
                f"📞 For soil testing: Contact your nearest Krishi Vigyan Kendra (KVK)"
            )
            return _translate_via_groq(english_response, language)

    english_response = (
        f"🧪 I can suggest fertilizers for these crops:\n\n"
        f"Rice 🌾 | Wheat 🌾 | Cotton 🌿 | Maize 🌽 | Tomato 🍅 | Groundnut | Sugarcane\n\n"
        f"Please tell me your **crop name** and I'll give you complete fertilizer guidance!\n\n"
        f"Example: *'fertilizer for wheat'* or *'ganhu ke liye khad'*"
    )
    return _translate_via_groq(english_response, language)
