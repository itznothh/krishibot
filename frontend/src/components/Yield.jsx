import { useState } from "react";
import Sidebar from "./Sidebar";

const BACKEND = "https://krishibot-api.onrender.com";

const CROPS = [
  { name: "Wheat",      yieldPerAcre: 16,  unit: "quintal" },
  { name: "Rice",       yieldPerAcre: 20,  unit: "quintal" },
  { name: "Maize",      yieldPerAcre: 18,  unit: "quintal" },
  { name: "Cotton",     yieldPerAcre: 8,   unit: "quintal" },
  { name: "Sugarcane",  yieldPerAcre: 280, unit: "quintal" },
  { name: "Soybean",    yieldPerAcre: 10,  unit: "quintal" },
  { name: "Mustard",    yieldPerAcre: 8,   unit: "quintal" },
  { name: "Groundnut",  yieldPerAcre: 12,  unit: "quintal" },
  { name: "Tomato",     yieldPerAcre: 100, unit: "quintal" },
  { name: "Onion",      yieldPerAcre: 80,  unit: "quintal" },
  { name: "Potato",     yieldPerAcre: 100, unit: "quintal" },
  { name: "Chickpea",   yieldPerAcre: 7,   unit: "quintal" },
  { name: "Lentil",     yieldPerAcre: 6,   unit: "quintal" },
  { name: "Bajra",      yieldPerAcre: 10,  unit: "quintal" },
  { name: "Jowar",      yieldPerAcre: 10,  unit: "quintal" },
  { name: "Sunflower",  yieldPerAcre: 8,   unit: "quintal" },
  { name: "Turmeric",   yieldPerAcre: 25,  unit: "quintal" },
  { name: "Ginger",     yieldPerAcre: 40,  unit: "quintal" },
];

// Approximate MSP / market prices in ₹ per quintal
const CROP_PRICES = {
  Wheat: 2275, Rice: 2300, Maize: 2090, Cotton: 6620, Sugarcane: 315,
  Soybean: 4600, Mustard: 5650, Groundnut: 6377, Tomato: 1200, Onion: 800,
  Potato: 700, Chickpea: 5440, Lentil: 6000, Bajra: 2500, Jowar: 3180,
  Sunflower: 6760, Turmeric: 7000, Ginger: 5000,
};

const LAND_OPTIONS = [
  { label: "0.5 acres", value: 0.5 },
  { label: "1 acre",    value: 1 },
  { label: "2 acres",   value: 2 },
  { label: "3 acres",   value: 3 },
  { label: "5 acres",   value: 5 },
  { label: "7 acres",   value: 7 },
  { label: "10 acres",  value: 10 },
  { label: "15 acres",  value: 15 },
  { label: "20 acres",  value: 20 },
];

const SEASON_MULTIPLIER = { Kharif: 1.0, Rabi: 0.95, Zaid: 0.85 };

const CATEGORIES = ["All", "Grains", "Vegetables", "Pulses", "Oilseeds", "Cash Crops"];

const MANDI_DATA = [
  { commodity:"Wheat",     category:"Grains",     min:2100, modal:2275, max:2400, trend:"up" },
  { commodity:"Rice",      category:"Grains",     min:2100, modal:2300, max:2500, trend:"stable" },
  { commodity:"Maize",     category:"Grains",     min:1900, modal:2090, max:2200, trend:"down" },
  { commodity:"Bajra",     category:"Grains",     min:2200, modal:2500, max:2700, trend:"up" },
  { commodity:"Jowar",     category:"Grains",     min:2900, modal:3180, max:3400, trend:"stable" },
  { commodity:"Tomato",    category:"Vegetables", min:800,  modal:1200, max:2000, trend:"up" },
  { commodity:"Onion",     category:"Vegetables", min:600,  modal:800,  max:1100, trend:"down" },
  { commodity:"Potato",    category:"Vegetables", min:500,  modal:700,  max:900,  trend:"stable" },
  { commodity:"Chickpea",  category:"Pulses",     min:5000, modal:5440, max:5800, trend:"up" },
  { commodity:"Lentil",    category:"Pulses",     min:5500, modal:6000, max:6400, trend:"stable" },
  { commodity:"Mustard",   category:"Oilseeds",   min:5200, modal:5650, max:6000, trend:"up" },
  { commodity:"Soybean",   category:"Oilseeds",   min:4200, modal:4600, max:4900, trend:"stable" },
  { commodity:"Groundnut", category:"Oilseeds",   min:5900, modal:6377, max:6800, trend:"up" },
  { commodity:"Sunflower", category:"Oilseeds",   min:6200, modal:6760, max:7100, trend:"up" },
  { commodity:"Sugarcane", category:"Cash Crops", min:290,  modal:315,  max:340,  trend:"stable" },
  { commodity:"Cotton",    category:"Cash Crops", min:6000, modal:6620, max:7200, trend:"up" },
  { commodity:"Turmeric",  category:"Cash Crops", min:6000, modal:7000, max:8500, trend:"up" },
  { commodity:"Ginger",    category:"Cash Crops", min:4000, modal:5000, max:6500, trend:"stable" },
];

