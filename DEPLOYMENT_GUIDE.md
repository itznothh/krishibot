# 🚀 KrishiBot — Free Deployment Guide
# Backend → Render.com | Frontend → Vercel

---

## Architecture Overview

```
[User Browser]
      │
      ▼
[Vercel — Frontend]          ← Free static hosting
frontend/index.html
      │  API calls
      ▼
[Render.com — Backend]       ← Free Flask hosting
backend/app.py
      │
      ├──▶ Open-Meteo API    ← Free weather (no key!)
      ├──▶ Claude API        ← AI responses
      └──▶ MyMemory API      ← Free translation (no key!)
```

---

## 💰 Cost Breakdown

| Service     | What it does         | Cost |
|-------------|----------------------|------|
| Vercel      | Host frontend        | FREE |
| Render.com  | Host Flask backend   | FREE |
| Open-Meteo  | Real-time weather    | FREE (no key!) |
| MyMemory    | Translation EN/HI/KN | FREE (no key!) |
| Claude API  | AI farming answers   | Free $5 credit |

**Total: ₹0/month** ✅

---

## PART 1 — Deploy Backend to Render.com

### Step 1: Push backend to GitHub

```bash
# From inside the krishibot-vercel/ folder:
git init
git add .
git commit -m "KrishiBot initial commit"

# Create a repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/krishibot.git
git push -u origin main
```

### Step 2: Create Render account
- Go to **https://render.com** → Sign up (free)
- Click **"New +"** → **"Web Service"**
- Connect your GitHub account
- Select your **krishibot** repository

### Step 3: Configure Render settings

Fill in these fields:
```
Name:           krishibot-api
Runtime:        Python 3
Root Directory: backend          ← IMPORTANT: set this!
Build Command:  pip install -r requirements.txt
Start Command:  gunicorn app:app --bind 0.0.0.0:$PORT
```

### Step 4: Add environment variable
- Scroll to **"Environment Variables"**
- Click **"Add Environment Variable"**
- Key:   `ANTHROPIC_API_KEY`
- Value: `your_actual_key_from_console.anthropic.com`
- Click **"Create Web Service"**

### Step 5: Wait for deploy (~3 minutes)
- Render will build and start your Flask app
- You'll get a URL like: `https://krishibot-api.onrender.com`
- Test it: open `https://krishibot-api.onrender.com/health` in browser
- You should see: `{"service": "KrishiBot API", "status": "ok"}`

> ⚠️ **Free Render note:** The free tier "sleeps" after 15 minutes of inactivity.
> First request after sleep takes ~30 seconds to wake up. This is normal and fine for a college project!

---

## PART 2 — Update Frontend with Your Render URL

Open `frontend/index.html` and find this line (around line 340):

```javascript
const RENDER_BACKEND = 'https://YOUR-APP-NAME.onrender.com';
```

Replace with your actual Render URL:
```javascript
const RENDER_BACKEND = 'https://krishibot-api.onrender.com';
```

Save the file.

---

## PART 3 — Deploy Frontend to Vercel

### Step 1: Create Vercel account
- Go to **https://vercel.com** → Sign up with GitHub (free)

### Step 2: Import project
- Click **"Add New..."** → **"Project"**
- Select your **krishibot** GitHub repository
- Click **"Import"**

### Step 3: Configure Vercel settings

```
Framework Preset:  Other
Root Directory:    ./              ← Keep as root (vercel.json handles routing)
Build Command:     (leave empty)
Output Directory:  frontend
```

Click **"Deploy"**

### Step 4: Get your live URL
- Vercel deploys in ~1 minute
- You'll get a URL like: `https://krishibot-yourname.vercel.app`
- Share this with anyone — it's your live KrishiBot! 🎉

---

## PART 4 — Test Everything

Open your Vercel URL and test these:

| Test | What to type | Expected |
|------|-------------|----------|
| Greeting | "hello" | Welcome message |
| Weather | Click 📍 then "weather" | Real weather data |
| Crops | "kharif season black soil" | Crop recommendations |
| Pest | "my wheat has aphids" | Pest advice |
| Fertilizer | "fertilizer for rice" | NPK guide |
| Hindi | Switch to हिंदी, ask anything | Hindi response |

---

## 🔧 Troubleshooting

### "Failed to fetch" error on Vercel site
→ Your Render URL in `frontend/index.html` is wrong. Double-check and redeploy.

### Render shows "Build failed"
→ Check that Root Directory is set to `backend` in Render settings.

### Weather not working
→ Open-Meteo is free with no key. If it fails, it's a network issue — try again.

### "AI not responding" / 500 error
→ Check that `ANTHROPIC_API_KEY` is set correctly in Render environment variables.

### Render is slow on first load
→ Normal! Free tier sleeps after 15 min. Just wait 30 seconds for it to wake up.

### CORS error in browser console
→ Flask-CORS is already configured. Make sure you're using the HTTPS Render URL, not HTTP.

---

## 🔄 How to Update Your App

After making changes to any file:

```bash
git add .
git commit -m "Update: describe your change"
git push
```

- **Render** auto-redeploys the backend ✅
- **Vercel** auto-redeploys the frontend ✅

---

## 📁 Final File Structure for GitHub

```
krishibot/                    ← Root of your GitHub repo
├── vercel.json               ← Vercel reads this
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── render.yaml
│   └── modules/
│       ├── weather.py        ← Uses Open-Meteo (free)
│       ├── crop_recommender.py
│       ├── pest_advisor.py
│       ├── fertilizer.py
│       ├── ai_assistant.py
│       └── language.py
└── frontend/
    └── index.html            ← Update RENDER_BACKEND URL here!
```

---

## 🎓 For Your College Submission

Your project uses:
- **REST API design** (Flask, JSON)
- **Cloud deployment** (Render + Vercel)
- **Free third-party APIs** (Open-Meteo, MyMemory, Anthropic)
- **Modular backend architecture**
- **Responsive frontend** (mobile + desktop)
- **Multi-language NLP** (EN, HI, KN)

Live URL format: `https://krishibot-[yourname].vercel.app`
