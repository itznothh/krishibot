import { useState } from "react";
import Sidebar from "./Sidebar";

const BACKEND = "https://krishibot-api.onrender.com";

const STATES = [
  "Andhra Pradesh","Bihar","Delhi","Gujarat","Haryana","Himachal Pradesh",
  "Karnataka","Kerala","Madhya Pradesh","Maharashtra","Odisha","Punjab",
  "Rajasthan","Tamil Nadu","Telangana","Uttar Pradesh","Uttarakhand","West Bengal"
];

const CROPS = [
  "Wheat","Rice","Maize","Cotton","Sugarcane","Soybean","Mustard","Groundnut",
  "Tomato","Onion","Potato","Chilli","Banana","Mango","Grapes","Chickpea",
  "Lentil","Moong","Jowar","Bajra","Turmeric","Ginger","Sunflower","Other"
];

const LAND_SIZES = ["Less than 1 acre","1–2 acres","2–5 acres","5–10 acres","More than 10 acres"];

const QUICK_QUESTIONS = [
  "Tell me about PM-KISAN scheme",
  "How to apply for crop insurance (PMFBY)?",
  "What is Kisan Credit Card?",
  "Soil Health Card scheme details",
  "PM Fasal Bima Yojana eligibility",
  "How to get agricultural loan?",
];

