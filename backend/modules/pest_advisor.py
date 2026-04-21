"""
KrishiBot - Pest and Disease Advisory Module
"""

PEST_DATABASE = {
    "aphid": {
        "name": "Aphids (Mahu/Chepwa)",
        "crops": ["wheat", "mustard", "vegetables", "cotton"],
        "symptoms": "Small soft-bodied insects, yellowing leaves, sticky honeydew",
        "harmful": True,
        "remedies": [
            "Spray neem oil (5ml/liter water)",
            "Use yellow sticky traps",
            "Spray imidacloprid 0.5ml/liter",
            "Introduce ladybird beetles (natural predator)",
            "Spray soap solution (5g soap/liter water)"
        ]
    },
    "stem borer": {
        "name": "Stem Borer (Tana Chedak)",
        "crops": ["rice", "maize", "sugarcane"],
        "symptoms": "Dead heart in young plants, white ear in mature plants, holes in stem",
        "harmful": True,
        "remedies": [
            "Use light traps to catch adult moths",
            "Apply carbofuran 3G in soil",
            "Spray chlorpyrifos 2ml/liter",
            "Remove and destroy infected plants",
            "Use Trichogramma cards for biological control"
        ]
    },
    "whitefly": {
        "name": "Whitefly (Safed Makhi)",
        "crops": ["cotton", "tomato", "chilli", "vegetables"],
        "symptoms": "Tiny white insects under leaves, yellowing, leaf curl",
        "harmful": True,
        "remedies": [
            "Spray neem oil 5ml/liter water",
            "Use yellow sticky traps",
            "Spray imidacloprid or thiamethoxam",
            "Remove heavily infected leaves",
            "Avoid excessive nitrogen fertilizer"
        ]
    },
    "leaf blight": {
        "name": "Leaf Blight (Patti Jhulsa)",
        "crops": ["rice", "wheat", "maize"],
        "symptoms": "Water-soaked lesions, yellowing edges, brown spots on leaves",
        "harmful": True,
        "remedies": [
            "Spray mancozeb 2.5g/liter water",
            "Use copper oxychloride 3g/liter",
            "Remove infected crop residues",
            "Avoid overhead irrigation",
            "Use resistant varieties next season"
        ]
    },
    "rust": {
        "name": "Rust Disease (Raila/Tikka)",
        "crops": ["wheat", "groundnut", "coffee"],
        "symptoms": "Orange/brown powder-like pustules on leaves",
        "harmful": True,
        "remedies": [
            "Spray propiconazole 1ml/liter",
            "Use mancozeb 2.5g/liter as preventive",
            "Remove infected leaves early",
            "Use rust-resistant varieties",
            "Avoid late sowing"
        ]
    },
    "powdery mildew": {
        "name": "Powdery Mildew (Choorni Rog)",
        "crops": ["wheat", "grapes", "vegetables", "peas"],
        "symptoms": "White powdery coating on leaves and stems",
        "harmful": True,
        "remedies": [
            "Spray sulfur 3g/liter water",
            "Use carbendazim 1g/liter",
            "Spray diluted milk (1:9 ratio) as organic remedy",
            "Improve air circulation in crops",
            "Avoid excess humidity"
        ]
    },
    "caterpillar": {
        "name": "Caterpillar/Worm (Sundi/Keeda)",
        "crops": ["cotton", "vegetables", "maize", "tomato"],
        "symptoms": "Irregular holes in leaves, defoliation, frass present",
        "harmful": True,
        "remedies": [
            "Spray Bt (Bacillus thuringiensis) — organic",
            "Use spinosad 0.5ml/liter",
            "Hand pick and destroy in small fields",
            "Use pheromone traps for monitoring",
            "Spray chlorpyrifos 2ml/liter for severe attack"
        ]
    },
    "thrips": {
        "name": "Thrips",
        "crops": ["onion", "chilli", "cotton", "groundnut"],
        "symptoms": "Silver streaks on leaves, curling, stunted growth",
        "harmful": True,
        "remedies": [
            "Spray spinosad 0.5ml/liter",
            "Use blue sticky traps",
            "Spray neem oil 5ml/liter",
            "Apply imidacloprid soil drench",
            "Avoid water stress in crops"
        ]
    }
}

def get_pest_advice(message: str) -> str:
    msg_lower = message.lower()

    for pest_key, pest_info in PEST_DATABASE.items():
        if pest_key in msg_lower or any(crop in msg_lower for crop in pest_info["crops"]):
            remedies_list = "\n".join([f"  {i+1}. {r}" for i, r in enumerate(pest_info["remedies"])])
            return (
                f"🐛 **{pest_info['name']}**\n\n"
                f"**Affected Crops:** {', '.join(pest_info['crops']).title()}\n"
                f"**Symptoms:** {pest_info['symptoms']}\n"
                f"**Harmful:** {'⚠️ Yes' if pest_info['harmful'] else '✅ Not harmful'}\n\n"
                f"**Remedies:**\n{remedies_list}\n\n"
                f"💡 Always follow label instructions when using pesticides.\n"
                f"📞 For severe attacks, contact your local agricultural officer."
            )

    return (
        f"🔍 I can help identify pests and diseases!\n\n"
        f"Please describe:\n"
        f"  • What crop is affected?\n"
        f"  • What symptoms do you see? (spots, holes, wilting, color change)\n"
        f"  • Which part is affected? (leaves, stem, roots, fruit)\n\n"
        f"I know about: aphids, stem borers, whitefly, leaf blight, rust, powdery mildew, caterpillars, thrips\n\n"
        f"📞 **Kisan Call Center: 1800-180-1551** (Free, 24x7)"
    )
