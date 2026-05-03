# 🌾 KrishiBot — Smart Farming Assistant

<div align="center">

![KrishiBot](https://img.shields.io/badge/KrishiBot-Smart%20Farming%20AI-4a7c59?style=for-the-badge&logo=leaf)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask)
![Groq](https://img.shields.io/badge/Groq-LLaMA%203.3-F55036?style=for-the-badge)
![Vercel](https://img.shields.io/badge/Vercel-Frontend-000000?style=for-the-badge&logo=vercel)
![Render](https://img.shields.io/badge/Render-Backend-46E3B7?style=for-the-badge&logo=render)

**An AI-powered farming assistant for Indian farmers — available on Web & WhatsApp**

[🌐 Live Demo](https://krishibot-flame.vercel.app) · [🐛 Report Bug](https://github.com/itznothh/krishibot/issues) · [⭐ Star this repo](https://github.com/itznothh/krishibot)

</div>

---

## 📸 Preview

> KrishiBot helps farmers with crop advice, pest control, fertilizer guidance, real-time weather, and crop disease detection — in English, Hindi, and Kannada.

---

## ✨ Features

- 🤖 **AI Intent Classification** — Every message is classified by LLaMA 3.3 before routing to the right module
- 🌦️ **Real-time Weather** — GPS-based weather with farmer-friendly farming advice
- 🌾 **Crop Advisor** — Recommends crops based on soil type, season, and region
- 🐛 **Pest & Disease** — Identifies pests and gives treatment with quantities
- 🧪 **Fertilizer Guide** — NPK recommendations for any crop
- 📷 **Crop Disease Scanner** — Upload a photo, Gemini Vision diagnoses the disease
- 🎤 **Voice Input** — Speak in Hindi/Kannada/English, auto-sends the message
- 💬 **Chat History** — ChatGPT-style sidebar with persistent localStorage history
- 🌐 **Multilingual** — English, हिंदी, ಕನ್ನಡ with strict language enforcement
- 📱 **WhatsApp Bot** — Full chatbot on WhatsApp via Twilio with location memory

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                    GitHub Repo                       │
│              itznothh/krishibot                      │
└──────────────┬──────────────────┬───────────────────┘
               │                  │
               ▼                  ▼
        ┌──────────┐       ┌──────────────┐
        │  Vercel  │       │    Render    │
        │ frontend/│       │   backend/   │
        │index.html│       │   app.py     │
        └──────────┘       └──────┬───────┘
                                  │
               ┌──────────────────┼──────────────────┐
               │                  │                  │
               ▼                  ▼                  ▼
          ┌─────────┐      ┌────────────┐    ┌──────────────┐
          │  Groq   │      │ OpenWeather│    │    Gemini    │
          │ LLaMA   │      │    API     │    │    Vision    │
          │  3.3    │      │            │    │    (Images)  │
          └─────────┘      └────────────┘    └──────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML, CSS, Vanilla JavaScript |
| Backend | Python, Flask |
| AI Model | Groq API → `llama-3.3-70b-versatile` |
| Image Analysis | Google Gemini Vision |
| Weather | OpenWeatherMap API |
| WhatsApp | Twilio Messaging API |
| Frontend Hosting | Vercel |
| Backend Hosting | Render |
| Version Control | GitHub |

---

## 📁 Project Structure

```
krishibot/
├── frontend/
│   └── index.html              # Complete frontend (single file)
│
└── backend/
    ├── app.py                  # Main Flask app + WhatsApp webhook
    ├── render.yaml             # Render deployment config
    ├── requirements.txt        # Python dependencies
    └── modules/
        ├── ai_assistant.py     # Groq LLaMA integration
        ├── weather.py          # OpenWeatherMap integration
        ├── crop_recommender.py # Crop advice module
        ├── pest_advisor.py     # Pest & disease module
        ├── fertilizer.py       # Fertilizer recommendations
        ├── image_analyzer.py   # Gemini Vision integration
        └── language.py        # Language detection
```

---

## 🚀 How It Works

Every message goes through this flow:

```
User Message
     ↓
Intent Classifier (Groq, temp=0)
     ↓
┌────┴──────────────────────────────┐
│  weather → OpenWeather + Groq     │
│  pest    → pest_advisor.py        │
│  crop    → crop_recommender.py    │
│  fertilizer → fertilizer.py      │
│  general → ai_assistant.py        │
└───────────────────────────────────┘
     ↓
Response sent back to user
```

This approach is smarter than keyword matching — the AI understands natural language and routes correctly even for ambiguous questions.

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10+
- Git

### 1. Clone the repo
```bash
git clone https://github.com/itznothh/krishibot.git
cd krishibot
```

### 2. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Set environment variables
Create a `.env` file in the `backend/` folder:
```env
GROQ_API_KEY=your_groq_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
GEMINI_API_KEY=your_gemini_api_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
```

### 4. Run locally
```bash
cd backend
python app.py
```
Open `frontend/index.html` in your browser.

---

## 🌐 Deployment

### Frontend → Vercel
1. Connect your GitHub repo to [Vercel](https://vercel.com)
2. Set root directory to `frontend`
3. Deploy — done!

### Backend → Render
1. Connect your GitHub repo to [Render](https://render.com)
2. Set root directory to `backend`
3. Add all environment variables
4. Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`
5. Deploy — done!

---

## 📱 WhatsApp Setup (Twilio)

1. Sign up at [twilio.com](https://twilio.com)
2. Activate WhatsApp Sandbox
3. Set webhook URL to: `https://your-render-url.onrender.com/whatsapp`
4. Add `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` to Render env vars
5. Send `join <sandbox-code>` from your WhatsApp to the Twilio number

---

## 🔑 API Keys Required

| API | Purpose | Free Tier |
|-----|---------|-----------|
| [Groq](https://console.groq.com) | AI responses + intent classification | ✅ Free |
| [OpenWeatherMap](https://openweathermap.org/api) | Real-time weather data | ✅ Free (1000 calls/day) |
| [Google Gemini](https://ai.google.dev) | Crop disease image analysis | ✅ Free tier |
| [Twilio](https://twilio.com) | WhatsApp messaging | ✅ Sandbox free |

---

## 📞 Support

**Kisan Helpline: 1800-180-1551** (Free · 24x7)

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## 📄 License

MIT License — feel free to use and modify.

---

<div align="center">
Made with ❤️ for Indian Farmers 🌾
</div>
