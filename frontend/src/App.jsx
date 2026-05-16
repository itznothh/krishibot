import { useState } from "react";
import { signOut } from "firebase/auth";
import { auth } from "./firebase";
import { useAuth } from "./hooks/useAuth";
import Landing from "./components/Landing";
import LoginModal from "./components/LoginModal";
import ChatUI from "./components/ChatUI";

export default function App() {
  const { user, loading } = useAuth();
  const [showLogin, setShowLogin] = useState(false);
  const [showChat, setShowChat]   = useState(false);

  if (loading) {
    return (
      <div style={{ minHeight:"100vh", background:"#0e1510", display:"flex", alignItems:"center", justifyContent:"center" }}>
        <div style={{ color:"#6aaa7a", fontSize:"1.1rem", fontFamily:"'Nunito',sans-serif" }}>🌾 Loading KrishiBot…</div>
      </div>
    );
  }

  const handleEnter = () => {
    if (!user) { setShowLogin(true); return; }
    setShowChat(true);
  };

  if (showChat && user) {
    return (
      <ChatUI
        user={user}
        onSignOut={() => { signOut(auth); setShowChat(false); }}
        onBack={() => setShowChat(false)}
      />
    );
  }

  return (
    <>
      <Landing
        user={user}
        onEnter={handleEnter}
        onLoginClick={() => setShowLogin(true)}
        onSignOut={() => signOut(auth)}
      />
      {showLogin && <LoginModal onClose={() => setShowLogin(false)} />}
    </>
  );
}
