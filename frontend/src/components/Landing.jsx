import { useState, useEffect, useRef } from "react";

const features = [
  {
    icon: "🌾",
    title: "Crop Advisor",
    desc: "Get season & soil-specific crop recommendations instantly.",
  },
  {
    icon: "🐛",
    title: "Pest & Disease",
    desc: "Identify pests, diseases and get step-by-step treatment plans.",
  },
  {
    icon: "📸",
    title: "Disease Scanner",
    desc: "Upload a photo of your crop — AI diagnoses the problem.",
  },
  {
    icon: "🌦️",
    title: "Weather Alerts",
    desc: "Real-time hyperlocal weather with farming-specific advice.",
  },
  {
    icon: "🧪",
    title: "Fertilizer Guide",
    desc: "Exact NPK ratios, chemical & organic options per crop.",
  },
  {
    icon: "💬",
    title: "3 Languages",
    desc: "Ask in English, Hindi or Kannada — KrishiBot understands.",
  },
];

const stats = [
  { value: "3", label: "Languages" },
  { value: "7+", label: "Crop Modules" },
  { value: "24/7", label: "Available" },
  { value: "Free", label: "Always" },
];

// Floating particle
function Particle({ style }) {
  return (
    <div
      style={{
        position: "absolute",
        width: 6,
        height: 6,
        borderRadius: "50%",
        background: "rgba(106,170,122,0.35)",
        ...style,
      }}
    />
  );
}

