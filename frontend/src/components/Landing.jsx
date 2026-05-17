import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";

const features = [
  { icon: "🌾", title: "Crop Advisor", desc: "Get season & soil-specific crop recommendations instantly." },
  { icon: "🐛", title: "Pest & Disease", desc: "Identify pests, diseases and get step-by-step treatment plans." },
  { icon: "📸", title: "Disease Scanner", desc: "Upload a photo of your crop — AI diagnoses the problem." },
  { icon: "🌦️", title: "Weather Alerts", desc: "Real-time hyperlocal weather with farming-specific advice." },
  { icon: "🧪", title: "Fertilizer Guide", desc: "Exact NPK ratios, chemical & organic options per crop." },
  { icon: "💬", title: "3 Languages", desc: "Ask in English, Hindi or Kannada — KrishiBot understands." },
  { icon: "📊", title: "Yield Estimator", desc: "Enter land size & crop to get expected yield, income & profit estimate." },
];

const stats = [
  { value: "3", label: "Languages" },
  { value: "22+", label: "Crop Modules" },
  { value: "24/7", label: "Available" },
  { value: "Free", label: "Always" },
];

// Nav feature links shown in dropdown
const navFeatures = [
  { icon: "🏪", label: "Mandi Prices", desc: "Live crop prices from markets", path: "/mandi" },
  { icon: "📋", label: "Schemes & Loans", desc: "Govt schemes you qualify for", path: "/schemes" },
  { icon: "💬", label: "AI Chat", desc: "Ask anything in EN / HI / KN", path: null, action: "chat" },
  { icon: "📊", label: "Yield Estimator", desc: "Estimate income from your crop", path: "/yield" },
  { icon: "📸", label: "Disease Scanner", desc: "Photo-based crop diagnosis", path: null, action: "chat" },
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

  // Close dropdowns on outside click
  useEffect(() => {
    const handler = (e) => {
      if (featuresRef.current && !featuresRef.current.contains(e.target)) {
        setShowFeaturesDropdown(false);
      }
      if (profileRef.current && !profileRef.current.contains(e.target)) {
        setShowProfileDropdown(false);
      }
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
    if (item.path) {
      navigate(item.path);
    } else if (item.action === "chat") {
      onEnter && onEnter();
    }
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
        .feature-card { background:rgba(255,255,255,0.03); border:1px solid rgba(106,170,122,0.12); border-radius:20px; padding:28px 24px; transition:all 0.22s; position:relative; overflow:hidden; }
        .feature-card:hover { background:rgba(106,170,122,0.06); border-color:rgba(106,170,122,0.3); transform:translateY(-4px); box-shadow:0 12px 40px rgba(74,124,89,0.18); }
        .feature-card::before { content:''; position:absolute; top:0;left:0;right:0; height:1px; background:linear-gradient(90deg,transparent,rgba(106,170,122,0.4),transparent); opacity:0; transition:opacity 0.22s; }
        .feature-card:hover::before { opacity:1; }
        .stat-item { text-align:center; padding:24px 16px; }
        .stat-value { font-family:'Sora',sans-serif; font-size:2.4rem; font-weight:800; color:#6aaa7a; line-height:1; }
        .stat-label { font-size:0.82rem; color:rgba(232,240,228,0.5); margin-top:4px; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; }
        .orb { position:absolute; border-radius:50%; filter:blur(80px); pointer-events:none; animation:pulse 6s ease-in-out infinite; }
        .nav-link { color:rgba(232,240,228,0.55); font-weight:600; font-size:0.9rem; cursor:pointer; transition:color 0.15s; background:none; border:none; font-family:'Nunito',sans-serif; }
        .nav-link:hover { color:#8fbc8f; }
        .nav-link.active { color:#8fbc8f; }
        .badge { display:inline-flex; align-items:center; gap:6px; padding:6px 14px; background:rgba(106,170,122,0.1); border:1px solid rgba(106,170,122,0.2); border-radius:50px; font-size:0.78rem; font-weight:700; color:#8fbc8f; letter-spacing:0.06em; text-transform:uppercase; }
        .whatsapp-pill { display:inline-flex; align-items:center; gap:8px; padding:10px 20px; background:rgba(37,211,102,0.1); border:1px solid rgba(37,211,102,0.25); border-radius:50px; font-size:0.85rem; font-weight:700; color:#25d366; cursor:pointer; transition:all 0.18s; text-decoration:none; }
        .whatsapp-pill:hover { background:rgba(37,211,102,0.18); transform:translateY(-2px); }
        .profile-dropdown { position:absolute; top:calc(100% + 10px); right:0; background:#1c2419; border:1px solid rgba(106,170,122,0.2); border-radius:16px; padding:8px; min-width:200px; box-shadow:0 16px 40px rgba(0,0,0,0.4); animation:fadeIn 0.15s ease; z-index:200; }
        .features-dropdown { position:absolute; top:calc(100% + 14px); left:50%; transform:translateX(-50%); background:#1a2118; border:1px solid rgba(106,170,122,0.2); border-radius:18px; padding:10px; min-width:260px; box-shadow:0 20px 50px rgba(0,0,0,0.5); animation:fadeIn 0.15s ease; z-index:200; }
        .features-dropdown::before { content:''; position:absolute; top:-6px; left:50%; transform:translateX(-50%); width:12px; height:12px; background:#1a2118; border-left:1px solid rgba(106,170,122,0.2); border-top:1px solid rgba(106,170,122,0.2); transform:translateX(-50%) rotate(45deg); }
        .dropdown-item { display:flex; align-items:center; gap:10px; padding:10px 14px; border-radius:10px; cursor:pointer; color:rgba(232,240,228,0.7); font-size:0.88rem; font-weight:600; transition:all 0.15s; background:none; border:none; width:100%; text-align:left; font-family:'Nunito',sans-serif; }
        .dropdown-item:hover { background:rgba(106,170,122,0.1); color:#e8f0e4; }
        .dropdown-item.danger:hover { background:rgba(239,68,68,0.1); color:#f87171; }
        .features-dropdown-item { display:flex; align-items:flex-start; gap:12px; padding:12px 14px; border-radius:12px; cursor:pointer; transition:all 0.15s; background:none; border:none; width:100%; text-align:left; font-family:'Nunito',sans-serif; }
        .features-dropdown-item:hover { background:rgba(106,170,122,0.08); }
        .features-dropdown-item:hover .fdi-label { color:#e8f0e4; }
        .fdi-icon { font-size:1.3rem; line-height:1; margin-top:1px; flex-shrink:0; }
        .fdi-label { color:#b5d6a0; font-weight:700; font-size:0.9rem; margin-bottom:2px; }
        .fdi-desc { color:rgba(232,240,228,0.4); font-size:0.78rem; font-weight:500; }
        .features-dropdown-divider { height:1px; background:rgba(106,170,122,0.1); margin:6px 8px; }
      `}</style>

      <canvas ref={canvasRef} style={{ position:"fixed", inset:0, width:"100%", height:"100%", pointerEvents:"none", zIndex:99, opacity:0.55 }} />
      <div className="orb" style={{ width:500, height:500, background:"rgba(74,124,89,0.12)", top:-100, right:-100 }} />
      <div className="orb" style={{ width:400, height:400, background:"rgba(212,168,83,0.07)", bottom:200, left:-150, animationDelay:"3s" }} />
      <div className="orb" style={{ width:300, height:300, background:"rgba(106,170,122,0.08)", top:"40%", left:"40%", animationDelay:"1.5s" }} />
      {particles.map((p, i) => <Particle key={i} style={p} />)}

      {/* ── NAV ── */}
      <nav style={{ position:"fixed", top:0, left:0, right:0, zIndex:100, display:"flex", alignItems:"center", justifyContent:"space-between", padding:"18px 5%", background:"rgba(20,26,18,0.75)", backdropFilter:"blur(20px)", borderBottom:"1px solid rgba(106,170,122,0.1)" }}>
        {/* Logo */}
        <div style={{ display:"flex", alignItems:"center", gap:10 }}>
          <span style={{ fontSize:"1.5rem" }}>🌾</span>
          <span style={{ fontFamily:"'Sora',sans-serif", fontWeight:700, fontSize:"1.1rem", color:"#e8f0e4" }}>KrishiBot</span>
        </div>

        {/* Nav links */}
        <div style={{ display:"flex", alignItems:"center", gap:24 }}>

          {/* Features dropdown */}
          <div ref={featuresRef} style={{ position:"relative" }}>
            <button
              className={`nav-link${showFeaturesDropdown ? " active" : ""}`}
              onClick={() => setShowFeaturesDropdown(!showFeaturesDropdown)}
              style={{ display:"flex", alignItems:"center", gap:5 }}
            >
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

          <button className="nav-link">About</button>

          {/* User profile / Sign in */}
          {user ? (
            <div ref={profileRef} style={{ position:"relative" }}>
              <button
                onClick={() => setShowProfileDropdown(!showProfileDropdown)}
                style={{ display:"flex", alignItems:"center", gap:8, background:"rgba(106,170,122,0.08)", border:"1.5px solid rgba(106,170,122,0.25)", borderRadius:50, padding:"6px 14px 6px 6px", cursor:"pointer", transition:"all 0.18s" }}
              >
                {user.photoURL ? (
                  <img src={user.photoURL} alt={user.displayName} style={{ width:28, height:28, borderRadius:"50%", objectFit:"cover" }} />
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
          <p style={{ fontSize:"clamp(1rem,2vw,1.2rem)", color:"rgba(232,240,228,0.55)", maxWidth:560, margin:"0 auto 40px", lineHeight:1.65, fontWeight:500 }}>
            Ask crop questions in Hindi, Kannada or English. Get pest advice, fertilizer plans, weather alerts — all in one place. Free, always.
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

        {/* Stats */}
        <div style={{ display:"flex", marginTop:70, borderTop:"1px solid rgba(106,170,122,0.1)", borderBottom:"1px solid rgba(106,170,122,0.1)", width:"100%", maxWidth:700, opacity:visible?1:0, animation:visible?"fadeUp 0.8s 0.3s ease both":"none" }}>
          {stats.map((s, i) => (
            <div key={i} className="stat-item" style={{ flex:1, borderRight:i<stats.length-1?"1px solid rgba(106,170,122,0.1)":"none" }}>
              <div className="stat-value">{s.value}</div>
              <div className="stat-label">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── FEATURES SECTION ── */}
      <section style={{ padding:"80px 5% 100px", maxWidth:1100, margin:"0 auto" }}>
        <div style={{ textAlign:"center", marginBottom:56 }}>
          <div className="badge" style={{ marginBottom:16 }}>What KrishiBot can do</div>
          <h2 style={{ fontFamily:"'Sora',sans-serif", fontSize:"clamp(1.8rem,4vw,2.8rem)", fontWeight:800, color:"#e8f0e4", letterSpacing:"-0.02em" }}>
            Everything a farmer needs
          </h2>
        </div>
        <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(280px, 1fr))", gap:18 }}>
          {features.map((f, i) => (
            <div key={i} className="feature-card" onMouseEnter={() => setHoveredFeature(i)} onMouseLeave={() => setHoveredFeature(null)}>
              <div style={{ fontSize:"2rem", marginBottom:14, transition:"transform 0.2s", transform:hoveredFeature===i?"scale(1.15)":"scale(1)", display:"inline-block" }}>{f.icon}</div>
              <h3 style={{ fontFamily:"'Sora',sans-serif", fontWeight:700, fontSize:"1rem", color:"#e8f0e4", marginBottom:8 }}>{f.title}</h3>
              <p style={{ color:"rgba(232,240,228,0.45)", fontSize:"0.88rem", lineHeight:1.6 }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA BANNER ── */}
      <section style={{ margin:"0 5% 100px", background:"linear-gradient(135deg,rgba(74,124,89,0.18),rgba(106,170,122,0.08))", border:"1px solid rgba(106,170,122,0.2)", borderRadius:28, padding:"60px 40px", textAlign:"center", position:"relative", overflow:"hidden" }}>
        <div style={{ position:"absolute", inset:0, background:"radial-gradient(ellipse at 50% 0%,rgba(106,170,122,0.12),transparent 60%)", pointerEvents:"none" }} />
        <h2 style={{ fontFamily:"'Sora',sans-serif", fontSize:"clamp(1.6rem,3.5vw,2.4rem)", fontWeight:800, color:"#e8f0e4", marginBottom:14, letterSpacing:"-0.02em" }}>
          Start farming smarter today
        </h2>
        <p style={{ color:"rgba(232,240,228,0.5)", marginBottom:32, fontSize:"1rem" }}>No app download. No subscription. Just ask.</p>
        <button className="cta-btn" onClick={onEnter}>Open KrishiBot 🌾</button>
      </section>

      {/* ── FOOTER ── */}
      <footer style={{ borderTop:"1px solid rgba(106,170,122,0.1)", padding:"28px 5%", display:"flex", alignItems:"center", justifyContent:"space-between", flexWrap:"wrap", gap:12, color:"rgba(232,240,228,0.3)", fontSize:"0.82rem" }}>
        <div style={{ display:"flex", alignItems:"center", gap:8 }}>
          <span>🌾</span><span style={{ fontWeight:700 }}>KrishiBot</span><span>— Built for Indian farmers</span>
        </div>
        <div>Kisan Call Center: 1800-180-1551 (Free, 24x7)</div>
      </footer>
    </div>
  );
}
