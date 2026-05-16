export default function ChatUI({ user, onSignOut }) {
  return (
    <div className="min-h-screen bg-[#050d05] flex flex-col items-center justify-center p-6">
      <div className="text-center mb-8">
        <div className="text-5xl mb-3">🌾</div>
        <h1 className="text-3xl font-bold text-green-400">KrishiBot</h1>
        <p className="text-green-700 mt-2 text-sm">
          Namaste, <span className="text-green-400">{user.displayName || user.phoneNumber || "Farmer"}</span>!
        </p>
      </div>

      <div className="w-full max-w-xl bg-[#0f1a0f] border border-green-900/40 rounded-2xl p-6 mb-6">
        <p className="text-green-600 text-center text-sm">
          💬 Chat UI coming in Phase 3 — connecting to Flask backend
        </p>
      </div>

      <button
        onClick={onSignOut}
        className="text-green-800 hover:text-green-600 text-sm transition-colors"
      >
        Sign out
      </button>
    </div>
  );
}
