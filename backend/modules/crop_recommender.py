"""
KrishiBot - Crop Recommendation Module
Rule-based crop recommendation based on soil type and season.
"""

CROP_DATA = {
    "black": {
        "kharif": ["Cotton 🌿", "Soybean", "Jowar", "Bajra", "Tur (Pigeon Pea)"],
        "rabi": ["Wheat", "Chickpea (Chana)", "Linseed", "Safflower"],
        "zaid": ["Watermelon", "Muskmelon", "Cucumber", "Moong Dal"]
    },
    "loamy": {
        "kharif": ["Rice", "Maize", "Groundnut", "Sugarcane", "Cotton"],
        "rabi": ["Wheat", "Mustard", "Peas", "Lentil (Masoor)", "Barley"],
        "zaid": ["Vegetables", "Sunflower", "Moong", "Watermelon"]
    },
    "sandy": {
        "kharif": ["Bajra", "Groundnut", "Sesame (Til)", "Moth Bean", "Cluster Bean"],
        "rabi": ["Mustard", "Barley", "Chickpea", "Wheat (with irrigation)"],
        "zaid": ["Watermelon", "Cucumber", "Moong Dal"]
    },
    "clay": {
        "kharif": ["Rice", "Jute", "Sugarcane", "Maize"],
        "rabi": ["Wheat", "Mustard", "Chickpea", "Berseem"],
        "zaid": ["Vegetables", "Moong", "Urad"]
    },
    "red": {
        "kharif": ["Groundnut", "Maize", "Rice", "Ragi", "Bajra"],
        "rabi": ["Wheat", "Chickpea", "Mustard", "Lentil"],
        "zaid": ["Moong", "Watermelon", "Vegetables"]
    }
}

SEASON_KEYWORDS = {
    "kharif": ["kharif", "monsoon", "june", "july", "august", "september", "rainy"],
    "rabi": ["rabi", "winter", "october", "november", "december", "january", "february"],
    "zaid": ["zaid", "summer", "march", "april", "may", "zaid", "grishma"]
}

SOIL_KEYWORDS = {
    "black": ["black", "cotton soil", "regur", "काली मिट्टी"],
    "loamy": ["loamy", "loam", "दोमट"],
    "sandy": ["sandy", "sand", "बलुई"],
    "clay": ["clay", "clayey", "चिकनी मिट्टी"],
    "red": ["red", "laterite", "लाल मिट्टी"]
}

def recommend_crops(message: str, context: dict) -> str:
    msg_lower = message.lower()
    
    detected_soil = None
    detected_season = None

    for soil, keywords in SOIL_KEYWORDS.items():
        if any(k in msg_lower for k in keywords):
            detected_soil = soil
            break

    for season, keywords in SEASON_KEYWORDS.items():
        if any(k in msg_lower for k in keywords):
            detected_season = season
            break

    # Check context for previously mentioned soil/season
    if not detected_soil and context.get("soil"):
        detected_soil = context.get("soil")
    if not detected_season and context.get("season"):
        detected_season = context.get("season")

    if detected_soil and detected_season:
        crops = CROP_DATA.get(detected_soil, {}).get(detected_season, [])
        if crops:
            crop_list = "\n".join([f"  • {crop}" for crop in crops])
            return (
                f"🌾 **Recommended Crops for {detected_soil.capitalize()} Soil — {detected_season.capitalize()} Season:**\n\n"
                f"{crop_list}\n\n"
                f"💡 **Tips:**\n"
                f"  • Use certified seeds for better yield\n"
                f"  • Do a soil test before sowing\n"
                f"  • Follow local KVK (Krishi Vigyan Kendra) recommendations\n\n"
                f"📞 Kisan Call Center: **1800-180-1551** (Free, 24x7)"
            )

    elif detected_soil:
        return (
            f"You have **{detected_soil} soil** — {_soil_description(detected_soil)}\n\n"
            f"Which season are you planning for?"
            f"  • **Kharif** – June to November (monsoon)\n"
            f"  • **Rabi** – October to March (winter)\n"
            f"  • **Zaid** – March to June (summer)"
        )

    elif detected_season:
        return (
            f"For **{detected_season.capitalize()} season**, what is your soil type?\n\n"
            f"  • **Black soil** – good for cotton\n"
            f"  • **Loamy soil** – good for wheat, rice\n"
            f"  • **Sandy soil** – good for bajra, groundnut\n"
            f"  • **Clay soil** – good for rice, sugarcane\n"
            f"  • **Red soil** – good for groundnut, ragi"
        )

    else:
        return (
            f"🌱 I can suggest the best crops for your farm!\n\n"
            f"Please tell me:\n"
            f"1. **Soil type** — black, loamy, sandy, clay, or red?\n"
            f"2. **Season** — Kharif (monsoon), Rabi (winter), or Zaid (summer)?\n\n"
            f"Example: *'I have black soil, kharif season'*"
        )

def _soil_description(soil: str) -> str:
    descriptions = {
        "black": "High clay content, retains moisture well — great for cotton 🌍",
        "loamy": "Best soil type, well-drained and fertile — good for most crops 🌟",
        "sandy": "Well-drained but low nutrients — best for drought-resistant crops 🏜️",
        "clay": "Heavy soil, retains water — good for rice and sugarcane 💧",
        "red": "Low in nitrogen, good drainage — good for groundnut and millets 🔴"
    }
    return descriptions.get(soil, "suitable for many crops")
