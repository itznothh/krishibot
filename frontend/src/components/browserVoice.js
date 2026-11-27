export const SPEECH_LANGUAGES = Object.freeze({ en:"en-IN", hi:"hi-IN", kn:"kn-IN" });

export function getSpeechRecognition(environment = globalThis) {
  return environment?.SpeechRecognition || environment?.webkitSpeechRecognition || null;
}

const ERROR_MESSAGES = {
  "not-allowed":"Microphone access was denied. Allow microphone access in your browser settings, then retry.",
  "service-not-allowed":"The browser blocked its speech service. Check browser permissions or type your question.",
  "no-speech":"No speech was detected. Check the microphone, speak after listening starts, or type your question.",
  "audio-capture":"No microphone was found. Connect or enable a microphone, then retry.",
  network:"The browser speech service is unavailable. Check your connection and try again.",
  "language-not-supported":"The browser speech service does not support the selected language. Choose another language or type your question.",
  aborted:"Voice input was stopped. You can retry or type your question.",
};

export function recognitionErrorMessage(code) {
  return ERROR_MESSAGES[code] || "Voice input could not continue. Check microphone access and try again, or type your question.";
}

export function normalizeTranscriptEdit(value) {
  return typeof value === "string" ? value : "";
}

export function tryAcquireSubmission(lockRef) {
  if (lockRef.current) return false;
  lockRef.current = true;
  return true;
}

export function releaseSubmission(lockRef) {
  lockRef.current = false;
}

export function stopSpeech(synthesis) {
  if (!synthesis || typeof synthesis.cancel !== "function") return false;
  try {
    synthesis.cancel();
    return true;
  } catch {
    return false;
  }
}

