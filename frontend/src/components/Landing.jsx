import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";

const features = [
  { icon: "🌾", title: "Crop Advisor", desc: "Season & soil-specific crop recommendations — tell us your soil type and get the best options instantly." },
  { icon: "🐛", title: "Pest & Disease", desc: "Describe symptoms or upload a photo. Get identified pests and step-by-step treatment plans." },
  { icon: "📸", title: "Disease Scanner", desc: "Point your camera at any affected crop. AI diagnoses the problem and suggests remedies in seconds." },
  { icon: "🌦️", title: "Weather Alerts", desc: "Hyperlocal real-time weather with advice on irrigation, spraying windows, and harvest timing." },
  { icon: "🧪", title: "Fertilizer Guide", desc: "Exact NPK ratios, application schedules, and organic alternatives for 22+ crops." },
  { icon: "🏪", title: "Mandi Prices", desc: "Track live market prices across states. Know when and where to sell for maximum profit." },
  { icon: "📋", title: "Schemes & Loans", desc: "Filter government schemes, subsidies and loans that you actually qualify for — by state and crop." },
  { icon: "📊", title: "Yield Estimator", desc: "Enter your land size and crop. Get expected yield, gross income and estimated net profit." },
];

const stats = [
  { value: "3", label: "Languages", sub: "EN · HI · KN" },
  { value: "22+", label: "Crops", sub: "Full fertilizer data" },
  { value: "24/7", label: "Available", sub: "No downtime" },
  { value: "Free", label: "Always", sub: "No subscription" },
];

const navFeatures = [
  { icon: "🏪", label: "Mandi Prices", desc: "Live crop prices from markets", path: "/mandi" },
  { icon: "📋", label: "Schemes & Loans", desc: "Govt schemes you qualify for", path: "/schemes" },
  { icon: "📊", label: "Yield Estimator", desc: "Estimate income from your crop", path: "/yield" },
  { icon: "💬", label: "AI Chat", desc: "Ask anything in EN / HI / KN", path: null, action: "chat" },
  { icon: "📸", label: "Disease Scanner", desc: "Photo-based crop diagnosis", path: null, action: "chat" },
];

const howItWorks = [
  { step: "01", title: "Ask in your language", desc: "Type or speak in Hindi, Kannada, or English. No translation needed.", icon: "💬" },
  { step: "02", title: "AI understands context", desc: "KrishiBot reads your location, crop type, and season to give relevant advice.", icon: "🧠" },
  { step: "03", title: "Get actionable advice", desc: "Specific quantities, timings, and product names — not generic tips.", icon: "✅" },
];

function Particle({ style }) {
  return <div style={{ position: "absolute", width: 6, height: 6, borderRadius: "50%", background: "rgba(106,170,122,0.35)", ...style }} />;
}

