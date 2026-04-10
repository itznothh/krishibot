"""
KrishiBot - Fertilizer Recommendation Module
Recommends fertilizers based on crop type and soil conditions.
Covers both chemical (NPK) and organic options.
"""

# ──────────────────────────────────────────────
# Fertilizer Knowledge Base
# ──────────────────────────────────────────────
FERTILIZER_DATABASE = {
    "rice": {
        "npk": {"N": 120, "P": 60, "K": 60},
        "chemical": [
            {"name": "Urea (46% N)", "dose": "2.6 bags/acre", "timing": "Split: 50% at sowing, 25% at tillering, 25% at panicle initiation"},
            {"name": "DAP (18-46-0)", "dose": "1.5 bags/acre", "timing": "At sowing/transplanting"},
            {"name": "MOP (0-0-60)", "dose": "1 bag/acre", "timing": "Basal application"}
        ],
        "organic": [
            {"name": "FYM (Farmyard Manure)", "dose": "5–8 tonnes/acre", "timing": "2–3 weeks before transplanting"},
            {"name": "Green Manure (Dhaincha)", "dose": "Grow and incorporate before rice", "timing": "45 days before transplanting"},
            {"name": "Azolla (biofertilizer)", "dose": "500 kg/acre", "timing": "Apply in field 7 days after transplanting"},
        ],
        "tip": "Split urea application significantly improves nitrogen use efficiency in paddy."
    },
    "wheat": {
        "npk": {"N": 120, "P": 60, "K": 40},
        "chemical": [
            {"name": "Urea (46% N)", "dose": "2.6 bags/acre", "timing": "50% basal, 50% at first irrigation (CRI stage)"},
            {"name": "SSP (0-16-0)", "dose": "3 bags/acre", "timing": "Basal application"},
            {"name": "MOP (0-0-60)", "dose": "0.7 bag/acre", "timing": "Basal"}
        ],
        "organic": [
            {"name": "Vermicompost", "dose": "2–3 tonnes/acre", "timing": "Before sowing"},
            {"name": "FYM", "dose": "4–5 tonnes/acre", "timing": "3–4 weeks before sowing"},
        ],
        "tip": "Use zinc sulfate (25 kg/ha) if soil is zinc-deficient — very common in wheat-growing areas."
    },
    "cotton": {
        "npk": {"N": 80, "P": 40, "K": 40},
        "chemical": [
            {"name": "Urea", "dose": "1.75 bags/acre", "timing": "30 days, 60 days, 90 days after sowing (3 splits)"},
            {"name": "DAP", "dose": "1 bag/acre", "timing": "Basal"},
            {"name": "MOP", "dose": "0.7 bag/acre", "timing": "Basal"}
        ],
        "organic": [
            {"name": "FYM", "dose": "5 tonnes/acre", "timing": "2 weeks before sowing"},
            {"name": "Neem Cake", "dose": "100 kg/acre", "timing": "Mix in soil at sowing"},
        ],
        "tip": "Boron spray (0.1%) at flowering improves boll setting in cotton."
    },
    "maize": {
        "npk": {"N": 120, "P": 60, "K": 40},
        "chemical": [
            {"name": "Urea", "dose": "2.6 bags/acre", "timing": "1/3 basal, 1/3 knee-high, 1/3 tasseling"},
            {"name": "DAP", "dose": "1.5 bags/acre", "timing": "Basal"},
            {"name": "MOP", "dose": "0.7 bag/acre", "timing": "Basal"}
        ],
        "organic": [
            {"name": "Poultry Manure", "dose": "2 tonnes/acre", "timing": "Before sowing"},
            {"name": "FYM", "dose": "4 tonnes/acre", "timing": "2–3 weeks before sowing"}
        ],
        "tip": "Zinc deficiency is common in maize. Apply zinc sulfate 25 kg/ha."
    },
    "tomato": {
        "npk": {"N": 100, "P": 60, "K": 80},
        "chemical": [
            {"name": "Urea", "dose": "2.2 bags/acre", "timing": "Split into 4–5 applications"},
            {"name": "DAP", "dose": "1.5 bags/acre", "timing": "Basal"},
            {"name": "MOP", "dose": "1.3 bags/acre", "timing": "Split: basal + fruit set"}
        ],
        "organic": [
            {"name": "Vermicompost", "dose": "1.5 tonnes/acre", "timing": "Before transplanting"},
            {"name": "Compost Tea", "dose": "Spray every 15 days", "timing": "During growth"},
            {"name": "Bone Meal", "dose": "100 kg/acre", "timing": "Basal — improves root and fruit development"}
        ],
        "tip": "Calcium spray (calcium nitrate 1%) prevents blossom end rot in tomatoes."
    },
    "sugarcane": {
        "npk": {"N": 250, "P": 115, "K": 115},
        "chemical": [
            {"name": "Urea", "dose": "5.5 bags/acre", "timing": "Split into 3: at planting, 90 days, 180 days"},
            {"name": "DAP", "dose": "2.5 bags/acre", "timing": "At planting"},
            {"name": "MOP", "dose": "2 bags/acre", "timing": "Split: planting + 90 days"}
        ],
        "organic": [
            {"name": "Pressmud (sugarcane byproduct)", "dose": "5 tonnes/acre", "timing": "Before planting"},
            {"name": "FYM", "dose": "8 tonnes/acre", "timing": "1 month before planting"},
        ],
        "tip": "Sugarcane is a heavy feeder. Never skip potassium — it improves sucrose content."
    },
    "groundnut": {
        "npk": {"N": 25, "P": 50, "K": 75},
        "chemical": [
            {"name": "DAP", "dose": "1.25 bags/acre", "timing": "Basal"},
            {"name": "MOP", "dose": "1.25 bags/acre", "timing": "Basal"},
            {"name": "Gypsum", "dose": "100 kg/acre", "timing": "At pegging stage — essential for calcium"}
        ],
        "organic": [
            {"name": "Rhizobium biofertilizer", "dose": "Seed treatment before sowing", "timing": "At sowing"},
            {"name": "FYM", "dose": "3 tonnes/acre", "timing": "Before sowing"},
        ],
        "tip": "Groundnut fixes its own nitrogen (legume). Apply Rhizobium for best results."
    }
}

