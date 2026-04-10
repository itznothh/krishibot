"""
KrishiBot - Crop Recommendation Module
Rule-based crop recommender (designed for easy ML upgrade).
"""

import re

# ──────────────────────────────────────────────
# Knowledge Base
# ──────────────────────────────────────────────
CROP_DATABASE = {
    # Format: (season, soil_type) -> list of crops
    ("kharif", "loamy"):   ["Rice", "Maize", "Soybean", "Cotton", "Groundnut"],
    ("kharif", "black"):   ["Cotton", "Soybean", "Jowar", "Sugarcane", "Groundnut"],
    ("kharif", "sandy"):   ["Groundnut", "Bajra", "Moong", "Sesame"],
    ("kharif", "red"):     ["Groundnut", "Cotton", "Jowar", "Ragi"],
    ("kharif", "clayey"):  ["Rice", "Jute", "Sugarcane"],
    ("rabi", "loamy"):     ["Wheat", "Mustard", "Gram", "Peas", "Lentils"],
    ("rabi", "black"):     ["Wheat", "Chickpea", "Safflower", "Gram"],
    ("rabi", "sandy"):     ["Mustard", "Gram", "Barley"],
    ("rabi", "red"):       ["Wheat", "Gram", "Linseed"],
    ("rabi", "clayey"):    ["Wheat", "Mustard", "Gram"],
    ("zaid", "loamy"):     ["Watermelon", "Muskmelon", "Cucumber", "Bitter Gourd"],
    ("zaid", "sandy"):     ["Watermelon", "Muskmelon", "Moong"],
    ("zaid", "black"):     ["Moong", "Urad", "Sesame"],
    ("zaid", "red"):       ["Moong", "Watermelon", "Vegetables"],
    ("zaid", "clayey"):    ["Vegetables", "Cucumber", "Muskmelon"],
}

CROP_DETAILS = {
    "Rice":        {"water": "High", "duration": "120-150 days", "npk": "120-60-60 kg/ha"},
    "Wheat":       {"water": "Medium", "duration": "110-130 days", "npk": "120-60-40 kg/ha"},
    "Maize":       {"water": "Medium", "duration": "90-120 days", "npk": "120-60-40 kg/ha"},
    "Cotton":      {"water": "Medium", "duration": "160-200 days", "npk": "80-40-40 kg/ha"},
    "Soybean":     {"water": "Medium", "duration": "90-110 days", "npk": "30-80-40 kg/ha"},
    "Groundnut":   {"water": "Low-Medium", "duration": "100-130 days", "npk": "25-50-75 kg/ha"},
    "Mustard":     {"water": "Low", "duration": "90-110 days", "npk": "80-40-40 kg/ha"},
    "Gram":        {"water": "Low", "duration": "90-110 days", "npk": "20-50-40 kg/ha"},
    "Sugarcane":   {"water": "Very High", "duration": "300-365 days", "npk": "250-115-115 kg/ha"},
    "Watermelon":  {"water": "Low-Medium", "duration": "70-90 days", "npk": "60-40-60 kg/ha"},
    "Jowar":       {"water": "Low", "duration": "100-120 days", "npk": "80-40-40 kg/ha"},
    "Bajra":       {"water": "Low", "duration": "80-90 days", "npk": "80-40-40 kg/ha"},
}

SEASON_MONTHS = {
    "kharif": "June – November (Monsoon season)",
    "rabi":   "October – March (Winter season)",
    "zaid":   "March – June (Summer/dry season)",
}

SOIL_DESCRIPTIONS = {
    "loamy":  "Good water retention, rich in nutrients — ideal for most crops",
    "black":  "High clay content, retains moisture well — great for cotton",
    "sandy":  "Low water retention, good drainage — suited for drought crops",
    "red":    "Well-drained, low fertility — requires more fertilizer",
    "clayey": "Heavy soil, slow drainage — good for paddy and jute",
}


