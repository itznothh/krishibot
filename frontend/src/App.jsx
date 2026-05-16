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

  // Still checking auth state
  if (loading) {
    return (
      <div className="min-h-screen bg-[#050d05] flex items-center justify-center">
        <div className="text-green-500 text-lg animate-pulse">🌾 Loading KrishiBot…</div>
      </div>
    );
  }

  // Logged in → show chat
  if (user) {
    return <ChatUI user={user} onSignOut={() => signOut(auth)} />;
  }

  // Not logged in → landing + optional modal
  return (
    <>
      <Landing onLoginClick={() => setShowLogin(true)} />
      {showLogin && <LoginModal onClose={() => setShowLogin(false)} />}
    </>
  );
}
