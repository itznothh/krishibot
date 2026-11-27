# KrishiBot

KrishiBot is a farming assistant for Indian farmers. The web app is built with React and Vite; a Flask API provides chat, crop, pest, fertilizer, weather, image analysis, scheme, and mandi endpoints.

## Project layout

```text
frontend/                 React + Vite web app
  src/components/         Chat, mandi, schemes, yield, and landing views
  src/api.js              Shared backend URL and API response handling
backend/                  Flask API and farming modules
  app.py                  HTTP routes and WhatsApp webhook
  modules/                AI, weather, crop, pest, fertilizer, and image logic
```

## Run locally

Requirements: Node.js and Python 3.10 or later.

1. Install and start the API:

   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   $env:GROQ_API_KEY="your-groq-key"
   $env:OPENWEATHER_API_KEY="your-openweather-key"
   python app.py
   ```

   `GROQ_API_KEY` enables AI answers. `OPENWEATHER_API_KEY` enables live weather. Twilio credentials are only needed for the WhatsApp webhook.

2. In a second terminal, start the web app:

   ```powershell
   cd frontend
   npm install
   $env:VITE_BACKEND_URL="http://localhost:5000"
   npm run dev
   ```

   Open the local URL printed by Vite. If `VITE_BACKEND_URL` is omitted, the app uses the deployed KrishiBot API.

## Deploy

- **Frontend:** Deploy `frontend/` to Vercel. Set `VITE_BACKEND_URL` to the public Flask API URL, then redeploy after changing it.
- **Backend:** Deploy `backend/` to Render using its `render.yaml`; set `GROQ_API_KEY` and `OPENWEATHER_API_KEY` in the service environment.
- **WhatsApp:** Configure Twilio's inbound webhook to point to `/whatsapp` on the deployed API and provide the Twilio credentials.

## Voice input

Voice typing uses the browser's Web Speech API. Choose English, Hindi, or Kannada before tapping the microphone. Recognition quality and availability depend on the browser, its speech service, microphone permissions, network, and background noise. The transcript stays editable before sending. Chrome or Edge generally provide the broadest support.

## Notes

- Chat follow-ups include recent turns so the assistant can understand references such as “what about this crop?”
- Farming recommendations can depend on local conditions. Confirm chemical use, label rates, and diagnosis with a local KVK or agricultural officer.
- The app uses Firebase Authentication; configure an appropriate Firebase project for your deployment.