export default function Schemes({ user, onSignOut, onChatClick }) {
  const [state, setState] = useState("Karnataka");
  const [crop, setCrop] = useState("Wheat");
  const [landSize, setLandSize] = useState("1–2 acres");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("schemes"); // schemes | loans | insurance
  const [question, setQuestion] = useState("");
  const [chatResult, setChatResult] = useState(null);
  const [chatLoading, setChatLoading] = useState(false);

  async function fetchSchemes() {
    setLoading(true);
    setResult(null);
    try {
      const prompt = `You are KrishiBot, an expert on Indian government agricultural schemes.
A farmer from ${state} grows ${crop} on ${landSize} of land.

List ALL relevant government schemes, subsidies, and benefits they qualify for. Include:
1. **PM-KISAN** — eligibility & amount
2. **PMFBY (Crop Insurance)** — premium %, coverage, how to apply
3. **Kisan Credit Card** — loan limit, interest rate
4. **State-specific schemes for ${state}**
5. **Soil Health Card scheme**
6. Any other relevant central/state schemes for ${crop} farmers

For each scheme include:
- What it is (1 line)
- Benefit amount / subsidy %
- How to apply (portal or office)
- Key eligibility criteria

Format as clean sections. Be specific with numbers. End with: "📞 Kisan Call Center: 1800-180-1551 (Free, 24x7)"`;

      const res = await fetch(`${BACKEND}/schemes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt })
      });
      const data = await res.json();
      const text = data.result || "Could not load schemes. Please try again.";
      setResult(text);
    } catch {
      setResult("⚠️ Failed to load schemes. Please check your connection and try again.");
    }
    setLoading(false);
  }

  async function askQuestion(q) {
    const query = q || question;
    if (!query.trim()) return;
    setChatLoading(true);
    setChatResult(null);
    try {
      const prompt = `You are KrishiBot, an expert on Indian agricultural schemes, loans, and insurance.
Answer this farmer's question clearly and helpfully: "${query}"
Include specific numbers, amounts, eligibility, and how to apply where relevant.
Keep it concise but complete. End with a helpful tip or next step.`;

      const res = await fetch(`${BACKEND}/schemes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt })
      });
      const data = await res.json();
      const text = data.result || "Could not answer. Please try again.";
      setChatResult(text);
    } catch {
      setChatResult("⚠️ Failed to get answer. Please try again.");
    }
    setChatLoading(false);
    setQuestion("");
  }

  function renderMarkdown(text) {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong style="color:#b5d6a0">$1</strong>')
      .replace(/^### (.*)/gm, '<h3 style="color:#6aaa7a;font-size:1rem;margin:20px 0 8px;font-family:Sora,sans-serif">$1</h3>')
      .replace(/^## (.*)/gm, '<h2 style="color:#8fbc8f;font-size:1.1rem;margin:24px 0 10px;font-family:Sora,sans-serif">$1</h2>')
      .replace(/^- (.*)/gm, '<div style="display:flex;gap:8px;margin:4px 0"><span style="color:#6aaa7a">•</span><span>$1</span></div>')
      .replace(/\n\n/g, '<br/><br/>')
      .replace(/\n/g, '<br/>');
  }

  return (
    <div style={{ minHeight: "100vh", background: "#0e1510", fontFamily: "'Nunito', sans-serif", color: "#e8f0e4", display: "flex" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Sora:wght@700;800&display=swap');
        * { box-sizing: border-box; }
        .sidebar-content { flex: 1; margin-left: 220px; }
        select, input[type="text"] {
          background: rgba(255,255,255,0.05);
          border: 1px solid rgba(106,170,122,0.2);
          border-radius: 10px;
          padding: 10px 12px;
          color: #e8f0e4;
          font-family: 'Nunito', sans-serif;
          font-size: 0.9rem;
          outline: none;
          width: 100%;
          transition: border-color 0.15s;
        }
        select:focus, input:focus { border-color: rgba(106,170,122,0.5); }
        select option { background: #1c2419; color: #e8f0e4; }
        .find-btn { padding: 11px 28px; background: linear-gradient(135deg,#4a7c59,#6aaa7a); color: #fff; border: none; border-radius: 12px; font-family: 'Nunito',sans-serif; font-weight: 800; font-size: 0.95rem; cursor: pointer; transition: all 0.18s; }
        .find-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(74,124,89,0.4); }
        .find-btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .tab-btn { padding: 9px 22px; border-radius: 50px; font-family: 'Nunito',sans-serif; font-weight: 700; font-size: 0.88rem; cursor: pointer; transition: all 0.15s; border: 1px solid rgba(106,170,122,0.2); }
        .tab-btn.active { background: linear-gradient(135deg,#4a7c59,#6aaa7a); color: #fff; border-color: transparent; }
        .tab-btn.inactive { background: rgba(255,255,255,0.03); color: rgba(232,240,228,0.55); }
        .quick-chip { padding: 8px 16px; background: rgba(106,170,122,0.07); border: 1px solid rgba(106,170,122,0.18); border-radius: 50px; font-size: 0.82rem; font-weight: 600; color: #8fbc8f; cursor: pointer; transition: all 0.15s; white-space: nowrap; }
        .quick-chip:hover { background: rgba(106,170,122,0.15); color: #b5d6a0; transform: translateY(-1px); }
        .result-box { background: rgba(255,255,255,0.02); border: 1px solid rgba(106,170,122,0.12); border-radius: 18px; padding: 28px; line-height: 1.7; font-size: 0.92rem; color: rgba(232,240,228,0.85); }
        .ask-input-row { display: flex; gap: 10px; }
        .ask-input-row input { flex: 1; }
        .ask-btn { padding: 10px 20px; background: rgba(106,170,122,0.12); border: 1px solid rgba(106,170,122,0.25); border-radius: 10px; color: #8fbc8f; font-family: 'Nunito',sans-serif; font-weight: 700; font-size: 0.88rem; cursor: pointer; white-space: nowrap; transition: all 0.15s; }
        .ask-btn:hover { background: rgba(106,170,122,0.2); color: #b5d6a0; }
        @keyframes spin { from{transform:rotate(0deg);} to{transform:rotate(360deg);} }
        @keyframes fadeUp { from{opacity:0;transform:translateY(16px);} to{opacity:1;transform:translateY(0);} }
        .fade-up { animation: fadeUp 0.4s ease forwards; }
        @media (max-width: 700px) { .sidebar-content { margin-left: 0; margin-top: 60px; } }
      `}</style>

      <Sidebar user={user} onSignOut={onSignOut} onChatClick={onChatClick} />

      <div className="sidebar-content">
        <header style={{ background: "rgba(14,21,16,0.9)", backdropFilter: "blur(20px)", borderBottom: "1px solid rgba(106,170,122,0.12)", padding: "16px 5%", position: "sticky", top: 0, zIndex: 50, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: "1.3rem" }}>📋</span>
            <span style={{ fontFamily: "'Sora', sans-serif", fontWeight: 700, fontSize: "1.05rem", color: "#e8f0e4" }}>Schemes & Loans</span>
            <span style={{ fontSize: "0.75rem", background: "rgba(106,170,122,0.15)", border: "1px solid rgba(106,170,122,0.25)", borderRadius: 20, padding: "3px 10px", color: "#8fbc8f", fontWeight: 700 }}>AI Powered</span>
          </div>
          {user && (
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              {user.photoURL && <img src={user.photoURL} style={{ width: 28, height: 28, borderRadius: "50%" }} alt="" />}
              <span style={{ fontSize: "0.85rem", color: "rgba(232,240,228,0.5)", fontWeight: 600 }}>{user.displayName?.split(" ")[0]}</span>
            </div>
          )}
        </header>

        <div style={{ maxWidth: 860, margin: "0 auto", padding: "32px 5% 60px" }}>

          {/* Tabs */}
          <div style={{ display: "flex", gap: 8, marginBottom: 28, flexWrap: "wrap" }}>
            {[["schemes","📋 Govt Schemes"],["loans","💰 Loans & KCC"],["insurance","🛡️ Crop Insurance"]].map(([id, label]) => (
              <button key={id} className={`tab-btn ${activeTab === id ? "active" : "inactive"}`} onClick={() => setActiveTab(id)}>{label}</button>
            ))}
          </div>

          {/* Finder card */}
          <div style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(106,170,122,0.12)", borderRadius: 20, padding: "24px", marginBottom: 28 }}>
            <h2 style={{ fontFamily: "'Sora',sans-serif", fontSize: "1.1rem", fontWeight: 700, color: "#e8f0e4", marginBottom: 6 }}>
              {activeTab === "schemes" ? "🔍 Find schemes for your farm" : activeTab === "loans" ? "💰 Find loan options for you" : "🛡️ Find insurance for your crop"}
            </h2>
            <p style={{ color: "rgba(232,240,228,0.4)", fontSize: "0.85rem", marginBottom: 20 }}>
              Enter your details to get personalised {activeTab === "schemes" ? "government schemes" : activeTab === "loans" ? "loan & KCC options" : "crop insurance plans"}
            </p>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 12, marginBottom: 16 }}>
              <div>
                <p style={{ fontSize: "0.78rem", color: "rgba(232,240,228,0.45)", margin: "0 0 6px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em" }}>Your State</p>
                <select value={state} onChange={e => setState(e.target.value)}>
                  {STATES.map(s => <option key={s}>{s}</option>)}
                </select>
              </div>
              <div>
                <p style={{ fontSize: "0.78rem", color: "rgba(232,240,228,0.45)", margin: "0 0 6px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em" }}>Main Crop</p>
                <select value={crop} onChange={e => setCrop(e.target.value)}>
                  {CROPS.map(c => <option key={c}>{c}</option>)}
                </select>
              </div>
              <div>
                <p style={{ fontSize: "0.78rem", color: "rgba(232,240,228,0.45)", margin: "0 0 6px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em" }}>Land Size</p>
                <select value={landSize} onChange={e => setLandSize(e.target.value)}>
                  {LAND_SIZES.map(l => <option key={l}>{l}</option>)}
                </select>
              </div>
            </div>
            <button className="find-btn" onClick={fetchSchemes} disabled={loading}>
              {loading ? "⟳ Finding schemes…" : `Find ${activeTab === "schemes" ? "Schemes" : activeTab === "loans" ? "Loan Options" : "Insurance Plans"} →`}
            </button>
          </div>

          {/* Result */}
          {loading && (
            <div style={{ textAlign: "center", padding: "48px 0", color: "rgba(232,240,228,0.4)" }}>
              <div style={{ fontSize: "2rem", animation: "spin 1.2s linear infinite", display: "inline-block", marginBottom: 12 }}>⟳</div>
              <p style={{ fontWeight: 600 }}>Searching government databases…</p>
            </div>
          )}
          {!loading && result && (
            <div className="result-box fade-up" style={{ marginBottom: 28 }}>
              <div dangerouslySetInnerHTML={{ __html: renderMarkdown(result) }} />
            </div>
          )}

          {/* Quick Questions */}
          <div style={{ marginBottom: 24 }}>
            <p style={{ fontSize: "0.82rem", color: "rgba(232,240,228,0.4)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 12 }}>Quick Questions</p>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              {QUICK_QUESTIONS.map(q => (
                <button key={q} className="quick-chip" onClick={() => askQuestion(q)}>{q}</button>
              ))}
            </div>
          </div>

          {/* Ask anything */}
          <div style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(106,170,122,0.12)", borderRadius: 18, padding: "20px 24px" }}>
            <p style={{ fontSize: "0.88rem", fontWeight: 700, color: "rgba(232,240,228,0.6)", marginBottom: 12 }}>💬 Ask anything about schemes, loans, or insurance</p>
            <div className="ask-input-row">
              <input
                type="text"
                placeholder="e.g. How to claim PMFBY insurance after crop loss?"
                value={question}
                onChange={e => setQuestion(e.target.value)}
                onKeyDown={e => e.key === "Enter" && askQuestion()}
              />
              <button className="ask-btn" onClick={() => askQuestion()} disabled={chatLoading}>
                {chatLoading ? "⟳" : "Ask →"}
              </button>
            </div>
            {chatLoading && (
              <div style={{ marginTop: 16, color: "rgba(232,240,228,0.4)", fontSize: "0.88rem" }}>
                <span style={{ display: "inline-block", animation: "spin 1s linear infinite" }}>⟳</span> Getting answer…
              </div>
            )}
            {!chatLoading && chatResult && (
              <div className="fade-up" style={{ marginTop: 16, padding: "16px", background: "rgba(106,170,122,0.05)", borderRadius: 12, lineHeight: 1.7, fontSize: "0.9rem", color: "rgba(232,240,228,0.85)" }}>
                <div dangerouslySetInnerHTML={{ __html: renderMarkdown(chatResult) }} />
              </div>
            )}
          </div>

          {/* Helpline footer */}
          <div style={{ marginTop: 32, padding: "16px 20px", background: "rgba(106,170,122,0.05)", border: "1px solid rgba(106,170,122,0.12)", borderRadius: 14, display: "flex", alignItems: "center", gap: 12 }}>
            <span style={{ fontSize: "1.5rem" }}>📞</span>
            <div>
              <p style={{ margin: 0, fontWeight: 700, fontSize: "0.9rem", color: "#b5d6a0" }}>Kisan Call Center: 1800-180-1551</p>
              <p style={{ margin: 0, fontSize: "0.8rem", color: "rgba(232,240,228,0.4)" }}>Free helpline, available 24x7 in all regional languages</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