export default function Yield({ user, onSignOut, onChatClick }) {
  const [crop, setCrop]       = useState("Wheat");
  const [land, setLand]       = useState(2);
  const [season, setSeason]   = useState("Rabi");
  const [price, setPrice]     = useState(CROP_PRICES["Wheat"]);
  const [customPrice, setCustomPrice] = useState(false);
  const [result, setResult]   = useState(null);
  const [activeCategory, setActiveCategory] = useState("All");
  const [search, setSearch] = useState("");
  const [aiTips, setAiTips]   = useState(null);
  const [loading, setLoading] = useState(false);

  const selectedCrop = CROPS.find(c => c.name === crop);

  function handleCropChange(newCrop) {
    setCrop(newCrop);
    if (!customPrice) setPrice(CROP_PRICES[newCrop] || 2000);
  }

  function calculate() {
    const mult = SEASON_MULTIPLIER[season] || 1;
    const yieldTotal = selectedCrop.yieldPerAcre * land * mult;
    const revenue = yieldTotal * price;
    // Rough cost estimates per acre per crop type
    const costPerAcre = crop === "Sugarcane" ? 18000 : crop === "Cotton" ? 20000 :
      ["Tomato","Onion","Potato","Ginger","Turmeric"].includes(crop) ? 25000 : 12000;
    const totalCost = costPerAcre * land;
    const profit = revenue - totalCost;
    setResult({ yieldTotal, revenue, totalCost, profit, unit: selectedCrop.unit });
    fetchAiTips(yieldTotal, revenue, profit);
  }

  async function fetchAiTips(yieldTotal, revenue, profit) {
    setLoading(true);
    setAiTips(null);
    try {
      const prompt = `A farmer grows ${crop} on ${land} acres in ${season} season.
Expected yield: ${yieldTotal.toFixed(1)} quintals. Revenue: ₹${revenue.toLocaleString('en-IN')}. Profit: ₹${profit.toLocaleString('en-IN')}.

Give 3 short practical tips to maximize this yield and income. Format:
TIP: [One line tip]
WHY: [One line reason]
---
Keep each tip very short. Focus on ${crop} farming in India.`;

      const res = await fetch(`${BACKEND}/schemes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt })
      });
      const data = await res.json();
      setAiTips(data.result || null);
    } catch { setAiTips(null); }
    setLoading(false);
  }

  function renderTips(text) {
    if (!text) return null;
    const blocks = text.split(/\n(?=TIP:)/).map(b => b.trim()).filter(Boolean);
    return blocks.map((block, i) => {
      const lines = block.split('\n').filter(l => l.trim() && !l.startsWith('---'));
      const fields = {};
      lines.forEach(line => {
        const idx = line.indexOf(':');
        if (idx > -1) {
          fields[line.slice(0,idx).trim().toUpperCase()] = line.slice(idx+1).trim();
        }
      });
      return (
        <div key={i} style={{ display:"flex", gap:14, padding:"14px 18px", background:"rgba(106,170,122,0.05)", border:"1px solid rgba(106,170,122,0.12)", borderRadius:12, marginBottom:8 }}>
          <span style={{ fontSize:"1.3rem", flexShrink:0 }}>💡</span>
          <div>
            <div style={{ fontWeight:700, fontSize:"0.9rem", color:"#b5d6a0", marginBottom:3 }}>{fields['TIP'] || lines[0]}</div>
            {fields['WHY'] && <div style={{ fontSize:"0.82rem", color:"rgba(232,240,228,0.45)" }}>{fields['WHY']}</div>}
          </div>
        </div>
      );
    });
  }

  const fmt = (n) => `₹${Math.round(n).toLocaleString('en-IN')}`;

  return (
    <div style={{ minHeight:"100vh", background:"#0e1510", fontFamily:"'Nunito',sans-serif", color:"#e8f0e4", display:"flex" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Sora:wght@700;800&display=swap');
        * { box-sizing: border-box; }
        .sidebar-content { flex:1; margin-left:220px; }
        select, input[type="number"] { background:rgba(255,255,255,0.05); border:1px solid rgba(106,170,122,0.2); border-radius:10px; padding:10px 12px; color:#e8f0e4; font-family:'Nunito',sans-serif; font-size:0.9rem; outline:none; width:100%; transition:border-color 0.15s; }
        select:focus, input:focus { border-color:rgba(106,170,122,0.5); }
        select option { background:#1c2419; color:#e8f0e4; }
        .calc-btn { padding:13px 32px; background:linear-gradient(135deg,#4a7c59,#6aaa7a); color:#fff; border:none; border-radius:12px; font-family:'Nunito',sans-serif; font-weight:800; font-size:1rem; cursor:pointer; transition:all 0.18s; width:100%; }
        .calc-btn:hover { transform:translateY(-2px); box-shadow:0 8px 24px rgba(74,124,89,0.4); }
        .season-btn { padding:8px 20px; border-radius:50px; font-family:'Nunito',sans-serif; font-weight:700; font-size:0.85rem; cursor:pointer; transition:all 0.15s; border:1px solid rgba(106,170,122,0.2); }
        .season-btn.active { background:linear-gradient(135deg,#4a7c59,#6aaa7a); color:#fff; border-color:transparent; }
        .season-btn.inactive { background:rgba(255,255,255,0.03); color:rgba(232,240,228,0.55); }
        .metric-card { background:rgba(255,255,255,0.03); border:1px solid rgba(106,170,122,0.15); border-radius:16px; padding:20px 24px; text-align:center; }
        .metric-val { font-family:'Sora',sans-serif; font-size:1.6rem; font-weight:800; line-height:1.1; margin-bottom:4px; }
        .metric-label { font-size:0.78rem; color:rgba(232,240,228,0.4); font-weight:700; text-transform:uppercase; letter-spacing:0.06em; }
        @keyframes fadeUp { from{opacity:0;transform:translateY(16px);} to{opacity:1;transform:translateY(0);} }
        .fade-up { animation:fadeUp 0.4s ease forwards; }
        @keyframes spin { from{transform:rotate(0deg);} to{transform:rotate(360deg);} }
        @media (max-width:700px) { .sidebar-content { margin-left:0; margin-top:60px; } }
      `}</style>

      <Sidebar user={user} onSignOut={onSignOut} onChatClick={onChatClick} />

      <div className="sidebar-content">
        {/* Header */}
        <header style={{ background:"rgba(14,21,16,0.9)", backdropFilter:"blur(20px)", borderBottom:"1px solid rgba(106,170,122,0.12)", padding:"16px 5%", position:"sticky", top:0, zIndex:50, display:"flex", alignItems:"center", justifyContent:"space-between" }}>
          <div style={{ display:"flex", alignItems:"center", gap:8 }}>
            <span style={{ fontSize:"1.3rem" }}>📊</span>
            <span style={{ fontFamily:"'Sora',sans-serif", fontWeight:700, fontSize:"1.05rem", color:"#e8f0e4" }}>Yield Estimator</span>
            <span style={{ fontSize:"0.75rem", background:"rgba(106,170,122,0.15)", border:"1px solid rgba(106,170,122,0.25)", borderRadius:20, padding:"3px 10px", color:"#8fbc8f", fontWeight:700 }}>AI Powered</span>
          </div>
          {user && (
            <div style={{ display:"flex", alignItems:"center", gap:8 }}>
              {user.photoURL && <img src={user.photoURL} style={{ width:28, height:28, borderRadius:"50%" }} alt="" />}
              <span style={{ fontSize:"0.85rem", color:"rgba(232,240,228,0.5)", fontWeight:600 }}>{user.displayName?.split(" ")[0]}</span>
            </div>
          )}
        </header>

        <div style={{ maxWidth:860, margin:"0 auto", padding:"32px 5% 60px" }}>

          {/* Input card */}
          <div style={{ background:"rgba(255,255,255,0.02)", border:"1px solid rgba(106,170,122,0.12)", borderRadius:20, padding:"28px", marginBottom:24 }}>
            <h2 style={{ fontFamily:"'Sora',sans-serif", fontSize:"1.1rem", fontWeight:700, color:"#e8f0e4", marginBottom:4 }}>
              📊 Estimate your harvest income
            </h2>
            <p style={{ color:"rgba(232,240,228,0.4)", fontSize:"0.85rem", marginBottom:24 }}>
              Enter your crop details to get yield and income estimate
            </p>

            {/* Crop + Land */}
            <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit,minmax(160px,1fr))", gap:14, marginBottom:20 }}>
              <div>
                <p style={{ fontSize:"0.78rem", color:"rgba(232,240,228,0.45)", margin:"0 0 6px", fontWeight:700, textTransform:"uppercase", letterSpacing:"0.05em" }}>Crop</p>
                <select value={crop} onChange={e => handleCropChange(e.target.value)}>
                  {CROPS.map(c => <option key={c.name}>{c.name}</option>)}
                </select>
              </div>
              <div>
                <p style={{ fontSize:"0.78rem", color:"rgba(232,240,228,0.45)", margin:"0 0 6px", fontWeight:700, textTransform:"uppercase", letterSpacing:"0.05em" }}>Land Size</p>
                <select value={land} onChange={e => setLand(parseFloat(e.target.value))}>
                  {LAND_OPTIONS.map(l => <option key={l.value} value={l.value}>{l.label}</option>)}
                </select>
              </div>
              <div>
                <p style={{ fontSize:"0.78rem", color:"rgba(232,240,228,0.45)", margin:"0 0 6px", fontWeight:700, textTransform:"uppercase", letterSpacing:"0.05em" }}>Market Price (₹/quintal)</p>
                <input
                  type="number"
                  value={price}
                  onChange={e => { setPrice(Number(e.target.value)); setCustomPrice(true); }}
                />
                <p style={{ fontSize:"0.72rem", color:"rgba(232,240,228,0.3)", margin:"4px 0 0" }}>Default: MSP ₹{CROP_PRICES[crop]?.toLocaleString('en-IN')}/q</p>
              </div>
            </div>

            {/* Season */}
            <div style={{ marginBottom:24 }}>
              <p style={{ fontSize:"0.78rem", color:"rgba(232,240,228,0.45)", margin:"0 0 10px", fontWeight:700, textTransform:"uppercase", letterSpacing:"0.05em" }}>Season</p>
              <div style={{ display:"flex", gap:8 }}>
                {["Kharif","Rabi","Zaid"].map(s => (
                  <button key={s} className={`season-btn ${season===s?"active":"inactive"}`} onClick={() => setSeason(s)}>{s}</button>
                ))}
              </div>
            </div>

            <button className="calc-btn" onClick={calculate}>
              Calculate Yield & Income →
            </button>
          </div>

          {/* Results */}
          {result && (
            <div className="fade-up">
              {/* Metrics */}
              <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit,minmax(160px,1fr))", gap:12, marginBottom:20 }}>
                <div className="metric-card">
                  <div className="metric-val" style={{ color:"#6aaa7a" }}>{result.yieldTotal.toFixed(1)}</div>
                  <div className="metric-label">Quintals yield</div>
                </div>
                <div className="metric-card">
                  <div className="metric-val" style={{ color:"#b5d6a0" }}>{fmt(result.revenue)}</div>
                  <div className="metric-label">Gross revenue</div>
                </div>
                <div className="metric-card">
                  <div className="metric-val" style={{ color:"rgba(232,240,228,0.5)" }}>{fmt(result.totalCost)}</div>
                  <div className="metric-label">Est. input cost</div>
                </div>
                <div className="metric-card" style={{ borderColor: result.profit > 0 ? "rgba(106,170,122,0.3)" : "rgba(239,68,68,0.2)" }}>
                  <div className="metric-val" style={{ color: result.profit > 0 ? "#6aaa7a" : "#f87171" }}>{fmt(result.profit)}</div>
                  <div className="metric-label">Est. net profit</div>
                </div>
              </div>

              {/* Profit bar */}
              <div style={{ background:"rgba(255,255,255,0.02)", border:"1px solid rgba(106,170,122,0.12)", borderRadius:16, padding:"18px 22px", marginBottom:20 }}>
                <div style={{ display:"flex", justifyContent:"space-between", marginBottom:8, fontSize:"0.82rem", color:"rgba(232,240,228,0.5)", fontWeight:700 }}>
                  <span>Cost</span><span>Profit</span>
                </div>
                <div style={{ height:10, background:"rgba(255,255,255,0.06)", borderRadius:10, overflow:"hidden" }}>
                  <div style={{ height:"100%", width:`${Math.min(100, (result.profit/result.revenue)*100)}%`, background:"linear-gradient(90deg,#4a7c59,#6aaa7a)", borderRadius:10, transition:"width 0.6s ease" }} />
                </div>
                <div style={{ marginTop:8, fontSize:"0.8rem", color:"rgba(232,240,228,0.4)" }}>
                  Profit margin: <strong style={{ color:"#8fbc8f" }}>{((result.profit/result.revenue)*100).toFixed(1)}%</strong>
                  &nbsp;·&nbsp; Per acre: <strong style={{ color:"#8fbc8f" }}>{fmt(result.profit/land)}</strong>
                </div>
              </div>

              {/* AI Tips */}
              <div style={{ marginBottom:8 }}>
                <p style={{ fontSize:"0.82rem", color:"rgba(232,240,228,0.4)", fontWeight:700, textTransform:"uppercase", letterSpacing:"0.06em", marginBottom:12 }}>
                  💡 AI Tips to improve your yield
                </p>
                {loading ? (
                  <div style={{ color:"rgba(232,240,228,0.4)", fontSize:"0.88rem", display:"flex", alignItems:"center", gap:8 }}>
                    <span style={{ display:"inline-block", animation:"spin 1s linear infinite" }}>⟳</span> Getting tips…
                  </div>
                ) : renderTips(aiTips)}
              </div>

              {/* Disclaimer */}
              <div style={{ marginTop:20, padding:"12px 18px", background:"rgba(212,168,83,0.05)", border:"1px solid rgba(212,168,83,0.12)", borderRadius:12, fontSize:"0.78rem", color:"rgba(232,240,228,0.35)" }}>
                ⚠️ Estimates based on average yields and MSP. Actual results depend on soil quality, rainfall, farming practices, and market rates. Check local mandi prices for accuracy.
              </div>
            </div>
          )}
        {/* ── MANDI PRICE REFERENCE ── */}
          <div style={{ marginTop:40 }}>
            <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom:16, flexWrap:"wrap", gap:10 }}>
              <div>
                <h2 style={{ fontFamily:"'Sora',sans-serif", fontSize:"1rem", fontWeight:700, color:"#e8f0e4", margin:0 }}>📈 Reference Market Prices</h2>
                <p style={{ fontSize:"0.78rem", color:"rgba(232,240,228,0.35)", margin:"4px 0 0" }}>MSP / average mandi rates · ₹ per quintal · 2025–26</p>
              </div>
              <input
                type="text"
                placeholder="Search crop..."
                value={search}
                onChange={e => setSearch(e.target.value)}
                style={{ width:180, padding:"8px 12px", background:"rgba(255,255,255,0.05)", border:"1px solid rgba(106,170,122,0.2)", borderRadius:10, color:"#e8f0e4", fontFamily:"'Nunito',sans-serif", fontSize:"0.85rem", outline:"none" }}
              />
            </div>

            {/* Category chips */}
            <div style={{ display:"flex", gap:8, flexWrap:"wrap", marginBottom:16 }}>
              {CATEGORIES.map(cat => (
                <button key={cat} onClick={() => setActiveCategory(cat)}
                  style={{ padding:"6px 16px", borderRadius:50, border:"1px solid rgba(106,170,122,0.2)", background: activeCategory===cat ? "linear-gradient(135deg,#4a7c59,#6aaa7a)" : "rgba(255,255,255,0.03)", color: activeCategory===cat ? "#fff" : "rgba(232,240,228,0.55)", fontFamily:"'Nunito',sans-serif", fontWeight:700, fontSize:"0.82rem", cursor:"pointer", transition:"all 0.15s" }}
                >{cat}</button>
              ))}
            </div>

            {/* Table */}
            <div style={{ background:"rgba(255,255,255,0.02)", border:"1px solid rgba(106,170,122,0.1)", borderRadius:16, overflow:"hidden" }}>
              <div style={{ display:"grid", gridTemplateColumns:"1fr 90px 90px 90px 70px", padding:"10px 20px", borderBottom:"1px solid rgba(106,170,122,0.1)", fontSize:"0.72rem", color:"rgba(232,240,228,0.35)", fontWeight:700, textTransform:"uppercase", letterSpacing:"0.06em" }}>
                <span>Commodity</span><span style={{textAlign:"right"}}>Min</span><span style={{textAlign:"right"}}>Modal</span><span style={{textAlign:"right"}}>Max</span><span style={{textAlign:"right"}}>Trend</span>
              </div>
              {MANDI_DATA
                .filter(r => (activeCategory === "All" || r.category === activeCategory) && r.commodity.toLowerCase().includes(search.toLowerCase()))
                .map((row, i) => (
                  <div key={row.commodity}
                    onClick={() => { handleCropChange(row.commodity); setPrice(row.modal); setCustomPrice(true); }}
                    style={{ display:"grid", gridTemplateColumns:"1fr 90px 90px 90px 70px", padding:"13px 20px", borderBottom: i % 2 === 0 ? "1px solid rgba(106,170,122,0.05)" : "none", cursor:"pointer", transition:"background 0.15s" }}
                    onMouseEnter={e => e.currentTarget.style.background="rgba(106,170,122,0.06)"}
                    onMouseLeave={e => e.currentTarget.style.background="transparent"}
                  >
                    <div>
                      <span style={{ fontWeight:700, fontSize:"0.9rem", color:"#e8f0e4" }}>{row.commodity}</span>
                      <span style={{ marginLeft:8, fontSize:"0.72rem", color:"rgba(232,240,228,0.3)", background:"rgba(106,170,122,0.08)", padding:"2px 8px", borderRadius:20 }}>{row.category}</span>
                    </div>
                    <span style={{ textAlign:"right", fontSize:"0.88rem", color:"rgba(232,240,228,0.5)" }}>₹{row.min.toLocaleString('en-IN')}</span>
                    <span style={{ textAlign:"right", fontSize:"0.88rem", fontWeight:700, color:"#b5d6a0" }}>₹{row.modal.toLocaleString('en-IN')}</span>
                    <span style={{ textAlign:"right", fontSize:"0.88rem", color:"rgba(232,240,228,0.5)" }}>₹{row.max.toLocaleString('en-IN')}</span>
                    <span style={{ textAlign:"right", fontSize:"1rem" }}>
                      {row.trend === "up" ? "📈" : row.trend === "down" ? "📉" : "➡️"}
                    </span>
                  </div>
                ))}
            </div>
            <p style={{ fontSize:"0.72rem", color:"rgba(232,240,228,0.25)", marginTop:8 }}>💡 Click any row to use that crop & price in the estimator above</p>
          </div>

        </div>
      </div>
    </div>
  );
}