# Soil-based correction factors
SOIL_ADJUSTMENTS = {
    "black": "Black soils are naturally high in potassium. You may reduce K application by 25%.",
    "sandy": "Sandy soils have low water/nutrient retention. Use split fertilizer applications and prefer slow-release fertilizers.",
    "red": "Red soils are often deficient in nitrogen and phosphorus. Increase N and P doses by 20%.",
    "clayey": "Clayey soils have good nutrient holding capacity. Standard doses apply, but ensure good drainage.",
    "loamy": "Loamy soil is ideal. Standard fertilizer doses should work well for most crops."
}


def get_fertilizer_advice(message: str, context: dict) -> dict:
    """
    Parse message for crop and soil type, then return fertilizer recommendations.
    """
    msg_lower = message.lower()

    # Detect crop from message
    crop = _extract_crop(msg_lower) or context.get("crop")
    soil = _extract_soil(msg_lower) or context.get("soil")

    if crop and crop in FERTILIZER_DATABASE:
        return _build_fertilizer_response(crop, soil)
    elif crop:
        return {
            "message": (
                f"I have general guidelines for **{crop.title()}**. "
                f"For precise recommendations, a soil test is best.\n\n"
                f"Standard NPK ratio for {crop.title()}: depends on soil. "
                f"Please mention your soil type (black, red, sandy, loamy, clayey) for better advice."
            ),
            "status": "partial"
        }
    else:
        return {
            "message": (
                "🌿 I can suggest fertilizers for your crops!\n\n"
                "Which crop are you asking about?\n"
                "• Rice, Wheat, Maize, Cotton\n"
                "• Tomato, Groundnut, Sugarcane\n"
                "• (More crops available — just ask!)\n\n"
                "_Also mention your soil type for more accurate advice._\n"
                "_Example: 'Fertilizer for wheat on black soil'_"
            ),
            "status": "needs_info"
        }


def _build_fertilizer_response(crop: str, soil: str | None) -> dict:
    data = FERTILIZER_DATABASE[crop]
    npk = data["npk"]
    chemical = data["chemical"]
    organic = data["organic"]
    tip = data.get("tip", "")
    soil_note = SOIL_ADJUSTMENTS.get(soil, "") if soil else ""

    lines = [
        f"🌾 **Fertilizer Guide for {crop.title()}**\n",
        f"📊 **Required NPK:** N:{npk['N']} | P:{npk['P']} | K:{npk['K']} kg/hectare\n",
        "⚗️ **Chemical Fertilizers:**"
    ]
    for f in chemical:
        lines.append(f"  • **{f['name']}** — {f['dose']}")
        lines.append(f"    📅 _When: {f['timing']}_")

    lines.append("\n🌿 **Organic Options (Eco-friendly):**")
    for f in organic:
        lines.append(f"  • **{f['name']}** — {f['dose']}")
        lines.append(f"    📅 _When: {f['timing']}_")

    if soil_note:
        lines.append(f"\n🌍 **Soil Note ({soil.title()} soil):** {soil_note}")

    if tip:
        lines.append(f"\n💡 **Pro Tip:** {tip}")

    lines.append("\n📋 _Always do a soil test before applying fertilizers for best results._")

    return {
        "message": "\n".join(lines),
        "crop": crop,
        "npk": npk,
        "recommendations": chemical + organic,
        "status": "success"
    }


def _extract_crop(text: str) -> str | None:
    crop_keywords = {
        "rice": ["rice", "paddy", "dhaan"],
        "wheat": ["wheat", "gehun"],
        "cotton": ["cotton", "kapas"],
        "maize": ["maize", "corn", "makka"],
        "tomato": ["tomato", "tamatar"],
        "sugarcane": ["sugarcane", "ganna"],
        "groundnut": ["groundnut", "peanut", "moongfali"],
    }
    for crop, keywords in crop_keywords.items():
        if any(kw in text for kw in keywords):
            return crop
    return None


def _extract_soil(text: str) -> str | None:
    for soil in ["black", "red", "sandy", "loamy", "clayey"]:
        if soil in text:
            return soil
    return None
