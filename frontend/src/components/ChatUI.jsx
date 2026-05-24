import { useState, useRef, useEffect, useCallback } from "react";
import ReactMarkdown from "react-markdown";

const BACKEND = "https://krishibot-api.onrender.com";

// ── Voice recognition helper ───────────────────────────────────────────────
const SpeechAPI = window.SpeechRecognition || window.webkitSpeechRecognition || null;

const LANG_SPEECH_CODE = { en:"en-IN", hi:"hi-IN", kn:"kn-IN" };

const SUGGESTIONS = [
  { icon: "🌾", text: "Which crops to grow this season?" },
  { icon: "🐛", text: "My tomato leaves have yellow spots" },
  { icon: "🌦️", text: "Weather advice for farming today" },
  { icon: "🧪", text: "Fertilizer for wheat crop" },
  { icon: "📸", text: "Diagnose my crop disease (send image)" },
  { icon: "🪴", text: "Best soil for rice cultivation" },
];

const LANG_OPTIONS = [
  { code: "en", label: "EN" },
  { code: "hi", label: "HI" },
  { code: "kn", label: "KN" },
];

// ── Rich data cards ────────────────────────────────────────────────────────

function WeatherCard({ data }) {
  if (!data) return null;
  return (
    <div style={S.infoCard}>
      <div style={{ display:"flex", alignItems:"center", gap:10, marginBottom:10 }}>
        <span style={{ fontSize:"1.5rem" }}>🌦️</span>
        <div style={{ flex:1 }}>
          <div style={{ fontWeight:700, color:"#b5d6a0", fontSize:"0.9rem" }}>{data.city || "Weather"}</div>
          <div style={{ color:"rgba(232,240,228,0.45)", fontSize:"0.76rem" }}>{data.description || ""}</div>
        </div>
        {data.temperature && (
          <div style={{ fontFamily:"'Sora',sans-serif", fontSize:"1.5rem", fontWeight:800, color:"#6aaa7a" }}>
            {Math.round(data.temperature)}°C
          </div>
        )}
      </div>
      {(data.humidity || data.wind_speed) && (
        <div style={{ display:"flex", gap:16, borderTop:"1px solid rgba(106,170,122,0.15)", paddingTop:10 }}>
          {data.humidity   && <span style={S.metaStat}>💧 {data.humidity}% humidity</span>}
          {data.wind_speed && <span style={S.metaStat}>💨 {data.wind_speed} km/h</span>}
        </div>
      )}
    </div>
  );
}

function CropCard({ data }) {
  const crops = data?.recommended_crops || data?.crops || [];
  if (!crops.length) return null;
  return (
    <div style={S.infoCard}>
      <div style={S.cardLabel}><span>🌾</span> Recommended Crops</div>
      <div style={{ display:"flex", flexWrap:"wrap", gap:6, marginTop:10 }}>
        {crops.slice(0,8).map((c,i) => (
          <span key={i} style={S.chip}>{typeof c==="string" ? c : c.name || c}</span>
        ))}
      </div>
    </div>
  );
}

