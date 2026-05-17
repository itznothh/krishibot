import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const BACKEND = "https://krishibot-api.onrender.com";

const STATES = [
  "Andhra Pradesh", "Bihar", "Delhi", "Gujarat", "Haryana",
  "Himachal Pradesh", "Karnataka", "Kerala", "Madhya Pradesh",
  "Maharashtra", "Odisha", "Punjab", "Rajasthan", "Tamil Nadu",
  "Telangana", "Uttar Pradesh", "Uttarakhand", "West Bengal"
];

const FALLBACK_MARKETS = {
  "Karnataka": ["Bangalore","Mysore","Hubli","Belgaum","Mangalore","Davangere","Shimoga","Tumkur","Bijapur","Gulbarga"],
  "Maharashtra": ["Mumbai","Pune","Nashik","Nagpur","Aurangabad","Solapur","Kolhapur","Ahmednagar"],
  "Andhra Pradesh": ["Hyderabad","Vijayawada","Visakhapatnam","Guntur","Kurnool","Tirupati","Nellore"],
  "Tamil Nadu": ["Chennai","Coimbatore","Madurai","Salem","Tiruchirappalli","Tirunelveli","Erode"],
  "Uttar Pradesh": ["Lucknow","Kanpur","Agra","Varanasi","Allahabad","Meerut","Bareilly"],
  "Punjab": ["Amritsar","Ludhiana","Jalandhar","Patiala","Bathinda","Mohali"],
  "Rajasthan": ["Jaipur","Jodhpur","Udaipur","Kota","Ajmer","Bikaner"],
  "Gujarat": ["Ahmedabad","Surat","Vadodara","Rajkot","Bhavnagar","Jamnagar"],
  "Madhya Pradesh": ["Bhopal","Indore","Gwalior","Jabalpur","Ujjain","Sagar"],
  "West Bengal": ["Kolkata","Howrah","Siliguri","Asansol","Durgapur","Bardhaman"],
  "Delhi": ["Azadpur","Okhla","Shahdara","Narela","Lawrence Road"],
  "Haryana": ["Gurugram","Faridabad","Panipat","Ambala","Karnal","Rohtak","Hisar"],
  "Bihar": ["Patna","Gaya","Muzaffarpur","Bhagalpur","Darbhanga"],
  "Kerala": ["Thiruvananthapuram","Kochi","Kozhikode","Thrissur","Kollam"],
  "Telangana": ["Hyderabad","Warangal","Nizamabad","Karimnagar","Khammam"],
  "Odisha": ["Bhubaneswar","Cuttack","Rourkela","Sambalpur","Puri"],
  "Himachal Pradesh": ["Shimla","Manali","Dharamsala","Solan","Mandi"],
  "Uttarakhand": ["Dehradun","Haridwar","Roorkee","Haldwani","Nainital"],
};

const CATEGORIES = ["All", "Vegetables", "Grains", "Fruits", "Pulses"];

const CATEGORY_MAP = {
  Vegetables: ["Tomato", "Onion", "Potato", "Brinjal", "Cabbage", "Cauliflower", "Chilli", "Bitter Gourd", "Bottle Gourd", "Spinach"],
  Grains: ["Wheat", "Rice", "Maize", "Jowar", "Bajra", "Barley"],
  Fruits: ["Banana", "Mango", "Papaya", "Pomegranate", "Grapes", "Watermelon"],
  Pulses: ["Chickpea", "Lentil", "Moong", "Urad", "Tur", "Soybean"],
};

const CROP_EMOJI = {
  Tomato: "🍅", Onion: "🧅", Potato: "🥔", Brinjal: "🍆", Cabbage: "🥬",
  Cauliflower: "🥦", Chilli: "🌶️", Wheat: "🌾", Rice: "🌾", Maize: "🌽",
  Banana: "🍌", Mango: "🥭", Chickpea: "🫘", Lentil: "🫘", Moong: "🫘",
  Jowar: "🌾", Bajra: "🌾", Barley: "🌾", Papaya: "🍈", Pomegranate: "🍎",
  Grapes: "🍇", Watermelon: "🍉", Tur: "🫘", Soybean: "🫘", Urad: "🫘",
  Spinach: "🥬", "Bitter Gourd": "🥒", "Bottle Gourd": "🥒",
};