export default function Landing({ onEnter }) {
  const [visible, setVisible] = useState(false);
  const [hoveredFeature, setHoveredFeature] = useState(null);
  const [email, setEmail] = useState("");
  const [showLogin, setShowLogin] = useState(false);
  const canvasRef = useRef(null);

  useEffect(() => {
    setTimeout(() => setVisible(true), 100);
  }, []);

  // Animated grain canvas
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
        imageData.data[i] = v;
        imageData.data[i + 1] = v;
        imageData.data[i + 2] = v;
        imageData.data[i + 3] = 8;
      }
      ctx.putImageData(imageData, 0, 0);
      frame = requestAnimationFrame(draw);
    };
    draw();
    return () => cancelAnimationFrame(frame);
  }, []);

  const particles = Array.from({ length: 18 }, (_, i) => ({
    top: `${Math.random() * 100}%`,
    left: `${Math.random() * 100}%`,
    animation: `float${i % 3} ${4 + (i % 4)}s ease-in-out infinite`,
    animationDelay: `${(i * 0.4) % 3}s`,
    opacity: 0.4 + (i % 3) * 0.15,
  }));

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#141a12",
        fontFamily: "'Nunito', sans-serif",
        color: "#e8f0e4",
        overflowX: "hidden",
        position: "relative",
      }}
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');

        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(32px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeIn {
          from { opacity: 0; } to { opacity: 1; }
        }
        @keyframes float0 {
          0%,100% { transform: translateY(0px); }
          50%      { transform: translateY(-14px); }
        }
        @keyframes float1 {
          0%,100% { transform: translateY(0px) translateX(0px); }
          50%      { transform: translateY(-10px) translateX(8px); }
        }
        @keyframes float2 {
          0%,100% { transform: translateY(0px); }
          50%      { transform: translateY(-18px); }
        }
        @keyframes pulse {
          0%,100% { opacity: 0.6; transform: scale(1); }
          50%      { opacity: 1;   transform: scale(1.04); }
        }
        @keyframes shimmer {
          0%   { background-position: -200% center; }
          100% { background-position:  200% center; }
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to   { transform: rotate(360deg); }
        }
        .hero-title {
          font-family: 'Sora', sans-serif;
          font-size: clamp(2.6rem, 6vw, 5rem);
          font-weight: 800;
          line-height: 1.08;
          letter-spacing: -0.03em;
        }
        .green-shimmer {
          background: linear-gradient(90deg, #6aaa7a 0%, #b5d6a0 40%, #6aaa7a 60%, #4a7c59 100%);
          background-size: 200% auto;
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          animation: shimmer 3.5s linear infinite;
        }
        .cta-btn {
          display: inline-flex;
          align-items: center;
          gap: 10px;
          padding: 16px 38px;
          background: linear-gradient(135deg, #4a7c59, #6aaa7a);
          color: #fff;
          font-family: 'Nunito', sans-serif;
          font-weight: 800;
          font-size: 1.05rem;
          border: none;
          border-radius: 50px;
          cursor: pointer;
          box-shadow: 0 8px 32px rgba(74,124,89,0.4);
          transition: transform 0.18s, box-shadow 0.18s;
          letter-spacing: 0.01em;
        }
        .cta-btn:hover {
          transform: translateY(-3px) scale(1.03);
          box-shadow: 0 14px 40px rgba(74,124,89,0.55);
        }
        .login-btn {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          padding: 12px 28px;
          background: transparent;
          color: #8fbc8f;
          font-family: 'Nunito', sans-serif;
          font-weight: 700;
          font-size: 0.95rem;
          border: 1.5px solid rgba(143,188,143,0.3);
          border-radius: 50px;
          cursor: pointer;
          transition: all 0.18s;
        }
        .login-btn:hover {
          background: rgba(143,188,143,0.08);
          border-color: rgba(143,188,143,0.6);
          color: #b5d6a0;
        }
        .feature-card {
          background: rgba(255,255,255,0.03);
          border: 1px solid rgba(106,170,122,0.12);
          border-radius: 20px;
          padding: 28px 24px;
          transition: all 0.22s;
          cursor: default;
          position: relative;
          overflow: hidden;
        }
        .feature-card:hover {
          background: rgba(106,170,122,0.06);
          border-color: rgba(106,170,122,0.3);
          transform: translateY(-4px);
          box-shadow: 0 12px 40px rgba(74,124,89,0.18);
        }
        .feature-card::before {
          content: '';
          position: absolute;
          top: 0; left: 0; right: 0;
          height: 1px;
          background: linear-gradient(90deg, transparent, rgba(106,170,122,0.4), transparent);
          opacity: 0;
          transition: opacity 0.22s;
        }
        .feature-card:hover::before { opacity: 1; }
        .stat-item {
          text-align: center;
          padding: 24px 16px;
        }
        .stat-value {
          font-family: 'Sora', sans-serif;
          font-size: 2.4rem;
          font-weight: 800;
          color: #6aaa7a;
          line-height: 1;
        }
        .stat-label {
          font-size: 0.82rem;
          color: rgba(232,240,228,0.5);
          margin-top: 4px;
          font-weight: 600;
          letter-spacing: 0.08em;
          text-transform: uppercase;
        }
        .orb {
          position: absolute;
          border-radius: 50%;
          filter: blur(80px);
          pointer-events: none;
          animation: pulse 6s ease-in-out infinite;
        }
        .nav-link {
          color: rgba(232,240,228,0.55);
          font-weight: 600;
          font-size: 0.9rem;
          text-decoration: none;
          cursor: pointer;
          transition: color 0.15s;
          background: none;
          border: none;
        }
        .nav-link:hover { color: #8fbc8f; }
        .modal-overlay {
          position: fixed;
          inset: 0;
          background: rgba(0,0,0,0.7);
          backdrop-filter: blur(8px);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          animation: fadeIn 0.18s ease;
        }
        .modal-box {
          background: #1c2419;
          border: 1px solid rgba(106,170,122,0.2);
          border-radius: 24px;
          padding: 40px 36px;
          width: 90%;
          max-width: 420px;
          box-shadow: 0 32px 80px rgba(0,0,0,0.5);
          animation: fadeUp 0.22s ease;
        }
        .input-field {
          width: 100%;
          background: rgba(255,255,255,0.05);
          border: 1px solid rgba(106,170,122,0.2);
          border-radius: 12px;
          padding: 13px 16px;
          color: #e8f0e4;
          font-family: 'Nunito', sans-serif;
          font-size: 0.95rem;
          outline: none;
          transition: border-color 0.15s;
          box-sizing: border-box;
        }
        .input-field:focus { border-color: rgba(106,170,122,0.55); }
        .input-field::placeholder { color: rgba(232,240,228,0.3); }
        .google-btn {
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 10px;
          padding: 13px;
          background: rgba(255,255,255,0.06);
          border: 1px solid rgba(255,255,255,0.1);
          border-radius: 12px;
          color: #e8f0e4;
          font-family: 'Nunito', sans-serif;
          font-weight: 700;
          font-size: 0.95rem;
          cursor: pointer;
          transition: all 0.18s;
        }
        .google-btn:hover {
          background: rgba(255,255,255,0.1);
          border-color: rgba(255,255,255,0.2);
        }
        .divider {
          display: flex;
          align-items: center;
          gap: 12px;
          color: rgba(232,240,228,0.25);
          font-size: 0.8rem;
          margin: 16px 0;
        }
        .divider::before, .divider::after {
          content: '';
          flex: 1;
          height: 1px;
          background: rgba(255,255,255,0.08);
        }
        .badge {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 6px 14px;
          background: rgba(106,170,122,0.1);
          border: 1px solid rgba(106,170,122,0.2);
          border-radius: 50px;
          font-size: 0.78rem;
          font-weight: 700;
          color: #8fbc8f;
          letter-spacing: 0.06em;
          text-transform: uppercase;
        }
        .whatsapp-pill {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          padding: 10px 20px;
          background: rgba(37,211,102,0.1);
          border: 1px solid rgba(37,211,102,0.25);
          border-radius: 50px;
          font-size: 0.85rem;
          font-weight: 700;
          color: #25d366;
          cursor: pointer;
          transition: all 0.18s;
          text-decoration: none;
        }
        .whatsapp-pill:hover {
          background: rgba(37,211,102,0.18);
          transform: translateY(-2px);
        }
      `}</style>

      {/* Grain overlay */}
      <canvas
        ref={canvasRef}
        style={{
          position: "fixed",
          inset: 0,
          width: "100%",
          height: "100%",
          pointerEvents: "none",
          zIndex: 99,
          opacity: 0.55,
        }}
      />

      {/* Ambient orbs */}
      <div className="orb" style={{ width: 500, height: 500, background: "rgba(74,124,89,0.12)", top: -100, right: -100 }} />
      <div className="orb" style={{ width: 400, height: 400, background: "rgba(212,168,83,0.07)", bottom: 200, left: -150, animationDelay: "3s" }} />
      <div className="orb" style={{ width: 300, height: 300, background: "rgba(106,170,122,0.08)", top: "40%", left: "40%", animationDelay: "1.5s" }} />

      {/* Floating particles */}
      {particles.map((p, i) => (
        <Particle key={i} style={p} />
      ))}

      {/* ── NAV ── */}
      <nav
        style={{
          position: "fixed",
          top: 0, left: 0, right: 0,
          zIndex: 100,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "18px 5%",
          background: "rgba(20,26,18,0.75)",
          backdropFilter: "blur(20px)",
          borderBottom: "1px solid rgba(106,170,122,0.1)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{ fontSize: "1.5rem" }}>🌾</span>
          <span style={{ fontFamily: "'Sora', sans-serif", fontWeight: 700, fontSize: "1.1rem", color: "#e8f0e4" }}>
            KrishiBot
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
          <button className="nav-link">Features</button>
          <button className="nav-link">About</button>
          <button className="login-btn" onClick={() => setShowLogin(true)}>
            Sign in
          </button>
        </div>
      </nav>

      {/* ── HERO ── */}
      <section
        style={{
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          textAlign: "center",
          padding: "120px 5% 80px",
          position: "relative",
        }}
      >
        <div
          style={{
            opacity: visible ? 1 : 0,
            animation: visible ? "fadeUp 0.7s ease forwards" : "none",
          }}
        >
          <div style={{ marginBottom: 20 }}>
            <span className="badge">🇮🇳 Made for Indian Farmers</span>
          </div>

          <h1 className="hero-title" style={{ marginBottom: 20, maxWidth: 780, margin: "0 auto 20px" }}>
            Your AI farming<br />
            <span className="green-shimmer">companion</span>
          </h1>

          <p
            style={{
              fontSize: "clamp(1rem, 2vw, 1.2rem)",
              color: "rgba(232,240,228,0.55)",
              maxWidth: 560,
              margin: "0 auto 40px",
              lineHeight: 1.65,
              fontWeight: 500,
            }}
          >
            Ask crop questions in Hindi, Kannada or English. Get pest advice,
            fertilizer plans, weather alerts — all in one place. Free, always.
          </p>

          <div style={{ display: "flex", gap: 14, justifyContent: "center", flexWrap: "wrap", marginBottom: 40 }}>
            <button className="cta-btn" onClick={onEnter}>
              Start Chatting
              <span style={{ fontSize: "1.1rem" }}>→</span>
            </button>
            <button className="login-btn" onClick={() => setShowLogin(true)}>
              Sign in / Register
            </button>
          </div>

          <a
            href="https://wa.me/your-number"
            className="whatsapp-pill"
            target="_blank"
            rel="noopener noreferrer"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
            </svg>
            Also on WhatsApp
          </a>
        </div>

        {/* Stats row */}
        <div
          style={{
            display: "flex",
            gap: 0,
            marginTop: 70,
            borderTop: "1px solid rgba(106,170,122,0.1)",
            borderBottom: "1px solid rgba(106,170,122,0.1)",
            width: "100%",
            maxWidth: 700,
            opacity: visible ? 1 : 0,
            animation: visible ? "fadeUp 0.8s 0.3s ease both" : "none",
          }}
        >
          {stats.map((s, i) => (
            <div
              key={i}
              className="stat-item"
              style={{
                flex: 1,
                borderRight: i < stats.length - 1 ? "1px solid rgba(106,170,122,0.1)" : "none",
              }}
            >
              <div className="stat-value">{s.value}</div>
              <div className="stat-label">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── FEATURES ── */}
      <section style={{ padding: "80px 5% 100px", maxWidth: 1100, margin: "0 auto" }}>
        <div style={{ textAlign: "center", marginBottom: 56 }}>
          <div className="badge" style={{ marginBottom: 16 }}>What KrishiBot can do</div>
          <h2
            style={{
              fontFamily: "'Sora', sans-serif",
              fontSize: "clamp(1.8rem, 4vw, 2.8rem)",
              fontWeight: 800,
              color: "#e8f0e4",
              letterSpacing: "-0.02em",
            }}
          >
            Everything a farmer needs
          </h2>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
            gap: 18,
          }}
        >
          {features.map((f, i) => (
            <div
              key={i}
              className="feature-card"
              onMouseEnter={() => setHoveredFeature(i)}
              onMouseLeave={() => setHoveredFeature(null)}
              style={{
                animationDelay: `${i * 0.08}s`,
              }}
            >
              <div
                style={{
                  fontSize: "2rem",
                  marginBottom: 14,
                  transition: "transform 0.2s",
                  transform: hoveredFeature === i ? "scale(1.15)" : "scale(1)",
                  display: "inline-block",
                }}
              >
                {f.icon}
              </div>
              <h3
                style={{
                  fontFamily: "'Sora', sans-serif",
                  fontWeight: 700,
                  fontSize: "1rem",
                  color: "#e8f0e4",
                  marginBottom: 8,
                }}
              >
                {f.title}
              </h3>
              <p style={{ color: "rgba(232,240,228,0.45)", fontSize: "0.88rem", lineHeight: 1.6 }}>
                {f.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA BANNER ── */}
      <section
        style={{
          margin: "0 5% 100px",
          background: "linear-gradient(135deg, rgba(74,124,89,0.18), rgba(106,170,122,0.08))",
          border: "1px solid rgba(106,170,122,0.2)",
          borderRadius: 28,
          padding: "60px 40px",
          textAlign: "center",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: "radial-gradient(ellipse at 50% 0%, rgba(106,170,122,0.12), transparent 60%)",
            pointerEvents: "none",
          }}
        />
        <h2
          style={{
            fontFamily: "'Sora', sans-serif",
            fontSize: "clamp(1.6rem, 3.5vw, 2.4rem)",
            fontWeight: 800,
            color: "#e8f0e4",
            marginBottom: 14,
            letterSpacing: "-0.02em",
          }}
        >
          Start farming smarter today
        </h2>
        <p style={{ color: "rgba(232,240,228,0.5)", marginBottom: 32, fontSize: "1rem" }}>
          No app download. No subscription. Just ask.
        </p>
        <button className="cta-btn" onClick={onEnter}>
          Open KrishiBot 🌾
        </button>
      </section>

      {/* ── FOOTER ── */}
      <footer
        style={{
          borderTop: "1px solid rgba(106,170,122,0.1)",
          padding: "28px 5%",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: 12,
          color: "rgba(232,240,228,0.3)",
          fontSize: "0.82rem",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span>🌾</span>
          <span style={{ fontWeight: 700 }}>KrishiBot</span>
          <span>— Built for Indian farmers</span>
        </div>
        <div>Kisan Call Center: 1800-180-1551 (Free, 24x7)</div>
      </footer>

      {/* ── LOGIN MODAL ── */}
      {showLogin && (
        <div className="modal-overlay" onClick={() => setShowLogin(false)}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()}>
            <button
              onClick={() => setShowLogin(false)}
              style={{
                position: "absolute",
                top: 16, right: 20,
                background: "none",
                border: "none",
                color: "rgba(232,240,228,0.4)",
                fontSize: "1.4rem",
                cursor: "pointer",
                lineHeight: 1,
              }}
            >
              ×
            </button>

            <div style={{ textAlign: "center", marginBottom: 28 }}>
              <span style={{ fontSize: "2rem" }}>🌾</span>
              <h2
                style={{
                  fontFamily: "'Sora', sans-serif",
                  fontWeight: 800,
                  fontSize: "1.4rem",
                  color: "#e8f0e4",
                  margin: "10px 0 4px",
                }}
              >
                Welcome back
              </h2>
              <p style={{ color: "rgba(232,240,228,0.4)", fontSize: "0.88rem" }}>
                Sign in to save your farm profile
              </p>
            </div>

            {/* Google OAuth button */}
            <button className="google-btn" onClick={onEnter}>
              <svg width="18" height="18" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Continue with Google
            </button>

            <div className="divider">or</div>

            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <input
                className="input-field"
                type="email"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <input
                className="input-field"
                type="password"
                placeholder="Password"
              />
              <button className="cta-btn" style={{ width: "100%", justifyContent: "center" }} onClick={onEnter}>
                Sign in
              </button>
            </div>

            <p
              style={{
                textAlign: "center",
                marginTop: 16,
                fontSize: "0.82rem",
                color: "rgba(232,240,228,0.35)",
              }}
            >
              Don't have an account?{" "}
              <span style={{ color: "#8fbc8f", cursor: "pointer", fontWeight: 700 }}>
                Register free
              </span>
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