function FertilizerCard({ data }) {
  const npk = data?.npk || {};
  if (!Object.keys(npk).length && !data?.fertilizers) return null;
  return (
    <div style={S.infoCard}>
      <div style={S.cardLabel}><span>🧪</span> NPK Recommendation</div>
      <div style={{ display:"flex", gap:8, marginTop:10 }}>
        {["N","P","K"].map(k => npk[k]!==undefined && (
          <div key={k} style={S.npkBox}>
            <div style={{ fontFamily:"'Sora',sans-serif", fontWeight:800, fontSize:"1.25rem", color:"#6aaa7a" }}>{npk[k]}</div>
            <div style={{ fontSize:"0.7rem", color:"rgba(232,240,228,0.45)", fontWeight:700 }}>
              {k==="N"?"Nitrogen":k==="P"?"Phosphorus":"Potassium"}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ImageResultCard({ data }) {
  if (!data?.disease && !data?.diagnosis) return null;
  return (
    <div style={{ ...S.infoCard, borderColor:"rgba(239,120,80,0.25)", background:"rgba(239,120,80,0.05)" }}>
      <div style={{ ...S.cardLabel, color:"#f4a261" }}><span>🔬</span> Disease Detected</div>
      <div style={{ color:"#e8f0e4", fontWeight:700, fontSize:"0.95rem", marginTop:8 }}>
        {data.disease || data.diagnosis}
      </div>
      {data.confidence && (
        <div style={{ color:"rgba(232,240,228,0.4)", fontSize:"0.76rem", marginTop:4 }}>
          Confidence: {data.confidence}
        </div>
      )}
    </div>
  );
}

// ── Message bubble ─────────────────────────────────────────────────────────

function Message({ msg }) {
  const isUser = msg.role === "user";
  return (
    <div style={{ display:"flex", flexDirection:isUser?"row-reverse":"row", gap:10, marginBottom:18, alignItems:"flex-end" }}>
      {!isUser && <div style={S.botAvatar}>🌾</div>}
      <div style={{ maxWidth:"74%", display:"flex", flexDirection:"column", gap:5, alignItems:isUser?"flex-end":"flex-start" }}>
        {msg.imageUrl && (
          <img src={msg.imageUrl} alt="crop" style={{ maxWidth:180, borderRadius:12, border:"1px solid rgba(106,170,122,0.2)" }} />
        )}
        {msg.text && (
          <div style={isUser ? S.userBubble : S.botBubble}>
            {isUser ? msg.text : (
              <ReactMarkdown
                components={{
                  p: ({children}) => <p style={{ margin:"0 0 6px" }}>{children}</p>,
                  strong: ({children}) => <strong style={{ color:"#b5d6a0", fontWeight:700 }}>{children}</strong>,
                  ul: ({children}) => <ul style={{ paddingLeft:18, margin:"4px 0" }}>{children}</ul>,
                  ol: ({children}) => <ol style={{ paddingLeft:18, margin:"4px 0" }}>{children}</ol>,
                  li: ({children}) => <li style={{ marginBottom:3 }}>{children}</li>,
                  h1: ({children}) => <h1 style={{ fontSize:"1rem", color:"#b5d6a0", fontWeight:700, margin:"8px 0 4px" }}>{children}</h1>,
                  h2: ({children}) => <h2 style={{ fontSize:"0.95rem", color:"#b5d6a0", fontWeight:700, margin:"8px 0 4px" }}>{children}</h2>,
                  h3: ({children}) => <h3 style={{ fontSize:"0.9rem", color:"#8fbc8f", fontWeight:700, margin:"6px 0 3px" }}>{children}</h3>,
                  code: ({children}) => <code style={{ background:"rgba(106,170,122,0.12)", borderRadius:4, padding:"1px 5px", fontSize:"0.85em", color:"#b5d6a0" }}>{children}</code>,
                  hr: () => <hr style={{ border:"none", borderTop:"1px solid rgba(106,170,122,0.15)", margin:"8px 0" }}/>,
                }}
              >
                {msg.text}
              </ReactMarkdown>
            )}
          </div>
        )}
        {msg.status==="weather"    && msg.data && <WeatherCard data={msg.data}/>}
        {msg.status==="crop"       && msg.data && <CropCard data={msg.data}/>}
        {msg.status==="fertilizer" && msg.data && <FertilizerCard data={msg.data}/>}
        {msg.status==="image_analysis" && msg.data && <ImageResultCard data={msg.data}/>}
        <div style={S.timestamp}>{msg.time}</div>
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div style={{ display:"flex", gap:10, alignItems:"flex-end", marginBottom:18 }}>
      <div style={S.botAvatar}>🌾</div>
      <div style={{ ...S.botBubble, padding:"14px 18px" }}>
        <div className="krishi-dots">
          <span/><span/><span/>
        </div>
      </div>
    </div>
  );
}

// ── Main component ─────────────────────────────────────────────────────────

export default function ChatUI({ user, onSignOut, onBack }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput]       = useState("");
  const [loading, setLoading]   = useState(false);
  const [lang, setLang]         = useState("en");
  const [location, setLocation] = useState(null);
  const [locLoading, setLocLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [imagePreview, setImagePreview] = useState(null);
  const [imageFile, setImageFile]       = useState(null);
  const [chatHistory, setChatHistory]   = useState([{ id:1, title:"Current chat", active:true }]);

  const endRef     = useRef(null);
  const textareaRef = useRef(null);
  const fileRef    = useRef(null);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior:"smooth" }); }, [messages, loading]);

  const now = () => new Date().toLocaleTimeString([], { hour:"2-digit", minute:"2-digit" });

  const addBot = (text, status, data) =>
    setMessages(prev => [...prev, { role:"bot", text, status, data, time:now(), id:Date.now() }]);

  const handleSend = useCallback(async () => {
    const text = input.trim();
    if (!text && !imageFile) return;
    if (loading) return;

    setMessages(prev => [...prev, {
      role:"user", text: text || "📸 Image sent",
      imageUrl: imagePreview, time:now(), id:Date.now()
    }]);
    setInput(""); setImagePreview(null); setImageFile(null);
    setLoading(true);

    try {
      if (imageFile) {
        const fd = new FormData();
        fd.append("image", imageFile);
        fd.append("language", lang);
        if (text) fd.append("message", text);
        const res  = await fetch(`${BACKEND}/analyze-image`, { method:"POST", body:fd });
        const data = await res.json();
        addBot(data.message || data.analysis || "Here's what I found in your crop image.", "image_analysis", data.data || data);
      } else {
        const res  = await fetch(`${BACKEND}/chat`, {
          method:"POST",
          headers:{ "Content-Type":"application/json" },
          body: JSON.stringify({ message:text, language:lang, lat:location?.lat, lon:location?.lon, context:{} }),
        });
        const data = await res.json();
        addBot(data.message, data.status, data.data);
      }
    } catch {
      addBot("⚠️ Could not reach KrishiBot server. The backend may be waking up (cold start on free tier — ~30–60s). Please try again shortly.", "error", null);
    }
    setLoading(false);
  }, [input, imageFile, imagePreview, lang, location, loading]);

  const handleKey = (e) => {
    if (e.key==="Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  const handleImage = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
    e.target.value = "";
  };

  const getLocation = () => {
    if (!navigator.geolocation) return;
    setLocLoading(true);
    navigator.geolocation.getCurrentPosition(
      p => { setLocation({ lat:p.coords.latitude, lon:p.coords.longitude }); setLocLoading(false); },
      ()  => setLocLoading(false)
    );
  };

  // ── Voice recognition ───────────────────────────────────────────────────
  const [listening, setListening] = useState(false);
  const recognizerRef = useRef(null);

  const toggleVoice = useCallback(() => {
    if (!SpeechAPI) {
      alert("Voice recognition is not supported in this browser. Try Chrome.");
      return;
    }
    if (listening) {
      recognizerRef.current?.stop();
      setListening(false);
      return;
    }
    const rec = new SpeechAPI();
    rec.lang = LANG_SPEECH_CODE[lang] || "en-IN";
    rec.interimResults = true;
    rec.continuous = false;
    rec.onstart  = () => setListening(true);
    rec.onend    = () => setListening(false);
    rec.onerror  = () => setListening(false);
    rec.onresult = (e) => {
      const transcript = Array.from(e.results).map(r => r[0].transcript).join("");
      setInput(transcript);
      if (e.results[e.results.length - 1].isFinal) {
        setListening(false);
      }
    };
    recognizerRef.current = rec;
    rec.start();
  }, [listening, lang]);

  const newChat = () => {
    setMessages([]); setInput(""); setImagePreview(null); setImageFile(null);
    setSidebarOpen(false);
    setChatHistory(prev => [{ id:Date.now(), title:"New chat", active:true }, ...prev.map(c=>({...c,active:false}))]);
  };

  const firstName = user?.displayName?.split(" ")[0] || user?.phoneNumber || "Farmer";
  const photo     = user?.photoURL;

  return (
    <div style={S.root}>
      <style>{CSS}</style>

      {/* Sidebar */}
      <aside style={{ ...S.sidebar, transform: sidebarOpen ? "translateX(0)" : "translateX(-100%)" }}>
        <div style={S.sidebarHead}>
          <span style={{ fontFamily:"'Sora',sans-serif", fontWeight:800, color:"#b5d6a0" }}>🌾 KrishiBot</span>
          <button style={S.iBtn} onClick={()=>setSidebarOpen(false)}>✕</button>
        </div>

        <div style={S.sidebarSection}>
          <div style={S.sLabel}>Language</div>
          <div style={{ display:"flex", gap:6, marginTop:8 }}>
            {LANG_OPTIONS.map(l=>(
              <button type="button" key={l.code}
                className={`krishi-lang-btn${lang===l.code?" active":""}`}
                onClick={()=>setLang(l.code)}
                style={S.langBtn}>{l.label}</button>
            ))}
          </div>
        </div>

        <div style={S.sidebarSection}>
          <div style={S.sLabel}>Location</div>
          <button onClick={getLocation} style={S.locBtn}>
            {locLoading ? "Fetching…" : location ? `📍 ${location.lat.toFixed(2)}, ${location.lon.toFixed(2)}` : "📍 Share my location"}
          </button>
        </div>

        <div style={S.sidebarSection}>
          <button onClick={newChat} style={S.newChatBtn}>+ New Chat</button>
        </div>

        <div style={{ padding:"0 14px", flex:1, overflowY:"auto" }}>
          <div style={{ ...S.sLabel, marginBottom:8 }}>Recent</div>
          {chatHistory.map(c=>(
            <div key={c.id} style={{ ...S.histItem, ...(c.active?S.histActive:{}) }}>💬 {c.title}</div>
          ))}
        </div>

        <div style={S.sidebarFoot}>
          {photo
            ? <img src={photo} alt="" style={{ width:32,height:32,borderRadius:"50%",border:"2px solid rgba(106,170,122,0.3)" }}/>
            : <div style={S.avatarFb}>{firstName[0]}</div>
          }
          <div style={{ flex:1, minWidth:0 }}>
            <div style={{ color:"#e8f0e4", fontWeight:700, fontSize:"0.85rem", overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{firstName}</div>
            <div style={{ color:"rgba(232,240,228,0.38)", fontSize:"0.73rem", overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{user?.email||""}</div>
          </div>
          <button style={{ ...S.iBtn, color:"#f87171" }} onClick={onSignOut} title="Sign out">🚪</button>
        </div>
      </aside>

      {sidebarOpen && <div style={S.overlay} onClick={()=>setSidebarOpen(false)}/>}

      {/* Main */}
      <div style={S.main}>

        {/* Header */}
        <header style={S.header}>
          <div style={{ display:"flex", alignItems:"center", gap:12 }}>
            <button style={S.iBtn} onClick={()=>setSidebarOpen(true)}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/>
              </svg>
            </button>
            <span style={{ fontFamily:"'Sora',sans-serif", fontWeight:800, color:"#b5d6a0" }}>🌾 KrishiBot</span>
            <span style={S.onlineDot}/>
          </div>
          <div style={{ display:"flex", alignItems:"center", gap:8 }}>
            <div style={{ display:"flex", gap:5 }} className="krishi-lang-desktop">
              {LANG_OPTIONS.map(l=>(
                <button type="button" key={l.code}
                  className={`krishi-lang-btn${lang===l.code?" active":""}`}
                  onClick={()=>setLang(l.code)}
                  style={S.langBtn}>{l.label}</button>
              ))}
            </div>
            {onBack && <button style={S.backBtn} onClick={onBack}>← Home</button>}
            {photo
              ? <img src={photo} alt="" style={{ width:32,height:32,borderRadius:"50%",border:"2px solid rgba(106,170,122,0.3)",cursor:"pointer" }} onClick={onSignOut} title="Sign out"/>
              : <div style={S.avatarFb} onClick={onSignOut} title="Sign out">{firstName[0]}</div>
            }
          </div>
        </header>

        {/* Messages */}
        <div style={S.msgs}>
          {messages.length === 0 ? (
            <div style={S.empty}>
              <div style={{ fontSize:"3.2rem", marginBottom:10 }}>🌾</div>
              <h2 style={{ fontFamily:"'Sora',sans-serif", fontSize:"1.45rem", fontWeight:800, color:"#b5d6a0", margin:"0 0 8px" }}>
                Namaste, {firstName}!
              </h2>
              <p style={{ color:"rgba(232,240,228,0.42)", fontSize:"0.88rem", maxWidth:320, lineHeight:1.65, margin:"0 0 26px", textAlign:"center" }}>
                Ask me anything about farming — in English, Hindi or Kannada.
              </p>
              <div style={{ display:"flex", flexWrap:"wrap", gap:8, justifyContent:"center", maxWidth:520 }}>
                {SUGGESTIONS.map((s,i)=>(
                  <button key={i} style={S.suggChip} onClick={()=>{ setInput(s.text); textareaRef.current?.focus(); }}>
                    {s.icon} {s.text}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map(m=><Message key={m.id} msg={m}/>)}
              {loading && <TypingIndicator/>}
            </>
          )}
          <div ref={endRef}/>
        </div>

        {/* Input */}
        <div style={S.inputWrap}>
          {imagePreview && (
            <div style={S.imgPreviewBar}>
              <img src={imagePreview} alt="" style={{ width:52,height:52,objectFit:"cover",borderRadius:9,border:"1px solid rgba(106,170,122,0.25)" }}/>
              <span style={{ color:"rgba(232,240,228,0.55)", fontSize:"0.8rem" }}>Image ready to send</span>
              <button style={{ ...S.iBtn, marginLeft:"auto" }} onClick={()=>{ setImagePreview(null); setImageFile(null); }}>✕</button>
            </div>
          )}
          <div style={S.inputBar}>
            <input ref={fileRef} type="file" accept="image/*" style={{ display:"none" }} onChange={handleImage}/>
            <button style={{ ...S.iBtn, color: imageFile ? "#6aaa7a" : "rgba(232,240,228,0.3)" }}
              onClick={()=>fileRef.current?.click()} title="Upload crop photo">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>
              </svg>
            </button>
            <button style={{ ...S.iBtn, color: location ? "#6aaa7a" : "rgba(232,240,228,0.3)" }}
              onClick={getLocation} title={location?"Location active":"Share location for weather"}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
              </svg>
            </button>
            <textarea
              ref={textareaRef}
              value={input}
              onChange={e=>setInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder={listening ? "🎙 Listening…" : "Ask in English, Hindi or Kannada…"}
              rows={1}
              style={{ ...S.textarea, ...(listening ? { color:"#6aaa7a" } : {}) }}
              onInput={e=>{ e.target.style.height="auto"; e.target.style.height=Math.min(e.target.scrollHeight,120)+"px"; }}
            />
            {/* Mic button — always visible */}
            <button type="button"
              style={{ ...S.iBtn, color: listening ? "#f87171" : SpeechAPI ? "rgba(232,240,228,0.3)" : "rgba(232,240,228,0.15)", position:"relative" }}
              onClick={toggleVoice}
              title={!SpeechAPI ? "Voice not supported — use Chrome" : listening ? "Stop listening" : "Speak your question"}>
              {listening
                ? <svg width="18" height="18" viewBox="0 0 24 24" fill="#f87171" stroke="#f87171" strokeWidth="1"><rect x="9" y="9" width="6" height="6" rx="1"/><path fill="none" strokeWidth="2" d="M12 1a3 3 0 0 1 3 3v4a3 3 0 0 1-6 0V4a3 3 0 0 1 3-3z"/><path fill="none" strokeWidth="2" d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>
                : <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 1a3 3 0 0 1 3 3v4a3 3 0 0 1-6 0V4a3 3 0 0 1 3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>
              }
              {listening && <span style={S.micPulse}/>}
            </button>
            <button style={{ ...S.sendBtn, opacity:(input.trim()||imageFile)&&!loading?1:0.4 }}
              onClick={handleSend} disabled={loading||(!input.trim()&&!imageFile)} className="krishi-send">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
              </svg>
            </button>
          </div>
          <div style={S.hint}>
            Enter to send · Shift+Enter new line
            {location && <span style={{ color:"#6aaa7a" }}> · 📍 Location active</span>}
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Design tokens ──────────────────────────────────────────────────────────

const S = {
  root:       { minHeight:"100vh", height:"100dvh", background:"#0e1510", fontFamily:"'Nunito',sans-serif", color:"#e8f0e4", display:"flex", overflow:"hidden" },
  sidebar:    { position:"fixed", left:0, top:0, bottom:0, width:256, background:"#111910", borderRight:"1px solid rgba(106,170,122,0.12)", display:"flex", flexDirection:"column", zIndex:200, transition:"transform 0.27s cubic-bezier(0.4,0,0.2,1)" },
  sidebarHead:{ display:"flex", alignItems:"center", justifyContent:"space-between", padding:"18px 16px 14px", borderBottom:"1px solid rgba(106,170,122,0.1)" },
  sidebarSection:{ padding:"14px 16px 0" },
  sidebarFoot:{ display:"flex", alignItems:"center", gap:10, padding:"14px 16px", borderTop:"1px solid rgba(106,170,122,0.1)" },
  overlay:    { position:"fixed", inset:0, background:"rgba(0,0,0,0.55)", zIndex:199, backdropFilter:"blur(2px)" },
  main:       { flex:1, display:"flex", flexDirection:"column", height:"100dvh", minWidth:0 },
  header:     { display:"flex", alignItems:"center", justifyContent:"space-between", padding:"13px 20px", background:"rgba(13,20,11,0.92)", borderBottom:"1px solid rgba(106,170,122,0.1)", backdropFilter:"blur(16px)", flexShrink:0, zIndex:10 },
  onlineDot:  { width:7, height:7, borderRadius:"50%", background:"#4ade80", boxShadow:"0 0 6px rgba(74,222,128,0.7)", display:"inline-block", marginLeft:2 },
  msgs:       { flex:1, overflowY:"auto", padding:"22px 20px", display:"flex", flexDirection:"column", scrollbarWidth:"thin", scrollbarColor:"rgba(106,170,122,0.18) transparent" },
  empty:      { flex:1, display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center", minHeight:"60vh", padding:"32px 12px" },
  suggChip:   { display:"inline-flex", alignItems:"center", gap:6, padding:"8px 15px", background:"rgba(106,170,122,0.07)", border:"1px solid rgba(106,170,122,0.18)", borderRadius:50, color:"rgba(232,240,228,0.65)", fontSize:"0.81rem", fontWeight:600, cursor:"pointer", fontFamily:"'Nunito',sans-serif", transition:"all 0.15s" },
  botAvatar:  { width:30, height:30, borderRadius:"50%", background:"rgba(74,124,89,0.28)", border:"1px solid rgba(106,170,122,0.22)", display:"flex", alignItems:"center", justifyContent:"center", fontSize:"0.85rem", flexShrink:0 },
  botBubble:  { background:"rgba(255,255,255,0.04)", border:"1px solid rgba(106,170,122,0.13)", borderRadius:"18px 18px 18px 4px", padding:"11px 15px", fontSize:"0.9rem", lineHeight:1.65, color:"#e8f0e4", maxWidth:"100%", whiteSpace:"pre-wrap", wordBreak:"break-word" },
  userBubble: { background:"linear-gradient(135deg,#3a6b47,#4a7c59)", borderRadius:"18px 18px 4px 18px", padding:"11px 15px", fontSize:"0.9rem", lineHeight:1.65, color:"#e8f0e4", maxWidth:"100%", whiteSpace:"pre-wrap", wordBreak:"break-word", boxShadow:"0 4px 14px rgba(74,124,89,0.22)" },
  timestamp:  { fontSize:"0.67rem", color:"rgba(232,240,228,0.22)", marginTop:2 },
  infoCard:   { background:"rgba(106,170,122,0.06)", border:"1px solid rgba(106,170,122,0.17)", borderRadius:13, padding:"13px 15px", marginTop:4, maxWidth:310 },
  cardLabel:  { fontWeight:700, color:"#b5d6a0", fontSize:"0.82rem", display:"flex", alignItems:"center", gap:5 },
  metaStat:   { display:"flex", alignItems:"center", gap:4, color:"rgba(232,240,228,0.5)", fontSize:"0.78rem", fontWeight:600 },
  chip:       { padding:"4px 11px", background:"rgba(106,170,122,0.12)", border:"1px solid rgba(106,170,122,0.2)", borderRadius:50, color:"#b5d6a0", fontSize:"0.79rem", fontWeight:700 },
  npkBox:     { flex:1, background:"rgba(106,170,122,0.08)", borderRadius:9, padding:"9px 8px", textAlign:"center", border:"1px solid rgba(106,170,122,0.14)" },
  inputWrap:  { padding:"11px 16px 15px", borderTop:"1px solid rgba(106,170,122,0.1)", background:"rgba(13,20,11,0.96)", flexShrink:0 },
  imgPreviewBar:{ display:"flex", alignItems:"center", gap:10, padding:"8px 11px", background:"rgba(106,170,122,0.07)", border:"1px solid rgba(106,170,122,0.17)", borderRadius:11, marginBottom:9 },
  inputBar:   { display:"flex", alignItems:"flex-end", gap:7, background:"rgba(255,255,255,0.04)", border:"1px solid rgba(106,170,122,0.17)", borderRadius:18, padding:"7px 9px 7px 11px" },
  textarea:   { flex:1, background:"none", border:"none", outline:"none", color:"#e8f0e4", fontFamily:"'Nunito',sans-serif", fontSize:"0.91rem", lineHeight:1.55, resize:"none", minHeight:22, maxHeight:120, paddingTop:3, scrollbarWidth:"none" },
  sendBtn:    { width:34, height:34, borderRadius:"50%", background:"linear-gradient(135deg,#4a7c59,#6aaa7a)", border:"none", cursor:"pointer", display:"flex", alignItems:"center", justifyContent:"center", color:"#fff", flexShrink:0, transition:"opacity 0.15s,transform 0.15s", boxShadow:"0 3px 12px rgba(74,124,89,0.38)" },
  hint:       { fontSize:"0.69rem", color:"rgba(232,240,228,0.2)", textAlign:"center", marginTop:7, fontWeight:600 },
  iBtn:       { background:"none", border:"none", cursor:"pointer", color:"rgba(232,240,228,0.45)", padding:6, borderRadius:8, display:"flex", alignItems:"center", justifyContent:"center", transition:"color 0.14s", fontFamily:"inherit", fontSize:"0.84rem" },
  backBtn:    { background:"none", border:"1px solid rgba(106,170,122,0.2)", color:"rgba(232,240,228,0.45)", fontSize:"0.79rem", fontWeight:700, borderRadius:50, padding:"4px 13px", cursor:"pointer", fontFamily:"'Nunito',sans-serif" },
  langBtn:    { background:"rgba(255,255,255,0.04)", border:"1px solid rgba(106,170,122,0.15)", color:"rgba(232,240,228,0.45)", fontSize:"0.74rem", fontWeight:800, borderRadius:7, padding:"3px 9px", cursor:"pointer", fontFamily:"'Nunito',sans-serif", letterSpacing:"0.05em" },
  langActive: { background:"rgba(106,170,122,0.18)", border:"1px solid rgba(106,170,122,0.42)", color:"#b5d6a0" },
  sLabel:     { fontSize:"0.69rem", fontWeight:800, color:"rgba(232,240,228,0.28)", letterSpacing:"0.1em", textTransform:"uppercase" },
  locBtn:     { marginTop:8, width:"100%", background:"rgba(106,170,122,0.07)", border:"1px solid rgba(106,170,122,0.17)", color:"rgba(232,240,228,0.55)", fontSize:"0.81rem", fontWeight:700, borderRadius:9, padding:"8px 13px", cursor:"pointer", fontFamily:"'Nunito',sans-serif", textAlign:"left" },
  newChatBtn: { width:"100%", background:"linear-gradient(135deg,rgba(74,124,89,0.32),rgba(106,170,122,0.18))", border:"1px solid rgba(106,170,122,0.28)", color:"#b5d6a0", fontSize:"0.84rem", fontWeight:800, borderRadius:11, padding:"9px 13px", cursor:"pointer", fontFamily:"'Nunito',sans-serif", display:"flex", alignItems:"center", gap:7 },
  histItem:   { padding:"8px 11px", borderRadius:9, color:"rgba(232,240,228,0.4)", fontSize:"0.81rem", fontWeight:600, cursor:"pointer", marginTop:4, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" },
  histActive: { background:"rgba(106,170,122,0.1)", color:"#b5d6a0" },
  micPulse:   { position:"absolute", inset:0, borderRadius:"50%", border:"2px solid #f87171", animation:"krishiMicPulse 1s ease-out infinite", pointerEvents:"none" },
  avatarFb:   { width:32, height:32, borderRadius:"50%", background:"linear-gradient(135deg,#3a6b47,#6aaa7a)", display:"flex", alignItems:"center", justifyContent:"center", color:"#fff", fontWeight:800, fontSize:"0.84rem", cursor:"pointer", flexShrink:0 },
};

const CSS = `
  @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Sora:wght@700;800&display=swap');
  * { box-sizing: border-box; margin: 0; padding: 0; }

  @keyframes krishiDot {
    0%,80%,100% { transform:translateY(0); opacity:0.35; }
    40%          { transform:translateY(-6px); opacity:1; }
  }
  @keyframes krishiMicPulse {
    0%   { opacity:0.8; transform:scale(1); }
    100% { opacity:0;   transform:scale(1.9); }
  }

  .krishi-dots { display:flex; gap:5px; align-items:center; height:16px; }
  .krishi-dots span { display:inline-block; width:7px; height:7px; border-radius:50%; background:rgba(106,170,122,0.75); animation:krishiDot 1.2s ease-in-out infinite; }
  .krishi-dots span:nth-child(2) { animation-delay:0.18s; }
  .krishi-dots span:nth-child(3) { animation-delay:0.36s; }

  .krishi-send:hover:not(:disabled) { transform:scale(1.1) !important; opacity:1 !important; }

  /* lang buttons — active state must win over hover */
  .krishi-lang-btn { transition: background 0.15s, border-color 0.15s, color 0.15s; }
  .krishi-lang-btn:hover { opacity:1 !important; background:rgba(106,170,122,0.1); }
  .krishi-lang-btn.active {
    background: rgba(106,170,122,0.22) !important;
    border-color: rgba(106,170,122,0.55) !important;
    color: #b5d6a0 !important;
    box-shadow: 0 0 0 1px rgba(106,170,122,0.3);
  }

  textarea::placeholder { color:rgba(232,240,228,0.26); }
  textarea::-webkit-scrollbar { display:none; }
  ::-webkit-scrollbar { width:4px; }
  ::-webkit-scrollbar-thumb { background:rgba(106,170,122,0.18); border-radius:4px; }
  ::-webkit-scrollbar-track { background:transparent; }

  .krishi-lang-desktop { display:flex; }
  @media (max-width:480px) { .krishi-lang-desktop { display:none; } }
`;