function cleanSpeechString(value) {
  if (typeof value !== "string") return "";
  let text = value.trim();
  if (!text) return "";

  // JSON response text is decoded through the same user-facing field allowlist
  // as structured responses; unknown fields and provider metadata are ignored.
  if (text.startsWith("{") || text.startsWith("[")) {
    try {
      const parsed = JSON.parse(text);
      if (parsed && typeof parsed === "object") return extractSpeakableText(parsed);
    } catch {
      return "";
    }
  }
  if (/^(?:\[object Object\]|undefined|null|\[object .+\])$/i.test(text)) return "";

  text = text
    .replace(/!\[[^\]]*\]\([^)]*\)/g, "")
    .replace(/\[([^\]]+)\]\((?:https?:\/\/[^)]*)\)/g, "$1")
    .replace(/https?:\/\/\S+/g, "")
    .replace(/\[object Object\]/gi, "")
    .replace(/\bundefined\b/gi, "")
    .replace(/^\s{0,3}#{1,6}\s+/gm, "")
    .replace(/^\s*[-*+]\s+/gm, "")
    .replace(/^\s*\d+\.\s+/gm, "")
    .replace(/[*_`>]/g, "")
    .replace(/[ \t]+/g, " ")
    .replace(/\n{2,}/g, ". ")
    .trim();
  text = Array.from(text).filter(character => {
    const code = character.charCodeAt(0);
    return !((code < 0x20 && code !== 0x09 && code !== 0x0a && code !== 0x0d)
      || (code >= 0x7f && code <= 0x9f));
  }).join("");
  return /[\p{L}\p{N}]/u.test(text) ? text : "";
}

function speechList(value) {
  if (typeof value === "string") return cleanSpeechString(value);
  if (!Array.isArray(value)) return "";
  return value.map(item => typeof item === "string"
    ? cleanSpeechString(item)
    : item && typeof item === "object" && typeof item.text === "string"
      ? cleanSpeechString(item.text)
      : "")
    .filter(Boolean).join(". ");
}

function labeledSpeech(label, value) {
  const text = speechList(value);
  return text ? `${label}: ${text}.` : "";
}

function diagnosisSpeech(diagnosis) {
  if (!diagnosis || typeof diagnosis !== "object" || Array.isArray(diagnosis)) return "";
  if (diagnosis.success === false) return "";
  const parts = [];
  if (diagnosis.crop) parts.push(labeledSpeech("Crop", diagnosis.crop));
  if (diagnosis.confidence_status === "uncertain" || !diagnosis.suspected_disease) {
    parts.push("The image assessment is uncertain.");
  }
  if (diagnosis.suspected_disease) parts.push(labeledSpeech("Suspected disease or pest", diagnosis.suspected_disease));
  if (diagnosis.severity) parts.push(labeledSpeech("Severity", diagnosis.severity));
  parts.push(labeledSpeech("Visible symptoms", diagnosis.visible_symptoms));
  parts.push(labeledSpeech("Possible causes", diagnosis.possible_causes));
  const treatment = diagnosis.treatment && typeof diagnosis.treatment === "object" ? diagnosis.treatment : {};
  parts.push(labeledSpeech("Immediate steps", treatment.immediate_steps));
  parts.push(labeledSpeech("Organic approaches", treatment.organic));
  parts.push(labeledSpeech("Chemical approaches", treatment.chemical));
  parts.push(labeledSpeech("Prevention", diagnosis.prevention));
  parts.push(labeledSpeech("Additional information needed", diagnosis.additional_information_needed));
  if (parts.filter(Boolean).length) {
    parts.push("This image-based guidance is preliminary. Confirm uncertain diagnoses and treatment choices with a local agricultural expert.");
  }
  return parts.filter(Boolean).join(" ");
}

function weatherSpeech(weather) {
  if (!weather || typeof weather !== "object" || Array.isArray(weather)) return "";
  const parts = [];
  const location = weather.location || weather.city;
  if (location) parts.push(labeledSpeech("Weather for", location));
  const condition = weather.description || weather.condition;
  if (condition) parts.push(labeledSpeech(weather.data_type === "forecast" ? "Forecast" : "Current conditions", condition));
  if (Number.isFinite(weather.temperature)) parts.push(`Temperature: ${weather.temperature} degrees Celsius.`);
  if (Number.isFinite(weather.humidity)) parts.push(`Humidity: ${weather.humidity} percent.`);
  if (Number.isFinite(weather.wind_speed)) parts.push(`Wind speed: ${weather.wind_speed} meters per second.`);
  parts.push(labeledSpeech("Farming advisory", weather.farming_advice));
  return parts.filter(Boolean).join(" ");
}

/** Extract only user-facing text; IDs, timestamps, status and provider metadata are excluded. */
export function extractSpeakableText(value) {
  if (typeof value === "string") return cleanSpeechString(value);
  if (!value || typeof value !== "object") return "";
  if (Array.isArray(value)) return speechList(value);

  const diagnosis = value.diagnosis || (value.status === "image_analysis" ? value.data : null);
  if (diagnosis) return diagnosisSpeech(diagnosis);
  const weather = value.weather || (value.status === "weather" ? value.data : null);
  if (weather) return weatherSpeech(weather);

  for (const key of ["text", "message", "answer", "response", "content", "result"]) {
    const candidate = value[key];
    if (typeof candidate === "string") {
      const cleaned = cleanSpeechString(candidate);
      if (cleaned) return cleaned;
    } else if (candidate && typeof candidate === "object") {
      const nested = extractSpeakableText(candidate);
      if (nested) return nested;
    }
  }

  if (value.suspected_disease || value.visible_symptoms || value.treatment) return diagnosisSpeech(value);

  if (value.farming_advice || value.temperature !== undefined || value.wind_speed !== undefined) {
    return weatherSpeech(value);
  }

  for (const key of ["data", "payload"]) {
    const nested = extractSpeakableText(value[key]);
    if (nested) return nested;
  }
  return "";
}

function startupErrorMessage(error) {
  if (error?.name === "NotAllowedError" || error?.name === "SecurityError") return ERROR_MESSAGES["not-allowed"];
  if (error?.name === "InvalidStateError") return "A voice session is already active. Stop it before retrying.";
  return recognitionErrorMessage(error?.name === "LanguageNotSupportedError" ? "language-not-supported" : "");
}

export class BrowserVoiceInput {
  constructor({ Recognition, onState = () => {}, onTranscript = () => {}, onMessage = () => {} }) {
    this.Recognition = Recognition;
    this.onState = onState;
    this.onTranscript = onTranscript;
    this.onMessage = onMessage;
    this.recognition = null;
    this.state = "idle";
    this.stopRequested = false;
    this.hadTranscript = false;
    this.errorReported = false;
    this.ignoreResults = false;
  }

  setState(state) {
    this.state = state;
    this.onState(state);
  }

  start(language) {
    if (this.recognition) {
      this.onMessage("Voice input is already active. Stop it before starting another session.");
      return false;
    }
    if (typeof this.Recognition !== "function") {
      this.onMessage("Voice input is not supported in this browser. Try a browser with Web Speech recognition on a secure connection, or type your question.");
      return false;
    }

    let recognition;
    try {
      recognition = new this.Recognition();
      recognition.lang = SPEECH_LANGUAGES[language] || SPEECH_LANGUAGES.en;
      recognition.interimResults = true;
      recognition.continuous = false;
      recognition.maxAlternatives = 3;
    } catch (error) {
      this.setState("idle");
      this.onMessage(startupErrorMessage(error));
      return false;
    }

    this.recognition = recognition;
    this.stopRequested = false;
    this.hadTranscript = false;
    this.errorReported = false;
    this.ignoreResults = false;
    this.onMessage("");
    this.setState("starting");

    recognition.onstart = () => {
      if (this.recognition === recognition) this.setState("listening");
    };
    recognition.onresult = (event) => {
      if (this.recognition !== recognition || this.ignoreResults || !event?.results) return;
      const transcript = Array.from(event.results)
        .map(result => result?.[0]?.transcript || "")
        .join(" ")
        .trim();
      if (!transcript) return;
      this.hadTranscript = true;
      this.onTranscript(transcript);
      this.onMessage("Transcript ready. Review and edit it before sending.");
    };
    recognition.onerror = (event) => {
      if (this.recognition !== recognition) return;
      this.errorReported = true;
      this.onMessage(recognitionErrorMessage(event?.error));
      this.finish(recognition);
    };
    recognition.onend = () => {
      if (this.recognition !== recognition) return;
      if (!this.errorReported && !this.hadTranscript) {
        this.onMessage(this.stopRequested
          ? "No transcript was captured. Retry speaking or type your question."
          : "Voice input ended before speech was captured. Check the microphone and try again.");
      } else if (!this.errorReported && this.hadTranscript) {
        this.onMessage("Transcript ready. Review and edit it before sending.");
      }
      this.finish(recognition);
    };

    try {
      recognition.start();
      return true;
    } catch (error) {
      if (this.recognition === recognition) {
        this.onMessage(startupErrorMessage(error));
        this.finish(recognition);
      }
      return false;
    }
  }

  stop({ discardPending = false } = {}) {
    const recognition = this.recognition;
    if (!recognition) {
      this.setState("idle");
      return;
    }
    this.stopRequested = true;
    this.ignoreResults = discardPending;
    this.setState("stopping");
    try {
      recognition.stop();
    } catch {
      try { recognition.abort?.(); } catch { /* Session is already closed. */ }
      this.finish(recognition);
      this.onMessage(this.hadTranscript
        ? "Transcript ready. Review and edit it before sending."
        : "No transcript was captured. Retry speaking or type your question.");
    }
  }

  finish(recognition) {
    if (this.recognition !== recognition) return;
    this.recognition = null;
    this.setState("idle");
  }

  dispose() {
    this.onState = () => {};
    this.onTranscript = () => {};
    this.onMessage = () => {};
    this.cancel();
  }

  cancel() {
    const recognition = this.recognition;
    this.recognition = null;
    if (recognition) {
      recognition.onstart = null;
      recognition.onresult = null;
      recognition.onerror = null;
      recognition.onend = null;
      try { recognition.abort?.(); } catch { /* Browser may have closed the session. */ }
    }
    this.stopRequested = true;
    this.setState("idle");
  }
}

export function speakText(text, language, environment = globalThis, callbacks = {}) {
  const cleanText = extractSpeakableText(text);
  if (!cleanText) return { ok:false, message:"There is no reply text to read aloud." };

  const synthesis = environment?.speechSynthesis;
  const Utterance = environment?.SpeechSynthesisUtterance;
  if (synthesis && typeof synthesis.cancel === "function") {
    try {
      synthesis.cancel();
    } catch {
      return { ok:false, message:"Could not stop the previous spoken reply. Try again or read the text." };
    }
  }
  if (!synthesis || typeof synthesis.speak !== "function" || typeof Utterance !== "function") {
    return { ok:false, message:"Spoken replies are not supported in this browser. You can read or copy the reply." };
  }
  const lang = SPEECH_LANGUAGES[language] || SPEECH_LANGUAGES.en;
  let voices;
  try {
    voices = typeof synthesis.getVoices === "function" ? synthesis.getVoices() : [];
  } catch {
    stopSpeech(synthesis);
    return { ok:false, message:"Could not load speech voices on this device. Try again or read the reply." };
  }
  const voice = voices.find(item => item.lang?.toLowerCase() === lang.toLowerCase())
    || voices.find(item => item.lang?.toLowerCase().split("-")[0] === lang.split("-")[0]);
  if (voices.length && !voice) {
    return { ok:false, message:`No ${language === "hi" ? "Hindi" : language === "kn" ? "Kannada" : "English"} speech voice is available on this device. Add a system voice or read the reply.` };
  }
  try {
    const utterance = new Utterance(cleanText);
    utterance.lang = lang;
    if (voice) utterance.voice = voice;
    utterance.onstart = callbacks.onStart;
    utterance.onend = callbacks.onEnd;
    utterance.onerror = callbacks.onError;
    synthesis.speak(utterance);
    return { ok:true, utterance };
  } catch {
    return { ok:false, message:"Could not start spoken reply. Try again or read the text." };
  }
}