function today() {
  return new Date().toISOString().split("T")[0];
}

export default function Mandi({ user }) {
  const navigate = useNavigate();
  const [state, setState] = useState("Karnataka");
  const [mandi, setMandi] = useState("");
  const [date, setDate] = useState(today());
  const [category, setCategory] = useState("All");
  const [search, setSearch] = useState("");
  const [prices, setPrices] = useState([]);
  const [mandis, setMandis] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Fetch mandis when state changes
  useEffect(() => {
    fetchMandis(state);
  }, [state]);

  // Fetch prices when mandi or date changes
  useEffect(() => {
    if (mandi) fetchPrices();
  }, [mandi, date]);

  async function fetchMandis(stateName) {
    const fallback = FALLBACK_MARKETS[stateName] || ["All Markets"];
    try {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 8000);
      const res = await fetch(`${BACKEND}/mandi/markets?state=${encodeURIComponent(stateName)}`, { signal: controller.signal });
      clearTimeout(timer);
      const data = await res.json();
      const list = data.markets && data.markets.length > 0 ? data.markets : fallback;
      setMandis(list);
      setMandi(list[0] || "");
    } catch {
      setMandis(fallback);
      setMandi(fallback[0] || "");
    }
  }

  async function fetchPrices() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(
        `${BACKEND}/mandi/prices?state=${encodeURIComponent(state)}&market=${encodeURIComponent(mandi)}&date=${date}`
      );
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setPrices(data.prices || []);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (e) {
      setError(e.message || "Could not fetch prices. Try again.");
      setPrices([]);
    }
    setLoading(false);
  }

  const filtered = prices.filter(p => {
    const matchCat = category === "All" || (CATEGORY_MAP[category] || []).includes(p.commodity);
    const matchSearch = p.commodity.toLowerCase().includes(search.toLowerCase());
    return matchCat && matchSearch;
  });

  const trendColor = (trend) => {
    if (!trend) return "rgba(232,240,228,0.4)";
    if (trend > 0) return "#6aaa7a";
    if (trend < 0) return "#f87171";
    return "rgba(232,240,228,0.4)";
  };

  const trendLabel = (trend) => {
    if (trend == null) return "—";
    if (trend > 0) return `↑ ${trend.toFixed(1)}%`;
    if (trend < 0) return `↓ ${Math.abs(trend).toFixed(1)}%`;
    return "— 0%";
  };

  return (
    <div style={{ minHeight: "100vh", background: "#0e1510", fontFamily: "'Nunito', sans-serif", color: "#e8f0e4" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Sora:wght@700;800&display=swap');
        * { box-sizing: border-box; }
        select, input[type="date"], input[type="text"] {
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
        .price-row:hover { background: rgba(106,170,122,0.05); }
        .cat-pill { cursor: pointer; padding: 7px 16px; border-radius: 50px; font-size: 0.85rem; font-weight: 700; transition: all 0.15s; border: 1px solid rgba(106,170,122,0.2); }
        .cat-pill.active { background: linear-gradient(135deg, #4a7c59, #6aaa7a); color: #fff; border-color: transparent; }
        .cat-pill.inactive { background: rgba(255,255,255,0.03); color: rgba(232,240,228,0.55); }
        .cat-pill.inactive:hover { background: rgba(106,170,122,0.08); color: #e8f0e4; }
        .refresh-btn { display: flex; align-items: center; gap: 6px; padding: 9px 18px; background: rgba(106,170,122,0.1); border: 1px solid rgba(106,170,122,0.25); border-radius: 10px; color: #8fbc8f; font-family: 'Nunito', sans-serif; font-weight: 700; font-size: 0.88rem; cursor: pointer; transition: all 0.15s; }
        .refresh-btn:hover { background: rgba(106,170,122,0.18); color: #b5d6a0; }
        .back-btn { display: flex; align-items: center; gap: 6px; background: none; border: none; color: rgba(232,240,228,0.5); font-family: 'Nunito', sans-serif; font-weight: 700; font-size: 0.9rem; cursor: pointer; transition: color 0.15s; padding: 0; }
        .back-btn:hover { color: #8fbc8f; }
        @keyframes spin { from{transform:rotate(0deg);} to{transform:rotate(360deg);} }
        @keyframes fadeUp { from{opacity:0;transform:translateY(16px);} to{opacity:1;transform:translateY(0);} }
        .fade-up { animation: fadeUp 0.3s ease forwards; }
        .shimmer { background: linear-gradient(90deg, rgba(106,170,122,0.05) 25%, rgba(106,170,122,0.1) 50%, rgba(106,170,122,0.05) 75%); background-size: 200% 100%; animation: shimmerAnim 1.2s infinite; border-radius: 6px; }
        @keyframes shimmerAnim { 0%{background-position:200% 0;} 100%{background-position:-200% 0;} }
      `}</style>

      {/* ── HEADER ── */}
      <header style={{ background: "rgba(14,21,16,0.9)", backdropFilter: "blur(20px)", borderBottom: "1px solid rgba(106,170,122,0.12)", padding: "16px 5%", position: "sticky", top: 0, zIndex: 50, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <button className="back-btn" onClick={() => navigate("/")}>
            ← Home
          </button>
          <div style={{ width: 1, height: 20, background: "rgba(106,170,122,0.2)" }} />
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: "1.3rem" }}>🏪</span>
            <span style={{ fontFamily: "'Sora', sans-serif", fontWeight: 700, fontSize: "1.05rem", color: "#e8f0e4" }}>Mandi Prices</span>
            <span style={{ fontSize: "0.75rem", background: "rgba(106,170,122,0.15)", border: "1px solid rgba(106,170,122,0.25)", borderRadius: 20, padding: "3px 10px", color: "#8fbc8f", fontWeight: 700 }}>LIVE</span>
          </div>
        </div>

        {user && (
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            {user.photoURL && <img src={user.photoURL} style={{ width: 28, height: 28, borderRadius: "50%" }} alt="" />}
            <span style={{ fontSize: "0.85rem", color: "rgba(232,240,228,0.5)", fontWeight: 600 }}>{user.displayName?.split(" ")[0]}</span>
          </div>
        )}
      </header>

      <div style={{ maxWidth: 1100, margin: "0 auto", padding: "32px 5% 60px" }}>

        {/* ── FILTERS ── */}
        <div style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(106,170,122,0.1)", borderRadius: 18, padding: "20px 24px", marginBottom: 24 }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr auto", gap: 12, alignItems: "end" }}>
            <div>
              <p style={{ fontSize: "0.78rem", color: "rgba(232,240,228,0.45)", margin: "0 0 6px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em" }}>State</p>
              <select value={state} onChange={e => setState(e.target.value)}>
                {STATES.map(s => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <p style={{ fontSize: "0.78rem", color: "rgba(232,240,228,0.45)", margin: "0 0 6px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em" }}>Mandi</p>
              <select value={mandi} onChange={e => setMandi(e.target.value)} disabled={mandis.length === 0}>
                {mandis.length === 0
                  ? <option>Loading...</option>
                  : mandis.map(m => <option key={m}>{m}</option>)
                }
              </select>
            </div>
            <div>
              <p style={{ fontSize: "0.78rem", color: "rgba(232,240,228,0.45)", margin: "0 0 6px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em" }}>Date</p>
              <input type="date" value={date} max={today()} onChange={e => setDate(e.target.value)} />
            </div>
            <button className="refresh-btn" onClick={fetchPrices} disabled={loading}>
              <span style={{ display: "inline-block", animation: loading ? "spin 1s linear infinite" : "none" }}>⟳</span>
              Refresh
            </button>
          </div>
        </div>

        {/* ── CATEGORY + SEARCH ── */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 12, marginBottom: 20 }}>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {CATEGORIES.map(c => (
              <button key={c} className={`cat-pill ${category === c ? "active" : "inactive"}`} onClick={() => setCategory(c)}>
                {c}
              </button>
            ))}
          </div>
          <input
            type="text"
            placeholder="Search crop..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{ width: 200 }}
          />
        </div>

        {/* ── PRICE TABLE ── */}
        <div style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(106,170,122,0.1)", borderRadius: 18, overflow: "hidden" }}>

          {/* Table header */}
          <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr 1fr 1fr", padding: "12px 20px", background: "rgba(106,170,122,0.06)", borderBottom: "1px solid rgba(106,170,122,0.1)" }}>
            {["Commodity", "Min", "Modal", "Max", "Trend"].map((h, i) => (
              <p key={h} style={{ fontSize: "0.78rem", color: "rgba(232,240,228,0.45)", margin: 0, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", textAlign: i > 0 ? "right" : "left" }}>{h}</p>
            ))}
          </div>

          {/* Loading state */}
          {loading && (
            <div style={{ padding: "16px 20px" }}>
              {[1,2,3,4,5].map(i => (
                <div key={i} style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr 1fr 1fr", gap: 12, marginBottom: 14, alignItems: "center" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <div className="shimmer" style={{ width: 32, height: 32, borderRadius: "50%" }} />
                    <div className="shimmer" style={{ width: 100, height: 16 }} />
                  </div>
                  {[1,2,3,4].map(j => <div key={j} className="shimmer" style={{ height: 16, marginLeft: "auto", width: 60 }} />)}
                </div>
              ))}
            </div>
          )}

          {/* Error state */}
          {!loading && error && (
            <div style={{ padding: "48px 20px", textAlign: "center" }}>
              <p style={{ fontSize: "2rem", marginBottom: 12 }}>⚠️</p>
              <p style={{ color: "#f87171", fontWeight: 700, marginBottom: 8 }}>{error}</p>
              <p style={{ color: "rgba(232,240,228,0.4)", fontSize: "0.88rem" }}>Check your connection or try a different mandi</p>
            </div>
          )}

          {/* Empty state */}
          {!loading && !error && filtered.length === 0 && prices.length > 0 && (
            <div style={{ padding: "48px 20px", textAlign: "center" }}>
              <p style={{ fontSize: "2rem", marginBottom: 12 }}>🔍</p>
              <p style={{ color: "rgba(232,240,228,0.5)", fontWeight: 600 }}>No results for "{search}" in {category}</p>
            </div>
          )}

          {/* No data yet */}
          {!loading && !error && prices.length === 0 && (
            <div style={{ padding: "48px 20px", textAlign: "center" }}>
              <p style={{ fontSize: "2.5rem", marginBottom: 12 }}>🏪</p>
              <p style={{ color: "rgba(232,240,228,0.5)", fontWeight: 600, marginBottom: 6 }}>Select a mandi to see prices</p>
              <p style={{ color: "rgba(232,240,228,0.3)", fontSize: "0.85rem" }}>Choose state → mandi → date above</p>
            </div>
          )}

          {/* Price rows */}
          {!loading && filtered.map((p, i) => (
            <div
              key={i}
              className="price-row fade-up"
              style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr 1fr 1fr", padding: "14px 20px", borderBottom: i < filtered.length - 1 ? "1px solid rgba(106,170,122,0.07)" : "none", alignItems: "center", transition: "background 0.15s", animationDelay: `${i * 0.03}s` }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{ fontSize: "1.4rem", minWidth: 28 }}>{CROP_EMOJI[p.commodity] || "🌱"}</span>
                <div>
                  <p style={{ fontSize: "0.95rem", fontWeight: 700, margin: 0, color: "#e8f0e4" }}>{p.commodity}</p>
                  <p style={{ fontSize: "0.75rem", color: "rgba(232,240,228,0.4)", margin: 0 }}>{p.variety || "—"} · per {p.unit || "quintal"}</p>
                </div>
              </div>
              <p style={{ fontSize: "0.9rem", margin: 0, textAlign: "right", color: "rgba(232,240,228,0.6)" }}>₹{p.min_price?.toLocaleString()}</p>
              <p style={{ fontSize: "0.95rem", margin: 0, textAlign: "right", fontWeight: 700, color: "#e8f0e4" }}>₹{p.modal_price?.toLocaleString()}</p>
              <p style={{ fontSize: "0.9rem", margin: 0, textAlign: "right", color: "rgba(232,240,228,0.6)" }}>₹{p.max_price?.toLocaleString()}</p>
              <p style={{ fontSize: "0.88rem", margin: 0, textAlign: "right", fontWeight: 700, color: trendColor(p.trend) }}>{trendLabel(p.trend)}</p>
            </div>
          ))}
        </div>

        {/* Footer note */}
        {lastUpdated && (
          <p style={{ fontSize: "0.78rem", color: "rgba(232,240,228,0.3)", textAlign: "center", marginTop: 16 }}>
            Source: Agmarknet (data.gov.in) · Last fetched at {lastUpdated}
          </p>
        )}
      </div>
    </div>
  );
}
