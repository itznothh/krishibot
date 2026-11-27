import test from "node:test";
import assert from "node:assert/strict";
import {
  BrowserVoiceInput,
  SPEECH_LANGUAGES,
  extractSpeakableText,
  getSpeechRecognition,
  normalizeTranscriptEdit,
  releaseSubmission,
  speakText,
  stopSpeech,
  tryAcquireSubmission,
} from "./browserVoice.js";

function fakeRecognitionClass({ startError } = {}) {
  const instances = [];
  class FakeRecognition {
    constructor() { instances.push(this); }
    start() { if (startError) throw startError; this.started = true; }
    stop() { this.stopped = true; }
    abort() { this.aborted = true; }
  }
  FakeRecognition.instances = instances;
  return FakeRecognition;
}

test("recognition starts with selected English, Hindi and Kannada language codes", () => {
  for (const [language, expected] of Object.entries(SPEECH_LANGUAGES)) {
    const Recognition = fakeRecognitionClass();
    const controller = new BrowserVoiceInput({ Recognition });
    assert.equal(controller.start(language), true);
    const recognition = Recognition.instances[0];
    assert.equal(recognition.lang, expected);
    assert.equal(recognition.interimResults, true);
    assert.equal(recognition.continuous, false);
    recognition.onstart();
    assert.equal(controller.state, "listening");
    controller.stop();
    recognition.onend();
    assert.equal(controller.state, "idle");
  }
});

test("unsupported recognition and synchronous permission errors recover cleanly", () => {
  const messages = [];
  const unsupported = new BrowserVoiceInput({ Recognition:null, onMessage:message=>messages.push(message) });
  assert.equal(unsupported.start("en"), false);
  assert.match(messages.at(-1), /not supported/i);
  assert.equal(unsupported.state, "idle");

  const denied = new Error("denied");
  denied.name = "NotAllowedError";
  const Recognition = fakeRecognitionClass({ startError:denied });
  const controller = new BrowserVoiceInput({ Recognition, onMessage:message=>messages.push(message) });
  assert.equal(controller.start("hi"), false);
  assert.equal(controller.state, "idle");
  assert.match(messages.at(-1), /microphone access was denied/i);
});

test("asynchronous permission and language errors clear the recording state", () => {
  const Recognition = fakeRecognitionClass();
  const messages = [];
  const controller = new BrowserVoiceInput({ Recognition, onMessage:message=>messages.push(message) });
  controller.start("kn");
  const recognition = Recognition.instances[0];
  recognition.onerror({ error:"not-allowed" });
  assert.equal(controller.state, "idle");
  assert.match(messages.at(-1), /microphone access was denied/i);
  assert.equal(controller.start("kn"), true);
  Recognition.instances[1].onerror({ error:"language-not-supported" });
  assert.equal(controller.state, "idle");
  assert.match(messages.at(-1), /selected language/i);
});

test("prevents duplicate sessions and reports empty or unexpectedly ended input", () => {
  const Recognition = fakeRecognitionClass();
  const messages = [];
  const controller = new BrowserVoiceInput({ Recognition, onMessage:message=>messages.push(message) });
  controller.start("en");
  assert.equal(controller.start("hi"), false);
  assert.equal(Recognition.instances.length, 1);
  const recognition = Recognition.instances[0];
  recognition.onend();
  assert.equal(controller.state, "idle");
  assert.match(messages.at(-1), /ended before speech/i);

  controller.start("en");
  Recognition.instances[1].onstart();
  Recognition.instances[1].onresult({ results:[] });
  Recognition.instances[1].onend();
  assert.match(messages.at(-1), /ended before speech/i);
});

