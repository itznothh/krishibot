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
   $env:AGMARKNET_API_KEY="your-data-gov-in-key"
   python app.py
   ```

   `GROQ_API_KEY` enables AI answers and image diagnosis. `OPENWEATHER_API_KEY` enables live weather. `AGMARKNET_API_KEY` enables live mandi data. Twilio credentials are only needed for the WhatsApp webhook.

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
- **Backend:** Deploy `backend/` to Render using its `render.yaml`; set `GROQ_API_KEY`, `OPENWEATHER_API_KEY`, and `AGMARKNET_API_KEY` in the service environment. Set `CORS_ORIGINS` to the comma-separated public frontend origins when using a custom deployment; local Vite and the existing Vercel frontend are allowed by default.
- **WhatsApp:** Set `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, and `TWILIO_WEBHOOK_URL` in Render. The webhook URL must be the exact public HTTPS URL configured in Twilio, for example `https://your-service.onrender.com/whatsapp`. Configure Twilio's inbound WhatsApp webhook to use that same URL.

### Environment checklist

| Variable | Needed for | Notes |
| --- | --- | --- |
| `GROQ_API_KEY` | Chat, image diagnosis, scheme answers, Hindi/Kannada specialist translation | Backend secret; required for live AI responses. |
| `OPENWEATHER_API_KEY` | Weather conditions and weather advisory | Backend secret; weather is unavailable without it. |
| `AGMARKNET_API_KEY` | Live mandi market and price data | Backend secret; obtain/rotate through data.gov.in. Missing configuration returns `503`. |
| `TWILIO_ACCOUNT_SID` | WhatsApp webhook media download | Backend secret/configuration. |
| `TWILIO_AUTH_TOKEN` | WhatsApp signature validation and media download | Backend secret. |
| `TWILIO_WEBHOOK_URL` | WhatsApp signature validation | Exact externally reachable HTTPS callback URL, including `/whatsapp`. |
| `VITE_BACKEND_URL` | Frontend API requests | Set to the public Flask base URL for non-default/custom deployments; it is embedded in the frontend build. |
| `CORS_ORIGINS` | Restrict API browser access to a custom frontend | Optional comma-separated origin list. Defaults allow local Vite and the existing Vercel frontend. |
| `RATE_LIMIT_CHAT_PER_MINUTE` | Chat requests per client IP | Optional; defaults to 20. |
| `RATE_LIMIT_IMAGE_PER_MINUTE` | Image analysis requests per client IP | Optional; defaults to 5. |
| `RATE_LIMIT_SCHEMES_PER_MINUTE` | Scheme AI requests per client IP | Optional; defaults to 5. |
| `RATE_LIMIT_WEATHER_PER_MINUTE` | Weather-provider requests per client IP | Optional; defaults to 15, in addition to the chat limit. |
| `RATE_LIMIT_MANDI_MARKETS_PER_MINUTE` | Mandi market lookups per client IP | Optional; defaults to 20. |
| `RATE_LIMIT_MANDI_PRICES_PER_MINUTE` | Mandi price lookups per client IP | Optional; defaults to 30. |
| `RATE_LIMIT_WHATSAPP_PER_MINUTE` | Signed WhatsApp requests per sender | Optional; defaults to 15. Signed sender IDs are used when they match WhatsApp's phone-number form; otherwise the socket/proxy-derived client address is used. |
| `RATE_LIMIT_TRUSTED_PROXY_HOPS` | Number of trusted proxy hops for `X-Forwarded-For` | Optional; defaults to `0`, so proxy headers are ignored. Set only after confirming the exact proxy chain and that it sanitizes/appends this header. |

The rate limiter uses a bounded, thread-safe in-memory sliding window. It applies per endpoint and client IP and returns HTTP `429` with `Retry-After` when the configured limit is exceeded. This requires no added service, but counters are local to one worker process: they reset on restart and are not shared across Gunicorn workers or Render instances. For scaled deployments, use a shared store (such as Redis/Render Key Value) before relying on limits as a hard provider-spend ceiling. Render proxies requests, so set `RATE_LIMIT_TRUSTED_PROXY_HOPS` only after verifying the forwarded chain for the deployed service; leaving it at `0` is spoof-resistant but may group clients by the socket peer address.

Firebase Authentication currently uses the web configuration in `frontend/src/firebase.js`; it is a public browser configuration, not a server secret. Confirm the Firebase project and authorized domains are correct for the deployed frontend. No Firebase environment variable is currently read by the code.

## Voice input

Voice typing uses the browser's Web Speech API. Choose English, Hindi, or Kannada before tapping the microphone. Recognition quality and availability depend on the browser, its speech service, microphone permissions, network, and background noise. The transcript stays editable before sending. Chrome or Edge generally provide the broadest support.

## Notes

- Chat follow-ups include recent turns so the assistant can understand references such as “what about this crop?”
- Farming recommendations can depend on local conditions. Confirm chemical use, label rates, and diagnosis with a local KVK or agricultural officer.
- The app uses Firebase Authentication; configure an appropriate Firebase project for your deployment.
