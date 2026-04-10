"""
KrishiBot - Pest & Disease Advisory Module
Identifies pests/diseases and provides treatment recommendations.
Designed to support image-based detection in the future.
"""

# ──────────────────────────────────────────────
# Pest Knowledge Base
# ──────────────────────────────────────────────
PEST_DATABASE = {
    "aphid": {
        "name": "Aphids",
        "harmful": True,
        "crops_affected": ["Wheat", "Mustard", "Vegetables", "Cotton"],
        "symptoms": "Small green/yellow insects clustering on leaves, sticky honeydew residue, curled/yellowing leaves",
        "damage": "Suck sap from plants, transmit viruses, reduce yield",
        "organic_remedies": [
            "Spray neem oil solution (5ml/litre water) every 7 days",
            "Introduce ladybugs — natural aphid predators",
            "Spray diluted soap solution (dish soap + water)",
            "Plant marigolds nearby as a repellent"
        ],
        "chemical_remedies": [
            "Imidacloprid 17.8 SL @ 0.5ml/litre",
            "Dimethoate 30 EC @ 1.5ml/litre"
        ],
        "prevention": "Avoid excess nitrogen fertilizer; use reflective mulch to deter aphids"
    },
    "bollworm": {
        "name": "Bollworm",
        "harmful": True,
        "crops_affected": ["Cotton", "Tomato", "Chickpea"],
        "symptoms": "Holes in bolls/fruits, frass (droppings) near entry holes, premature boll drop",
        "damage": "Destroys cotton bolls and tomato fruits directly",
        "organic_remedies": [
            "Apply neem-based pesticide (NSKE 5%)",
            "Set up pheromone traps @ 5 per acre",
            "Spray Bt (Bacillus thuringiensis) @ 1.5g/litre",
            "Manually remove and destroy affected bolls"
        ],
        "chemical_remedies": [
            "Emamectin benzoate 5 SG @ 0.4g/litre",
            "Spinosad 45 SC @ 0.3ml/litre"
        ],
        "prevention": "Rotate crops yearly; sow early to avoid peak infestation period"
    },
    "whitefly": {
        "name": "Whitefly",
        "harmful": True,
        "crops_affected": ["Cotton", "Tomato", "Chilli", "Brinjal"],
        "symptoms": "Tiny white insects flying when plant is disturbed, yellowing leaves, sticky leaves",
        "damage": "Transmits viruses (especially viral diseases in cotton/tomato)",
        "organic_remedies": [
            "Spray neem oil @ 5ml/litre water",
            "Use yellow sticky traps in field",
            "Spray garlic extract solution"
        ],
        "chemical_remedies": [
            "Thiamethoxam 25 WG @ 0.2g/litre",
            "Spiromesifen 22.9 SC @ 1ml/litre"
        ],
        "prevention": "Avoid consecutive cotton/tomato planting; use virus-resistant varieties"
    },
    "stem borer": {
        "name": "Stem Borer",
        "harmful": True,
        "crops_affected": ["Rice", "Maize", "Sugarcane", "Jowar"],
        "symptoms": "Dead heart in young plants, white ear (in rice), holes in stem with frass",
        "damage": "Bores into stems, kills growing points, severely reduces yield",
        "organic_remedies": [
            "Release Trichogramma egg parasitoids @ 1.5 lakh/acre",
            "Apply neem cake @ 100 kg/acre in soil",
            "Use pheromone traps for monitoring"
        ],
        "chemical_remedies": [
            "Cartap hydrochloride 4G @ 10kg/acre (granule into soil)",
            "Chlorpyrifos 20 EC @ 2.5ml/litre"
        ],
        "prevention": "Remove crop stubble after harvest; avoid late sowing"
    },
    "fungal blight": {
        "name": "Fungal Blight (Late Blight)",
        "harmful": True,
        "crops_affected": ["Potato", "Tomato", "Rice", "Wheat"],
        "symptoms": "Water-soaked lesions on leaves, white mold on undersides, rapid leaf death, brown lesions",
        "damage": "Can destroy entire crops within days in humid conditions",
        "organic_remedies": [
            "Spray Trichoderma viride solution @ 2g/litre",
            "Apply copper oxychloride (2.5g/litre) — contact fungicide",
            "Improve drainage and air circulation",
            "Remove infected plant material immediately"
        ],
        "chemical_remedies": [
            "Mancozeb 75 WP @ 2.5g/litre",
            "Metalaxyl + Mancozeb @ 2.5g/litre",
            "Propiconazole 25 EC @ 1ml/litre"
        ],
        "prevention": "Use resistant varieties; avoid overhead irrigation; crop rotation"
    },
    "locust": {
        "name": "Locust",
        "harmful": True,
        "crops_affected": ["All field crops"],
        "symptoms": "Sudden mass defoliation, crop stripped bare, large swarms visible",
        "damage": "Can destroy entire fields within hours",
        "organic_remedies": [
            "Use Bio-pesticide: Metarhizium anisopliae (Green Muscle) spray",
            "Dig trenches around field boundary",
            "Light traps at night"
        ],
        "chemical_remedies": [
            "Malathion 5% dust @ 25kg/ha (emergency use)",
            "Chlorpyrifos 20 EC spray (government program)",
            "⚠️ Report to district agriculture office immediately"
        ],
        "prevention": "Follow government locust alerts; join early warning systems"
    },
    "yellow leaves": {
        "name": "Yellowing Leaves (Chlorosis)",
        "harmful": True,
        "crops_affected": ["Most crops"],
        "symptoms": "Leaves turning yellow, pale green, or bleached",
        "damage": "Indicates nutrient deficiency, overwatering, or disease",
        "organic_remedies": [
            "Check soil nitrogen: Apply vermicompost or FYM (farmyard manure)",
            "If iron deficient: Spray ferrous sulfate 0.5% solution",
            "Ensure proper drainage — yellowing can be from waterlogging",
            "Check soil pH: optimal is 6.0–7.5 for most crops"
        ],
        "chemical_remedies": [
            "Urea spray (1–2%) for nitrogen deficiency",
            "Zinc sulfate 0.5% spray for zinc deficiency",
            "Ferrous sulfate 0.5% for iron chlorosis"
        ],
        "prevention": "Regular soil testing; balanced fertilizer application; proper irrigation"
    },
    "mealybug": {
        "name": "Mealybug",
        "harmful": True,
        "crops_affected": ["Cotton", "Sugarcane", "Grapes", "Papaya"],
        "symptoms": "White cottony mass on stems/leaves, sticky honeydew, sooty mold",
        "damage": "Suck sap, weaken plants, transmit diseases",
        "organic_remedies": [
            "Spray neem oil (3ml/litre) + soap (1ml/litre)",
            "Release Cryptolaemus beetles (natural predator)",
            "Spray 2% neem seed kernel extract (NSKE)"
        ],
        "chemical_remedies": [
            "Profenofos 50 EC @ 2ml/litre",
            "Buprofezin 25 SC @ 1.5ml/litre"
        ],
        "prevention": "Avoid ant activity near plants (ants protect mealybugs); use clean planting material"
    }
}