test("transcript is delivered for editing and stop/dispose clean up the session", () => {
  const Recognition = fakeRecognitionClass();
  const transcripts = [];
  const controller = new BrowserVoiceInput({ Recognition, onTranscript:value=>transcripts.push(value) });
  controller.start("en");
  const recognition = Recognition.instances[0];
  recognition.onresult({ results:[[{ transcript:"My tomato leaves" }], [{ transcript:"have yellow spots" }]] });
  assert.deepEqual(transcripts, ["My tomato leaves have yellow spots"]);
  assert.equal(normalizeTranscriptEdit("My tomato leaves have brown spots"), "My tomato leaves have brown spots");
  assert.equal(normalizeTranscriptEdit(""), "");
  controller.stop({ discardPending:true });
  assert.equal(recognition.stopped, true);
  recognition.onend();
  assert.equal(controller.state, "idle");

  controller.start("hi");
  const active = Recognition.instances[1];
  controller.dispose();
  assert.equal(active.aborted, true);
  assert.equal(active.onresult, null);
  assert.equal(controller.state, "idle");
});

test("browser feature detection and submission lock handle unsupported and duplicate actions", () => {
  const Recognition = fakeRecognitionClass();
  assert.equal(getSpeechRecognition({ SpeechRecognition:Recognition }), Recognition);
  assert.equal(getSpeechRecognition({ webkitSpeechRecognition:Recognition }), Recognition);
  assert.equal(getSpeechRecognition({}), null);

  const lock = { current:false };
  assert.equal(tryAcquireSubmission(lock), true);
  assert.equal(tryAcquireSubmission(lock), false);
  releaseSubmission(lock);
  assert.equal(tryAcquireSubmission(lock), true);
});

test("speech synthesis uses matching language voices, supports stop, and reports gaps", () => {
  const utterances = [];
  class FakeUtterance {
    constructor(text) { this.text = text; utterances.push(this); }
  }
  const voice = { lang:"kn-IN", name:"Kannada voice" };
  const synthesis = { getVoices:()=>[voice], cancel(){ this.cancelled = true; }, speak(item){ this.current = item; } };
  const callbacks = { onStart:()=>{}, onEnd:()=>{}, onError:()=>{} };
  const result = speakText("**Hello** farmer", "kn", { speechSynthesis:synthesis, SpeechSynthesisUtterance:FakeUtterance }, callbacks);
  assert.equal(result.ok, true);
  assert.equal(result.utterance.lang, "kn-IN");
  assert.equal(result.utterance.voice, voice);
  assert.equal(result.utterance.text, "Hello farmer");
  assert.equal(synthesis.cancelled, true);
  assert.equal(synthesis.current, result.utterance);

  const unavailable = speakText("नमस्ते", "hi", { speechSynthesis:{ ...synthesis, getVoices:()=>[{lang:"en-US"}] }, SpeechSynthesisUtterance:FakeUtterance });
  assert.equal(unavailable.ok, false);
  assert.match(unavailable.message, /Hindi speech voice/i);
  assert.equal(speakText("hello", "en", {}).ok, false);
  assert.equal(stopSpeech(synthesis), true);
  assert.equal(synthesis.cancelled, true);
  assert.equal(stopSpeech({}), false);
});

