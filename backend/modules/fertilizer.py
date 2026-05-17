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
    },

    # ── NEW CROPS ──────────────────────────────────────────────────────────

    "bajra": {
        "npk": "N:80 | P:40 | K:40 kg/hectare",
        "chemical": [
            {"name": "Urea", "amount": "1.75 bags/acre", "when": "50% basal + 50% at 30 days after sowing"},
            {"name": "DAP", "amount": "0.9 bags/acre", "when": "Basal application"},
            {"name": "MOP", "amount": "0.7 bags/acre", "when": "Basal application"}
        ],
        "organic": [
            {"name": "FYM", "amount": "3-4 tonnes/acre", "when": "2-3 weeks before sowing"},
            {"name": "Vermicompost", "amount": "1 tonne/acre", "when": "At sowing"},
            {"name": "Azotobacter", "amount": "Seed treatment", "when": "Before sowing"}
        ],
        "tip": "Bajra is drought tolerant — avoid excess irrigation. Iron spray (0.5% FeSO4) helps prevent chlorosis on sandy soils."
    },
    "jowar": {
        "npk": "N:80 | P:40 | K:40 kg/hectare",
        "chemical": [
            {"name": "Urea", "amount": "1.75 bags/acre", "when": "Half at sowing, half at 30 days"},
            {"name": "DAP", "amount": "0.9 bags/acre", "when": "Basal application"},
            {"name": "MOP", "amount": "0.7 bags/acre", "when": "Basal application"}
        ],
        "organic": [
            {"name": "FYM", "amount": "4 tonnes/acre", "when": "3 weeks before sowing"},
            {"name": "Compost", "amount": "2 tonnes/acre", "when": "At sowing"},
            {"name": "PSB", "amount": "Seed treatment", "when": "Before sowing"}
        ],
        "tip": "Jowar responds well to zinc — apply zinc sulfate 25kg/ha on deficient soils. Avoid waterlogging."
    },
    "soybean": {
        "npk": "N:30 | P:60 | K:40 kg/hectare",
        "chemical": [
            {"name": "DAP", "amount": "1.3 bags/acre", "when": "Basal application only — soybean fixes its own N"},
            {"name": "MOP", "amount": "0.7 bags/acre", "when": "Basal application"},
            {"name": "Sulfur (Gypsum)", "amount": "100 kg/acre", "when": "Basal — improves protein content"}
        ],
        "organic": [
            {"name": "FYM", "amount": "4 tonnes/acre", "when": "2-3 weeks before sowing"},
            {"name": "Rhizobium + PSB inoculant", "amount": "Seed treatment", "when": "Before sowing — critical for N fixation"},
            {"name": "Vermicompost", "amount": "1 tonne/acre", "when": "At sowing"}
        ],
        "tip": "Never skip Rhizobium seed treatment — it replaces 80-100kg urea naturally. Molybdenum spray (0.1%) boosts nodulation."
    },
    "mustard": {
        "npk": "N:80 | P:40 | K:40 kg/hectare",
        "chemical": [
            {"name": "Urea", "amount": "1.75 bags/acre", "when": "50% at sowing + 50% at first irrigation (25-30 days)"},
            {"name": "DAP", "amount": "0.9 bags/acre", "when": "Basal application"},
            {"name": "Sulfur (elemental)", "amount": "20 kg/acre", "when": "Basal — mustard needs sulfur for oil content"}
        ],
        "organic": [
            {"name": "FYM", "amount": "4 tonnes/acre", "when": "3 weeks before sowing"},
            {"name": "Vermicompost", "amount": "1.5 tonnes/acre", "when": "At sowing"},
            {"name": "Azotobacter", "amount": "Seed treatment", "when": "Before sowing"}
        ],
        "tip": "Sulfur is the most critical nutrient for mustard — it directly increases oil content. Never skip it."
    },
    "onion": {
        "npk": "N:100 | P:50 | K:100 kg/hectare",
        "chemical": [
            {"name": "Urea", "amount": "2.2 bags/acre", "when": "Split: 30%, 40%, 30% at 15, 30, 45 days after transplanting"},
            {"name": "DAP", "amount": "1.1 bags/acre", "when": "Basal application"},
            {"name": "MOP", "amount": "1.7 bags/acre", "when": "Half basal + half at bulb initiation"}
        ],
        "organic": [
            {"name": "FYM/Compost", "amount": "6 tonnes/acre", "when": "Before transplanting"},
            {"name": "Vermicompost", "amount": "2 tonnes/acre", "when": "At transplanting"},
            {"name": "Neem Cake", "amount": "100 kg/acre", "when": "At transplanting — controls soil pests"}
        ],
        "tip": "Potassium is critical for onion bulb size and storage quality. Stop irrigation 15 days before harvest for better shelf life."
    },
    "potato": {
        "npk": "N:180 | P:80 | K:150 kg/hectare",
        "chemical": [
            {"name": "Urea", "amount": "3.9 bags/acre", "when": "50% at planting + 50% at earthing up (30 days)"},
            {"name": "DAP", "amount": "1.7 bags/acre", "when": "Basal application"},
            {"name": "MOP", "amount": "2.5 bags/acre", "when": "50% basal + 50% at earthing up"}
        ],
        "organic": [
            {"name": "FYM", "amount": "8 tonnes/acre", "when": "2-3 weeks before planting"},
            {"name": "Vermicompost", "amount": "2 tonnes/acre", "when": "At planting"},
            {"name": "Trichoderma", "amount": "Mix in soil", "when": "At planting — prevents fungal diseases"}
        ],
        "tip": "Potato is a heavy feeder — never skip potassium. Boron (0.3%) and calcium spray at tuber initiation improves tuber quality and reduces hollow heart."
    },
    "chilli": {
        "npk": "N:120 | P:60 | K:60 kg/hectare",
        "chemical": [
            {"name": "Urea", "amount": "2.6 bags/acre", "when": "Split in 4 doses: transplanting, 30, 60, 90 days"},
            {"name": "DAP", "amount": "1.3 bags/acre", "when": "Basal application"},
            {"name": "MOP", "amount": "1 bag/acre", "when": "Basal + at fruiting stage"}
        ],
        "organic": [
            {"name": "FYM/Compost", "amount": "6 tonnes/acre", "when": "Before transplanting"},
            {"name": "Vermicompost", "amount": "2 tonnes/acre", "when": "At transplanting"},
            {"name": "Calcium + Boron spray", "amount": "0.5% + 0.1%", "when": "At flowering — prevents fruit drop"}
        ],
        "tip": "Calcium and boron spray at flowering stage dramatically reduces fruit drop and improves fruit set in chilli."
    },
    "chickpea": {
        "npk": "N:20 | P:40 | K:20 kg/hectare",
        "chemical": [
            {"name": "DAP", "amount": "0.9 bags/acre", "when": "Basal — chickpea fixes its own nitrogen"},
            {"name": "MOP", "amount": "0.35 bags/acre", "when": "Basal application"},
            {"name": "Sulfur", "amount": "10 kg/acre", "when": "Basal application"}
        ],
        "organic": [
            {"name": "FYM", "amount": "3 tonnes/acre", "when": "3 weeks before sowing"},
            {"name": "Rhizobium inoculant", "amount": "Seed treatment", "when": "Before sowing — essential for N fixation"},
            {"name": "PSB", "amount": "Seed treatment", "when": "Before sowing — improves phosphorus uptake"}
        ],
        "tip": "Chickpea fixes its own nitrogen through Rhizobium — never apply heavy doses of urea. Molybdenum (0.1% spray) boosts nodule formation."
    },
    "banana": {
        "npk": "N:200 | P:60 | K:300 kg/hectare",
        "chemical": [
            {"name": "Urea", "amount": "4.3 bags/acre", "when": "Split monthly from planting to bunch emergence (8-10 doses)"},
            {"name": "DAP", "amount": "1.3 bags/acre", "when": "At planting"},
            {"name": "MOP", "amount": "5 bags/acre", "when": "Split monthly — banana needs very high potassium"}
        ],
        "organic": [
            {"name": "FYM", "amount": "10 kg/plant", "when": "At planting and every 3 months"},
            {"name": "Vermicompost", "amount": "2 kg/plant", "when": "Every 2 months"},
            {"name": "Pseudomonas + Trichoderma", "amount": "Soil drench", "when": "At planting — prevents Panama wilt"}
        ],
        "tip": "Banana is a potassium-hungry crop — K deficiency causes 'blue disease' (leaf margin burn). Bunch covering with polybag improves fruit quality."
    },
    "mango": {
        "npk": "N:1000 | P:500 | K:1000 g/tree/year (mature tree)",
        "chemical": [
            {"name": "Urea", "amount": "2.2 kg/tree", "when": "Split: after harvest + before flowering (October-November)"},
            {"name": "SSP (Single Super Phosphate)", "amount": "3 kg/tree", "when": "After harvest (June-July)"},
            {"name": "MOP", "amount": "1.7 kg/tree", "when": "Split: after harvest + pre-flowering"}
        ],
        "organic": [
            {"name": "FYM", "amount": "50 kg/tree", "when": "After harvest — June to August"},
            {"name": "Vermicompost", "amount": "10 kg/tree", "when": "Before flowering — October"},
            {"name": "Micronutrient spray (Zinc + Boron)", "amount": "0.5% ZnSO4 + 0.3% Borax", "when": "At panicle initiation"}
        ],
        "tip": "Stop all nitrogen application 3 months before flowering — excess N causes vegetative growth instead of flowers. Paclobutrazol soil drench (2g/m canopy) promotes flowering in alternate bearing varieties."
    },
    "turmeric": {
        "npk": "N:60 | P:50 | K:120 kg/hectare",
        "chemical": [
            {"name": "Urea", "amount": "1.3 bags/acre", "when": "Split: 45 days and 90 days after planting"},
            {"name": "DAP", "amount": "1.1 bags/acre", "when": "Basal application"},
            {"name": "MOP", "amount": "2 bags/acre", "when": "Half basal + half at 90 days"}
        ],
        "organic": [
            {"name": "FYM", "amount": "8 tonnes/acre", "when": "Before planting — turmeric loves organic matter"},
            {"name": "Neem Cake", "amount": "200 kg/acre", "when": "At planting — controls rhizome rot"},
            {"name": "Trichoderma viride", "amount": "Mix with FYM", "when": "At planting — prevents rhizome rot"}
        ],
        "tip": "Turmeric requires shade — intercrop with banana or use shade net (25%). High potassium improves curcumin content (the yellow color pigment)."
    },
    "ginger": {
        "npk": "N:75 | P:50 | K:75 kg/hectare",
        "chemical": [
            {"name": "Urea", "amount": "1.6 bags/acre", "when": "Split: 40, 75, 110 days after planting"},
            {"name": "DAP", "amount": "1.1 bags/acre", "when": "Basal application"},
            {"name": "MOP", "amount": "1.25 bags/acre", "when": "Half basal + half at 75 days"}
        ],
        "organic": [
            {"name": "FYM", "amount": "8 tonnes/acre", "when": "Before planting"},
            {"name": "Vermicompost", "amount": "2 tonnes/acre", "when": "At planting"},
            {"name": "Neem Cake", "amount": "200 kg/acre", "when": "At planting — prevents rhizome rot and nematodes"}
        ],
        "tip": "Treat seed rhizomes with Mancozeb 0.3% for 30 minutes before planting to prevent soft rot. Mulching with dry leaves (5 tonnes/acre) conserves moisture and adds organic matter."
    },
    "pomegranate": {
        "npk": "N:625 | P:250 | K:250 g/tree/year",
        "chemical": [
            {"name": "Urea", "amount": "1.4 kg/tree", "when": "Split in 3 doses: Feb, June, September"},
            {"name": "SSP", "amount": "1.5 kg/tree", "when": "February application"},
            {"name": "MOP", "amount": "0.4 kg/tree", "when": "February + June split"}
        ],
        "organic": [
            {"name": "FYM", "amount": "20 kg/tree", "when": "February — before new flush"},
            {"name": "Vermicompost", "amount": "5 kg/tree", "when": "June application"},
            {"name": "Boron + Zinc spray", "amount": "0.3% Borax + 0.5% ZnSO4", "when": "At fruit set — improves fruit size and colour"}
        ],
        "tip": "Bahar treatment (water/chemical stress) is used to control flowering time in pomegranate. Calcium spray (0.5%) at fruit development reduces cracking."
    },
    "lentil": {
        "npk": "N:20 | P:40 | K:20 kg/hectare",
        "chemical": [
            {"name": "DAP", "amount": "0.9 bags/acre", "when": "Basal — lentil fixes its own nitrogen"},
            {"name": "MOP", "amount": "0.35 bags/acre", "when": "Basal application"},
            {"name": "Sulfur", "amount": "10 kg/acre", "when": "Basal application"}
        ],
        "organic": [
            {"name": "FYM", "amount": "3 tonnes/acre", "when": "3-4 weeks before sowing"},
            {"name": "Rhizobium inoculant", "amount": "Seed treatment", "when": "Before sowing — fixes atmospheric nitrogen"},
            {"name": "PSB", "amount": "Seed treatment", "when": "Before sowing"}
        ],
        "tip": "Like all pulses, lentil fixes its own nitrogen — Rhizobium seed treatment is more valuable than urea. Zinc spray (0.5%) at flowering improves seed fill."
    },
    "sunflower": {
        "npk": "N:80 | P:60 | K:60 kg/hectare",
        "chemical": [
            {"name": "Urea", "amount": "1.75 bags/acre", "when": "50% basal + 50% at knee height (30 days)"},
            {"name": "DAP", "amount": "1.3 bags/acre", "when": "Basal application"},
            {"name": "MOP", "amount": "1 bag/acre", "when": "Basal application"}
        ],
        "organic": [
            {"name": "FYM", "amount": "4 tonnes/acre", "when": "Before sowing"},
            {"name": "Vermicompost", "amount": "1.5 tonnes/acre", "when": "At sowing"},
            {"name": "Boron spray", "amount": "0.3% Borax", "when": "At bud initiation — critical for seed set"}
        ],
        "tip": "Boron is the most critical micronutrient for sunflower — deficiency causes empty seeds. Apply boron spray twice: bud stage and 50% flowering."
    },
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

    # aliases so farmers can type common names
    aliases = {
        "ganhu": "wheat", "gehun": "wheat", "gehu": "wheat",
        "dhan": "rice", "paddy": "rice",
        "makka": "maize", "corn": "maize",
        "sarson": "mustard", "rape": "mustard",
        "chana": "chickpea", "gram": "chickpea",
        "moong": "lentil", "masoor": "lentil", "dal": "lentil",
        "hari mirch": "chilli", "mirchi": "chilli", "pepper": "chilli",
        "aloo": "potato",
        "pyaz": "onion", "pyaaz": "onion",
        "kela": "banana",
        "aam": "mango",
        "haldi": "turmeric",
        "adrak": "ginger",
        "anaar": "pomegranate",
        "surajmukhi": "sunflower",
        "soyabean": "soybean",
    }

    for alias, crop in aliases.items():
        if alias in msg_lower:
            msg_lower = msg_lower.replace(alias, crop)

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

    crop_list = "Rice 🌾 | Wheat 🌾 | Cotton 🌿 | Maize 🌽 | Tomato 🍅 | Groundnut | Sugarcane | Bajra | Jowar | Soybean | Mustard | Onion | Potato | Chilli | Chickpea | Banana 🍌 | Mango 🥭 | Turmeric | Ginger | Pomegranate | Lentil | Sunflower"
    english_response = (
        f"🧪 I can suggest fertilizers for these crops:\n\n"
        f"{crop_list}\n\n"
        f"Please tell me your **crop name** and I'll give you complete fertilizer guidance!\n\n"
        f"Example: *'fertilizer for wheat'* or *'sarson ke liye khad'*"
    )
    return _translate_via_groq(english_response, language)
