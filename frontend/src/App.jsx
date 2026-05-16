import { useState } from "react";
import { signOut } from "firebase/auth";
import { auth } from "./firebase";
import { useAuth } from "./hooks/useAuth";
import Landing from "./components/Landing";
import LoginModal from "./components/LoginModal";

export default function App() {
  const { user, loading } = useAuth();
  const [showLogin, setShowLogin] = useState(false);
  const [showChat, setShowChat] = useState(false);

  if (loading) {
    return (
      <div style={{ minHeight:"100vh", background:"#141a12", display:"flex", alignItems:"center", justifyContent:"center" }}>
        <div style={{ color:"#6aaa7a", fontSize:"1.2rem", fontFamily:"sans-serif" }}>🌾 Loading KrishiBot…</div>
      </div>
    );
  }

  // Chat view (Phase 3 — coming soon)
  if (showChat) {
    return (
      <div style={{ minHeight:"100vh", background:"#141a12", display:"flex", alignItems:"center", justifyContent:"center", flexDirection:"column", gap:16, fontFamily:"sans-serif" }}>
        <div style={{ fontSize:"3rem" }}>🌾</div>
        <div style={{ color:"#6aaa7a", fontSize:"1.2rem", fontWeight:700 }}>Chat UI coming in Phase 3!</div>
        <button onClick={() => setShowChat(false)} style={{ marginTop:8, color:"rgba(232,240,228,0.4)", background:"none", border:"none", cursor:"pointer", fontSize:"0.9rem" }}>
          ← Back to home
        </button>
      </div>
    );
  }

  return (
    <>
      <Landing
        user={user}
        onEnter={() => setShowChat(true)}
        onLoginClick={() => setShowLogin(true)}
        onSignOut={() => signOut(auth)}
      />
      {showLogin && <LoginModal onClose={() => setShowLogin(false)} />}
    </>
  );
}