test("extracts only readable text from message and structured diagnosis responses", () => {
  const message = {
    role:"bot", text:"**Check the soil moisture.**", status:"ai_response",
    id:12345, time:"10:42", data:{ secret:"internal metadata" },
  };
  assert.equal(extractSpeakableText(message), "Check the soil moisture.");

  const diagnosis = extractSpeakableText({
    role:"bot", status:"image_analysis", id:987,
    data:{
      success:true, crop:"Tomato", visible_symptoms:["Yellow spots near leaf edges"],
      suspected_disease:"Possible early blight", severity:"Mild", confidence_status:"uncertain",
      possible_causes:["Fungal infection"],
      treatment:{ immediate_steps:["Remove badly affected leaves"], organic:["Improve airflow"], chemical:["Use only a locally approved product as labelled"] },
      prevention:["Avoid overhead watering"], additional_information_needed:["Share a clearer photo"],
      provider:"internal-provider", raw_response:"do not speak this",
    },
  });
  assert.match(diagnosis, /Crop: Tomato/);
  assert.match(diagnosis, /The image assessment is uncertain/);
  assert.match(diagnosis, /Visible symptoms: Yellow spots near leaf edges/);
  assert.match(diagnosis, /Organic approaches: Improve airflow/);
  assert.doesNotMatch(diagnosis, /internal-provider|raw_response|987|success/);

  const weather = extractSpeakableText({
    role:"bot", status:"weather", id:654,
    data:{ location:"Mysuru", temperature:30, condition:"Clear", humidity:70, wind_speed:2.5,
      farming_advice:"Check soil moisture before irrigating.", source:"OpenWeatherMap", retrieved_at:"2026-11-27T00:00:00Z" },
  });
  assert.match(weather, /Weather for: Mysuru/);
  assert.match(weather, /Farming advisory: Check soil moisture/);
  assert.doesNotMatch(weather, /OpenWeatherMap|2026|654/);

  assert.equal(extractSpeakableText({ role:"bot", id:1, time:"10:42", status:"unknown", data:{ arbitrary:{ value:true } } }), "");
});

test("rejects object coercion, undefined and raw JSON while decoding known JSON text", () => {
  assert.equal(extractSpeakableText({}), "");
  assert.equal(extractSpeakableText(undefined), "");
  assert.equal(extractSpeakableText("[object Object]"), "");
  assert.equal(extractSpeakableText("undefined"), "");
  assert.equal(extractSpeakableText('{"status":"ok","secret":"x"}'), "");
  assert.equal(extractSpeakableText('{"message":"Water the crop in the morning","api_key":"hidden"}'), "Water the crop in the morning");

  class FakeUtterance { constructor(text) { this.text = text; } }
  const synthesis = { getVoices:()=>[], speak(item){ this.current = item; }, cancel(){ this.cancelled = true; } };
  const environment = { speechSynthesis:synthesis, SpeechSynthesisUtterance:FakeUtterance };
  const result = speakText({ id:4, data:{ arbitrary:"metadata" } }, "en", environment);
  assert.equal(result.ok, false);
  assert.match(result.message, /no reply text/i);
  assert.equal(synthesis.current, undefined);
});

test("preserves all three speech languages and replaces a previous utterance cleanly", () => {
  class FakeUtterance { constructor(text) { this.text = text; } }
  const synthesis = {
    voices:[], cancelled:0, utterances:[],
    getVoices(){ return this.voices; },
    cancel(){ this.cancelled += 1; },
    speak(item){ this.utterances.push(item); },
  };
  const environment = { speechSynthesis:synthesis, SpeechSynthesisUtterance:FakeUtterance };
  for (const [language, expected] of [["en","en-IN"],["hi","hi-IN"],["kn","kn-IN"]]) {
    const result = speakText("नमस्ते farmer", language, environment);
    assert.equal(result.ok, true);
    assert.equal(result.utterance.lang, expected);
  }
  assert.equal(synthesis.cancelled, 3);
  assert.equal(synthesis.utterances.length, 3);
  assert.equal(stopSpeech(synthesis), true);
  assert.equal(synthesis.cancelled, 4);
});

test("stops the previous reply even when the next language has no installed voice", () => {
  class FakeUtterance { constructor(text) { this.text = text; } }
  const synthesis = {
    cancelled:0, utterances:[], getVoices:()=>[{ lang:"en-IN" }],
    cancel(){ this.cancelled += 1; }, speak(item){ this.utterances.push(item); },
  };
  const environment = { speechSynthesis:synthesis, SpeechSynthesisUtterance:FakeUtterance };
  assert.equal(speakText("First answer", "en", environment).ok, true);
  const unsupported = speakText("ಹಲೋ", "kn", environment);
  assert.equal(unsupported.ok, false);
  assert.match(unsupported.message, /Kannada speech voice/);
  assert.equal(synthesis.cancelled, 2);
  assert.equal(synthesis.utterances.length, 1);
});