export default function Landing({ onEnter, onLoginClick, user, onSignOut }) {
  const navigate = useNavigate();
  const [visible, setVisible] = useState(false);
  const [hoveredFeature, setHoveredFeature] = useState(null);
  const [showProfileDropdown, setShowProfileDropdown] = useState(false);
  const [showFeaturesDropdown, setShowFeaturesDropdown] = useState(false);
  const featuresRef = useRef(null);
  const profileRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => { setTimeout(() => setVisible(true), 100); }, []);

  useEffect(() => {
    const handler = (e) => {
      if (featuresRef.current && !featuresRef.current.contains(e.target)) setShowFeaturesDropdown(false);
      if (profileRef.current && !profileRef.current.contains(e.target)) setShowProfileDropdown(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let frame;
    const draw = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
      const imageData = ctx.createImageData(canvas.width, canvas.height);
      for (let i = 0; i < imageData.data.length; i += 4) {
        const v = Math.random() * 255;
        imageData.data[i] = v; imageData.data[i+1] = v; imageData.data[i+2] = v; imageData.data[i+3] = 8;
      }
      ctx.putImageData(imageData, 0, 0);
      frame = requestAnimationFrame(draw);
    };
    draw();
    return () => cancelAnimationFrame(frame);
  }, []);

  const particles = Array.from({ length: 18 }, (_, i) => ({
    top: `${Math.random() * 100}%`, left: `${Math.random() * 100}%`,
    animation: `float${i % 3} ${4 + (i % 4)}s ease-in-out infinite`,
    animationDelay: `${(i * 0.4) % 3}s`, opacity: 0.4 + (i % 3) * 0.15,
  }));

  const handleNavFeatureClick = (item) => {
    setShowFeaturesDropdown(false);
    if (item.path) navigate(item.path);
    else if (item.action === "chat") onEnter && onEnter();
  };

  return (
    <div style={{ minHeight: "100vh", background: "#141a12", fontFamily: "'Nunito', sans-serif", color: "#e8f0e4", overflowX: "hidden", position: "relative" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');
        @keyframes fadeUp { from { opacity:0; transform:translateY(32px); } to { opacity:1; transform:translateY(0); } }
        @keyframes fadeIn { from { opacity:0; transform:translateY(-6px); } to { opacity:1; transform:translateY(0); } }
        @keyframes float0 { 0%,100%{transform:translateY(0);} 50%{transform:translateY(-14px);} }
        @keyframes float1 { 0%,100%{transform:translateY(0) translateX(0);} 50%{transform:translateY(-10px) translateX(8px);} }
        @keyframes float2 { 0%,100%{transform:translateY(0);} 50%{transform:translateY(-18px);} }
        @keyframes pulse { 0%,100%{opacity:0.6;transform:scale(1);} 50%{opacity:1;transform:scale(1.04);} }
        @keyframes shimmer { 0%{background-position:-200% center;} 100%{background-position:200% center;} }
        .hero-title { font-family:'Sora',sans-serif; font-size:clamp(2.6rem,6vw,5rem); font-weight:800; line-height:1.08; letter-spacing:-0.03em; }
        .green-shimmer { background:linear-gradient(90deg,#6aaa7a 0%,#b5d6a0 40%,#6aaa7a 60%,#4a7c59 100%); background-size:200% auto; -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; animation:shimmer 3.5s linear infinite; }
        .cta-btn { display:inline-flex; align-items:center; gap:10px; padding:16px 38px; background:linear-gradient(135deg,#4a7c59,#6aaa7a); color:#fff; font-family:'Nunito',sans-serif; font-weight:800; font-size:1.05rem; border:none; border-radius:50px; cursor:pointer; box-shadow:0 8px 32px rgba(74,124,89,0.4); transition:transform 0.18s,box-shadow 0.18s; }
        .cta-btn:hover { transform:translateY(-3px) scale(1.03); box-shadow:0 14px 40px rgba(74,124,89,0.55); }
        .login-btn { display:inline-flex; align-items:center; gap:8px; padding:12px 28px; background:transparent; color:#8fbc8f; font-family:'Nunito',sans-serif; font-weight:700; font-size:0.95rem; border:1.5px solid rgba(143,188,143,0.3); border-radius:50px; cursor:pointer; transition:all 0.18s; }
        .login-btn:hover { background:rgba(143,188,143,0.08); border-color:rgba(143,188,143,0.6); color:#b5d6a0; }
        .feature-card { background:rgba(255,255,255,0.03); border:1px solid rgba(106,170,122,0.12); border-radius:20px; padding:28px 24px; transition:all 0.22s; position:relative; overflow:hidden; cursor:default; }
        .feature-card:hover { background:rgba(106,170,122,0.06); border-color:rgba(106,170,122,0.3); transform:translateY(-4px); box-shadow:0 12px 40px rgba(74,124,89,0.18); }
        .feature-card::before { content:''; position:absolute; top:0;left:0;right:0; height:1px; background:linear-gradient(90deg,transparent,rgba(106,170,122,0.4),transparent); opacity:0; transition:opacity 0.22s; }
        .feature-card:hover::before { opacity:1; }
        .orb { position:absolute; border-radius:50%; filter:blur(80px); pointer-events:none; animation:pulse 6s ease-in-out infinite; }
        .nav-link { color:rgba(232,240,228,0.55); font-weight:600; font-size:0.9rem; cursor:pointer; transition:color 0.15s; background:none; border:none; font-family:'Nunito',sans-serif; }
        .nav-link:hover { color:#8fbc8f; }
        .nav-link.active { color:#8fbc8f; }
        .badge { display:inline-flex; align-items:center; gap:6px; padding:6px 14px; background:rgba(106,170,122,0.1); border:1px solid rgba(106,170,122,0.2); border-radius:50px; font-size:0.78rem; font-weight:700; color:#8fbc8f; letter-spacing:0.06em; text-transform:uppercase; }
        .whatsapp-pill { display:inline-flex; align-items:center; gap:8px; padding:10px 20px; background:rgba(37,211,102,0.1); border:1px solid rgba(37,211,102,0.25); border-radius:50px; font-size:0.85rem; font-weight:700; color:#25d366; cursor:pointer; transition:all 0.18s; text-decoration:none; }
        .whatsapp-pill:hover { background:rgba(37,211,102,0.18); transform:translateY(-2px); }
        .profile-dropdown { position:absolute; top:calc(100% + 10px); right:0; background:#1c2419; border:1px solid rgba(106,170,122,0.2); border-radius:16px; padding:8px; min-width:200px; box-shadow:0 16px 40px rgba(0,0,0,0.4); animation:fadeIn 0.15s ease; z-index:200; }
        .features-dropdown { position:absolute; top:calc(100% + 14px); left:50%; transform:translateX(-50%); background:#1a2118; border:1px solid rgba(106,170,122,0.2); border-radius:18px; padding:10px; min-width:280px; box-shadow:0 20px 50px rgba(0,0,0,0.5); animation:fadeIn 0.15s ease; z-index:200; }
        .features-dropdown::before { content:''; position:absolute; top:-6px; left:50%; width:12px; height:12px; background:#1a2118; border-left:1px solid rgba(106,170,122,0.2); border-top:1px solid rgba(106,170,122,0.2); transform:translateX(-50%) rotate(45deg); }
        .dropdown-item { display:flex; align-items:center; gap:10px; padding:10px 14px; border-radius:10px; cursor:pointer; color:rgba(232,240,228,0.7); font-size:0.88rem; font-weight:600; transition:all 0.15s; background:none; border:none; width:100%; text-align:left; font-family:'Nunito',sans-serif; }
        .dropdown-item:hover { background:rgba(106,170,122,0.1); color:#e8f0e4; }
        .dropdown-item.danger:hover { background:rgba(239,68,68,0.1); color:#f87171; }
        .features-dropdown-item { display:flex; align-items:flex-start; gap:12px; padding:12px 14px; border-radius:12px; cursor:pointer; transition:all 0.15s; background:none; border:none; width:100%; text-align:left; font-family:'Nunito',sans-serif; }
        .features-dropdown-item:hover { background:rgba(106,170,122,0.08); }
        .features-dropdown-item:hover .fdi-label { color:#e8f0e4; }
        .fdi-icon { font-size:1.3rem; line-height:1; margin-top:1px; flex-shrink:0; }
        .fdi-label { color:#b5d6a0; font-weight:700; font-size:0.9rem; margin-bottom:2px; }
        .fdi-desc { color:rgba(232,240,228,0.4); font-size:0.78rem; font-weight:500; }
        .step-card { background:rgba(255,255,255,0.02); border:1px solid rgba(106,170,122,0.1); border-radius:20px; padding:32px 28px; position:relative; }
        .step-num { font-family:'Sora',sans-serif; font-size:3rem; font-weight:800; color:rgba(106,170,122,0.12); position:absolute; top:20px; right:24px; line-height:1; }
      `}</style>

      <canvas ref={canvasRef} style={{ position:"fixed", inset:0, width:"100%", height:"100%", pointerEvents:"none", zIndex:99, opacity:0.55 }} />
      <div className="orb" style={{ width:500, height:500, background:"rgba(74,124,89,0.12)", top:-100, right:-100 }} />
      <div className="orb" style={{ width:400, height:400, background:"rgba(212,168,83,0.07)", bottom:200, left:-150, animationDelay:"3s" }} />
      <div className="orb" style={{ width:300, height:300, background:"rgba(106,170,122,0.08)", top:"40%", left:"40%", animationDelay:"1.5s" }} />
      {particles.map((p, i) => <Particle key={i} style={p} />)}

      {/* ── NAV ── */}
      <nav style={{ position:"fixed", top:0, left:0, right:0, zIndex:100, display:"flex", alignItems:"center", justifyContent:"space-between", padding:"18px 5%", background:"rgba(20,26,18,0.75)", backdropFilter:"blur(20px)", borderBottom:"1px solid rgba(106,170,122,0.1)" }}>
        <div style={{ display:"flex", alignItems:"center", gap:10 }}>
          <span style={{ fontSize:"1.5rem" }}>🌾</span>
          <span style={{ fontFamily:"'Sora',sans-serif", fontWeight:700, fontSize:"1.1rem", color:"#e8f0e4" }}>KrishiBot</span>
        </div>

        <div style={{ display:"flex", alignItems:"center", gap:24 }}>
          {/* Features dropdown */}
          <div ref={featuresRef} style={{ position:"relative" }}>
            <button className={`nav-link${showFeaturesDropdown ? " active" : ""}`}
              onClick={() => setShowFeaturesDropdown(!showFeaturesDropdown)}
              style={{ display:"flex", alignItems:"center", gap:5 }}>
              Features
              <span style={{ fontSize:"0.65rem", opacity:0.6, transition:"transform 0.2s", display:"inline-block", transform: showFeaturesDropdown ? "rotate(180deg)" : "rotate(0deg)" }}>▼</span>
            </button>
            {showFeaturesDropdown && (
              <div className="features-dropdown">
                <div style={{ padding:"6px 10px 8px", borderBottom:"1px solid rgba(106,170,122,0.1)", marginBottom:4 }}>
                  <div style={{ fontSize:"0.7rem", color:"rgba(232,240,228,0.3)", fontWeight:700, letterSpacing:"0.08em", textTransform:"uppercase" }}>KrishiBot Features</div>
                </div>
                {navFeatures.map((item, i) => (
                  <button key={i} className="features-dropdown-item" onClick={() => handleNavFeatureClick(item)}>
                    <span className="fdi-icon">{item.icon}</span>
                    <div>
                      <div className="fdi-label">{item.label}</div>
                      <div className="fdi-desc">{item.desc}</div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* About → GitHub */}
          <a href="https://github.com/itznothh/krishibot" target="_blank" rel="noopener noreferrer"
            className="nav-link" style={{ textDecoration:"none", display:"flex", alignItems:"center", gap:6 }}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" style={{ opacity:0.7 }}>
              <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0 1 12 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/>
            </svg>
            About
          </a>

          {/* User profile / Sign in */}
          {user ? (
            <div ref={profileRef} style={{ position:"relative" }}>
              <button onClick={() => setShowProfileDropdown(!showProfileDropdown)}
                style={{ display:"flex", alignItems:"center", gap:8, background:"rgba(106,170,122,0.08)", border:"1.5px solid rgba(106,170,122,0.25)", borderRadius:50, padding:"6px 14px 6px 6px", cursor:"pointer", transition:"all 0.18s" }}>
                {user.photoURL ? (
                  <img src={user.photoURL} style={{ width:28, height:28, borderRadius:"50%" }} alt="" />
                ) : (
                  <div style={{ width:28, height:28, borderRadius:"50%", background:"linear-gradient(135deg,#4a7c59,#6aaa7a)", display:"flex", alignItems:"center", justifyContent:"center", fontSize:"0.85rem", fontWeight:700, color:"#fff" }}>
                    {user.displayName?.[0] || "F"}
                  </div>
                )}
                <span style={{ color:"#b5d6a0", fontWeight:700, fontSize:"0.88rem" }}>
                  {user.displayName?.split(" ")[0] || "Farmer"}
                </span>
                <span style={{ color:"rgba(181,214,160,0.5)", fontSize:"0.7rem" }}>▼</span>
              </button>
              {showProfileDropdown && (
                <div className="profile-dropdown">
                  <div style={{ padding:"10px 14px 8px", borderBottom:"1px solid rgba(106,170,122,0.1)", marginBottom:4 }}>
                    <div style={{ fontSize:"0.78rem", color:"rgba(232,240,228,0.4)" }}>Signed in as</div>
                    <div style={{ fontSize:"0.85rem", color:"#b5d6a0", fontWeight:700, marginTop:2, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{user.email}</div>
                  </div>
                  <button className="dropdown-item" onClick={() => { setShowProfileDropdown(false); onEnter && onEnter(); }}>
                    💬 Start Chatting
                  </button>
                  <button className="dropdown-item danger" onClick={() => { setShowProfileDropdown(false); onSignOut(); }}>
                    🚪 Sign out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <button className="login-btn" onClick={onLoginClick}>Sign in</button>
          )}
        </div>
      </nav>

      {/* ── HERO ── */}
      <section style={{ minHeight:"100vh", display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center", textAlign:"center", padding:"120px 5% 80px", position:"relative" }}>
        <div style={{ opacity:visible?1:0, animation:visible?"fadeUp 0.7s ease forwards":"none" }}>
          <div style={{ marginBottom:20 }}>
            <span className="badge">🇮🇳 Made for Indian Farmers</span>
          </div>
          <h1 className="hero-title" style={{ margin:"0 auto 20px", maxWidth:780 }}>
            Your AI farming<br /><span className="green-shimmer">companion</span>
          </h1>
          <p style={{ fontSize:"clamp(1rem,2vw,1.15rem)", color:"rgba(232,240,228,0.55)", maxWidth:520, margin:"0 auto 40px", lineHeight:1.7, fontWeight:500 }}>
            Ask in Hindi, Kannada or English. Get instant advice on crops, pests, fertilizers and weather — tailored to your farm. Always free.
          </p>
          <div style={{ display:"flex", gap:14, justifyContent:"center", flexWrap:"wrap", marginBottom:40 }}>
            <button className="cta-btn" onClick={onEnter}>
              Start Chatting <span style={{ fontSize:"1.1rem" }}>→</span>
            </button>
            {user ? (
              <div style={{ display:"flex", alignItems:"center", gap:8, padding:"12px 20px", background:"rgba(106,170,122,0.08)", border:"1px solid rgba(106,170,122,0.2)", borderRadius:50 }}>
                <span>🙏</span>
                <span style={{ color:"#b5d6a0", fontWeight:700, fontSize:"0.95rem" }}>
                  Namaste, {user.displayName?.split(" ")[0] || "Farmer"}!
                </span>
              </div>
            ) : (
              <button className="login-btn" onClick={onLoginClick}>Sign in / Register</button>
            )}
          </div>
          <a href="https://wa.me/14155238886" className="whatsapp-pill" target="_blank" rel="noopener noreferrer">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
            </svg>
            Also on WhatsApp
          </a>
        </div>

        {/* ── STATS ── */}
        <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", marginTop:70, borderTop:"1px solid rgba(106,170,122,0.1)", borderBottom:"1px solid rgba(106,170,122,0.1)", width:"100%", maxWidth:700, opacity:visible?1:0, animation:visible?"fadeUp 0.8s 0.3s ease both":"none" }}>
          {stats.map((s, i) => (
            <div key={i} style={{ textAlign:"center", padding:"24px 16px", borderRight:i<stats.length-1?"1px solid rgba(106,170,122,0.1)":"none" }}>
              <div style={{ fontFamily:"'Sora',sans-serif", fontSize:"2.4rem", fontWeight:800, color:"#6aaa7a", lineHeight:1 }}>{s.value}</div>
              <div style={{ fontSize:"0.82rem", color:"rgba(232,240,228,0.5)", marginTop:4, fontWeight:700, letterSpacing:"0.08em", textTransform:"uppercase" }}>{s.label}</div>
              <div style={{ fontSize:"0.72rem", color:"rgba(232,240,228,0.28)", marginTop:3, fontWeight:500 }}>{s.sub}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── HOW IT WORKS ── */}
      <section style={{ padding:"80px 5%", maxWidth:1100, margin:"0 auto" }}>
        <div style={{ textAlign:"center", marginBottom:48 }}>
          <div className="badge" style={{ marginBottom:14 }}>Simple as talking</div>
          <h2 style={{ fontFamily:"'Sora',sans-serif", fontSize:"clamp(1.8rem,4vw,2.6rem)", fontWeight:800, color:"#e8f0e4", letterSpacing:"-0.02em" }}>
            How KrishiBot works
          </h2>
        </div>
        <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit,minmax(280px,1fr))", gap:18 }}>
          {howItWorks.map((h, i) => (
            <div key={i} className="step-card">
              <div className="step-num">{h.step}</div>
              <div style={{ fontSize:"2rem", marginBottom:14 }}>{h.icon}</div>
              <h3 style={{ fontFamily:"'Sora',sans-serif", fontWeight:700, fontSize:"1rem", color:"#e8f0e4", marginBottom:8 }}>{h.title}</h3>
              <p style={{ color:"rgba(232,240,228,0.45)", fontSize:"0.88rem", lineHeight:1.65 }}>{h.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── FEATURES SECTION ── */}
      <section style={{ padding:"0 5% 100px", maxWidth:1100, margin:"0 auto" }}>
        <div style={{ textAlign:"center", marginBottom:48 }}>
          <div className="badge" style={{ marginBottom:14 }}>Full toolkit</div>
          <h2 style={{ fontFamily:"'Sora',sans-serif", fontSize:"clamp(1.8rem,4vw,2.6rem)", fontWeight:800, color:"#e8f0e4", letterSpacing:"-0.02em" }}>
            Everything a farmer needs
          </h2>
          <p style={{ color:"rgba(232,240,228,0.4)", marginTop:12, fontSize:"0.95rem", maxWidth:480, margin:"12px auto 0" }}>
            All tools in one place — no switching apps, no subscriptions, no downloads.
          </p>
        </div>
        <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(260px, 1fr))", gap:16 }}>
          {features.map((f, i) => (
            <div key={i} className="feature-card"
              onMouseEnter={() => setHoveredFeature(i)}
              onMouseLeave={() => setHoveredFeature(null)}>
              <div style={{ fontSize:"1.8rem", marginBottom:12, transition:"transform 0.2s", transform:hoveredFeature===i?"scale(1.15)":"scale(1)", display:"inline-block" }}>{f.icon}</div>
              <h3 style={{ fontFamily:"'Sora',sans-serif", fontWeight:700, fontSize:"0.95rem", color:"#e8f0e4", marginBottom:6 }}>{f.title}</h3>
              <p style={{ color:"rgba(232,240,228,0.42)", fontSize:"0.85rem", lineHeight:1.65 }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA BANNER ── */}
      <section style={{ margin:"0 5% 100px", background:"linear-gradient(135deg,rgba(74,124,89,0.18),rgba(106,170,122,0.08))", border:"1px solid rgba(106,170,122,0.2)", borderRadius:28, padding:"60px 40px", textAlign:"center", position:"relative", overflow:"hidden" }}>
        <div style={{ position:"absolute", inset:0, background:"radial-gradient(ellipse at 50% 0%,rgba(106,170,122,0.12),transparent 60%)", pointerEvents:"none" }} />
        <div className="badge" style={{ marginBottom:20 }}>Free, forever</div>
        <h2 style={{ fontFamily:"'Sora',sans-serif", fontSize:"clamp(1.6rem,3.5vw,2.4rem)", fontWeight:800, color:"#e8f0e4", marginBottom:14, letterSpacing:"-0.02em" }}>
          Start farming smarter today
        </h2>
        <p style={{ color:"rgba(232,240,228,0.45)", marginBottom:32, fontSize:"0.95rem", maxWidth:400, margin:"0 auto 32px" }}>
          No app to download. No account required to try. No subscription ever.
        </p>
        <div style={{ display:"flex", gap:14, justifyContent:"center", flexWrap:"wrap" }}>
          <button className="cta-btn" onClick={onEnter}>Open KrishiBot 🌾</button>
          <a href="https://wa.me/14155238886" className="whatsapp-pill" target="_blank" rel="noopener noreferrer">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
            Try on WhatsApp
          </a>
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer style={{ borderTop:"1px solid rgba(106,170,122,0.1)", padding:"28px 5%", display:"flex", alignItems:"center", justifyContent:"space-between", flexWrap:"wrap", gap:12, color:"rgba(232,240,228,0.3)", fontSize:"0.82rem" }}>
        <div style={{ display:"flex", alignItems:"center", gap:8 }}>
          <span>🌾</span>
          <span style={{ fontWeight:700 }}>KrishiBot</span>
          <span>— Built for Indian farmers</span>
        </div>
        <div style={{ display:"flex", alignItems:"center", gap:20 }}>
          <span>Kisan Helpline: 1800-180-1551 (Free, 24x7)</span>
          <a href="https://github.com/itznothh/krishibot" target="_blank" rel="noopener noreferrer"
            style={{ color:"rgba(232,240,228,0.3)", textDecoration:"none", display:"flex", alignItems:"center", gap:5, transition:"color 0.15s" }}
            onMouseEnter={e=>e.currentTarget.style.color="#8fbc8f"}
            onMouseLeave={e=>e.currentTarget.style.color="rgba(232,240,228,0.3)"}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0 1 12 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/>
            </svg>
            GitHub
          </a>
        </div>
      </footer>
    </div>
  );
}