EARTHWORM_INFO = {
    "name": "Earthworm",
    "harmful": False,
    "message": "🪱 Earthworms are **beneficial** to your soil! They:\n• Improve soil aeration and structure\n• Break down organic matter into nutrients\n• Increase water retention\n\nMore earthworms = healthier soil. Encourage them by adding compost and avoiding harsh chemical pesticides."
}


def get_pest_advice(message: str) -> dict:
    """
    Identify pest/disease from message and return advice.
    """
    msg_lower = message.lower()

    # Check for beneficial organisms first
    if "earthworm" in msg_lower or "earth worm" in msg_lower:
        return {
            "message": EARTHWORM_INFO["message"],
            "harmful": False,
            "status": "success"
        }

    # Try to match pest in knowledge base
    matched_pest = None
    for key, data in PEST_DATABASE.items():
        if key in msg_lower or key.replace(" ", "") in msg_lower:
            matched_pest = data
            break
        # Also check by symptoms
        if any(symptom_word in msg_lower for symptom_word in key.split()):
            matched_pest = data
            break

    # Special keyword mapping
    if not matched_pest:
        keyword_map = {
            "yellow": PEST_DATABASE["yellow leaves"],
            "blight": PEST_DATABASE["fungal blight"],
            "white fly": PEST_DATABASE["whitefly"],
            "boll": PEST_DATABASE["bollworm"],
            "boring": PEST_DATABASE["stem borer"],
            "bore": PEST_DATABASE["stem borer"],
            "locust": PEST_DATABASE["locust"],
            "mealy": PEST_DATABASE["mealybug"],
        }
        for kw, pest in keyword_map.items():
            if kw in msg_lower:
                matched_pest = pest
                break

    if matched_pest:
        return _format_pest_response(matched_pest)

    # Generic farming advice for unrecognized pests
    return {
        "message": (
            "🔍 I need more details to identify the exact pest or disease.\n\n"
            "**Please describe:**\n"
            "• What symptoms do you see? (yellowing, holes, spots, wilting)\n"
            "• Which crop is affected?\n"
            "• What insects do you see? (color, size)\n\n"
            "**Common issues I can help with:**\n"
            "• Aphids, Bollworm, Whitefly, Stem Borer\n"
            "• Fungal Blight, Yellow Leaves, Mealybug\n"
            "• Locust attack\n\n"
            "💡 _Example: 'White insects on my cotton leaves' or 'Yellow spots on rice'_"
        ),
        "status": "needs_info"
    }


def _format_pest_response(pest: dict) -> dict:
    name = pest["name"]
    harmful = pest["harmful"]
    crops = ", ".join(pest.get("crops_affected", []))
    symptoms = pest.get("symptoms", "")
    damage = pest.get("damage", "")
    organic = pest.get("organic_remedies", [])
    chemical = pest.get("chemical_remedies", [])
    prevention = pest.get("prevention", "")

    severity_icon = "⚠️" if harmful else "✅"
    lines = [
        f"{severity_icon} **Identified: {name}**",
        f"🌾 Crops affected: {crops}",
        f"👁️ Symptoms: {symptoms}",
        f"💥 Damage: {damage}\n",
        "🌿 **Organic Remedies (Recommended First):**"
    ]
    for r in organic:
        lines.append(f"  • {r}")

    lines.append("\n⚗️ **Chemical Options (Last Resort):**")
    for r in chemical:
        lines.append(f"  • {r}")

    if prevention:
        lines.append(f"\n🛡️ **Prevention:** {prevention}")

    lines.append("\n⚠️ _Always wear protective gear when applying pesticides. Follow label instructions._")

    return {
        "message": "\n".join(lines),
        "pest_name": name,
        "harmful": harmful,
        "remedies": organic + chemical,
        "status": "success"
    }


# ──────────────────────────────────────────────
# Future: Image-Based Detection Hook
# ──────────────────────────────────────────────
def detect_disease_from_image(image_bytes: bytes, crop_type: str) -> dict:
    """
    Future: Integrate a CNN model (e.g., PlantVillage dataset trained ResNet)
    or call an external API like Plant.id for disease detection from images.
    """
    raise NotImplementedError("Image-based disease detection not yet integrated")