def recommend_crops(message: str, context: dict) -> dict:
    """
    Parse user message for soil type and season, then recommend crops.
    Falls back to asking for details if insufficient info.
    """
    msg_lower = message.lower()

    # Extract season
    season = _extract_season(msg_lower)

    # Extract soil type
    soil = _extract_soil(msg_lower)

    # Use context from previous messages if available
    if not season:
        season = context.get("season")
    if not soil:
        soil = context.get("soil")

    # Generate recommendation
    if season and soil:
        return _build_recommendation(season, soil)
    elif season:
        return {
            "message": (
                f"I can help with {season.title()} crops! 🌱\n\n"
                "What type of soil do you have?\n"
                "• **Loamy** – soft, brown soil (most common)\n"
                "• **Black** – dark cotton soil (regur)\n"
                "• **Sandy** – light, grainy soil\n"
                "• **Red** – reddish, iron-rich soil\n"
                "• **Clayey** – heavy, sticky soil"
            ),
            "status": "needs_soil",
            "context_update": {"season": season}
        }
    elif soil:
        return {
            "message": (
                f"You have **{soil} soil** — {SOIL_DESCRIPTIONS.get(soil, '')} 🌍\n\n"
                "Which season are you planning for?\n"
                "• **Kharif** – June to November (monsoon)\n"
                "• **Rabi** – October to March (winter)\n"
                "• **Zaid** – March to June (summer)"
            ),
            "status": "needs_season",
            "context_update": {"soil": soil}
        }
    else:
        return {
            "message": (
                "I'll help you choose the best crops! 🌾\n\n"
                "Please tell me:\n"
                "1. **Season**: Kharif (monsoon), Rabi (winter), or Zaid (summer)?\n"
                "2. **Soil type**: Loamy, Black, Sandy, Red, or Clayey?\n\n"
                "_Example: \"Rabi season, loamy soil\"_"
            ),
            "status": "needs_info"
        }


def _build_recommendation(season: str, soil: str) -> dict:
    key = (season, soil)
    crops = CROP_DATABASE.get(key, [])

    if not crops:
        # Try closest match
        for k, v in CROP_DATABASE.items():
            if k[0] == season:
                crops = v
                soil = k[1]
                break

    if not crops:
        return {
            "message": f"I don't have data for {season} + {soil} combination. Please consult your local Krishi Vigyan Kendra.",
            "crops": [],
            "status": "not_found"
        }

    # Build rich response
    lines = [
        f"✅ **Best crops for {season.title()} season on {soil.title()} soil:**\n",
        f"📅 Season window: {SEASON_MONTHS.get(season, '')}",
        f"🌍 Soil: {soil.title()} — {SOIL_DESCRIPTIONS.get(soil, '')}\n",
        "**Recommended Crops:**"
    ]

    for i, crop in enumerate(crops[:5], 1):
        details = CROP_DETAILS.get(crop, {})
        water = details.get("water", "Medium")
        duration = details.get("duration", "~120 days")
        lines.append(f"{i}. **{crop}** — 💧 Water: {water} | ⏱ Duration: {duration}")

    lines.append("\n💡 _Tip: Contact your local agricultural officer for seed subsidies._")

    return {
        "message": "\n".join(lines),
        "crops": crops,
        "season": season,
        "soil": soil,
        "status": "success"
    }


def _extract_season(text: str) -> str | None:
    if any(w in text for w in ["kharif", "monsoon", "june", "july", "august"]):
        return "kharif"
    if any(w in text for w in ["rabi", "winter", "november", "december", "january"]):
        return "rabi"
    if any(w in text for w in ["zaid", "summer", "march", "april", "may"]):
        return "zaid"
    return None


def _extract_soil(text: str) -> str | None:
    if any(w in text for w in ["loamy", "loam"]):
        return "loamy"
    if any(w in text for w in ["black", "cotton soil", "regur"]):
        return "black"
    if any(w in text for w in ["sandy", "sand"]):
        return "sandy"
    if any(w in text for w in ["red soil", "red"]):
        return "red"
    if any(w in text for w in ["clayey", "clay"]):
        return "clayey"
    return None


# ──────────────────────────────────────────────
# Future ML Hook (placeholder)
# ──────────────────────────────────────────────
def recommend_crops_ml(soil: str, season: str, location: dict, rainfall: float) -> list:
    """
    Future: Replace rule-based logic with ML model.
    Could use RandomForest or a trained neural network
    trained on soil-crop-yield datasets.
    """
    raise NotImplementedError("ML model not yet integrated")
