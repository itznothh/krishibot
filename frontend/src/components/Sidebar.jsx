import { useNavigate, useLocation } from "react-router-dom";

const NAV_ITEMS = [
  { path: "/",        icon: "🌾", label: "Home" },
  { path: "/chat",    icon: "💬", label: "Chat" },
  { path: "/mandi",   icon: "🏪", label: "Mandi Prices" },
  { path: "/schemes", icon: "📋", label: "Schemes & Loans" },
];

export default function Sidebar({ user, onSignOut, onChatClick }) {
  const navigate = useNavigate();
  const { pathname } = useLocation();

  return (
    <>
      <style>{`
        .sidebar { width: 220px; min-height: 100vh; background: rgba(14,21,16,0.97); border-right: 1px solid rgba(106,170,122,0.12); display: flex; flex-direction: column; padding: 24px 0; position: fixed; top: 0; left: 0; z-index: 40; font-family: 'Nunito', sans-serif; }
        .sidebar-logo { display: flex; align-items: center; gap: 10px; padding: 0 20px 24px; border-bottom: 1px solid rgba(106,170,122,0.1); margin-bottom: 12px; }
        .sidebar-logo span { font-family: 'Sora', sans-serif; font-weight: 800; font-size: 1.1rem; color: #e8f0e4; }
        .nav-item { display: flex; align-items: center; gap: 12px; padding: 11px 20px; margin: 2px 10px; border-radius: 12px; cursor: pointer; font-size: 0.9rem; font-weight: 700; color: rgba(232,240,228,0.5); transition: all 0.15s; border: none; background: none; width: calc(100% - 20px); text-align: left; }
        .nav-item:hover { background: rgba(106,170,122,0.08); color: #e8f0e4; }
        .nav-item.active { background: rgba(106,170,122,0.15); color: #b5d6a0; border: 1px solid rgba(106,170,122,0.2); }
        .nav-item .icon { font-size: 1.1rem; min-width: 22px; }
        .sidebar-footer { margin-top: auto; padding: 16px 20px; border-top: 1px solid rgba(106,170,122,0.1); }
        .sidebar-user { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
        .signout-btn { width: 100%; padding: 8px 14px; background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.15); border-radius: 10px; color: #f87171; font-family: 'Nunito', sans-serif; font-weight: 700; font-size: 0.85rem; cursor: pointer; transition: all 0.15s; }
        .signout-btn:hover { background: rgba(239,68,68,0.15); }
        .sidebar-content { margin-left: 220px; }
        @media (max-width: 700px) {
          .sidebar { width: 100%; min-height: unset; height: 60px; flex-direction: row; align-items: center; padding: 0 12px; border-right: none; border-bottom: 1px solid rgba(106,170,122,0.12); position: fixed; top: 0; left: 0; right: 0; overflow-x: auto; gap: 4px; }
          .sidebar-logo { display: none; }
          .sidebar-footer { display: none; }
          .nav-item { padding: 8px 12px; margin: 0; font-size: 0.78rem; white-space: nowrap; border-radius: 20px; }
          .sidebar-content { margin-left: 0; margin-top: 60px; }
        }
      `}</style>

      <nav className="sidebar">
        <div className="sidebar-logo">
          <span>🌾</span>
          <span>KrishiBot</span>
        </div>

        {NAV_ITEMS.map(item => {
          const isActive = pathname === item.path;
          const isChat = item.path === "/chat";
          return (
            <button
              key={item.path}
              className={`nav-item ${isActive ? "active" : ""}`}
              onClick={() => {
                if (isChat && onChatClick) onChatClick();
                else navigate(item.path);
              }}
            >
              <span className="icon">{item.icon}</span>
              {item.label}
            </button>
          );
        })}

        <div className="sidebar-footer">
          {user ? (
            <>
              <div className="sidebar-user">
                {user.photoURL && <img src={user.photoURL} style={{ width: 32, height: 32, borderRadius: "50%" }} alt="" />}
                <div>
                  <div style={{ fontSize: "0.88rem", fontWeight: 700, color: "#e8f0e4" }}>{user.displayName?.split(" ")[0]}</div>
                  <div style={{ fontSize: "0.75rem", color: "rgba(232,240,228,0.4)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: 130 }}>{user.email}</div>
                </div>
              </div>
              <button className="signout-btn" onClick={onSignOut}>🚪 Sign out</button>
            </>
          ) : (
            <div style={{ fontSize: "0.82rem", color: "rgba(232,240,228,0.3)", textAlign: "center" }}>Not signed in</div>
          )}
        </div>
      </nav>
    </>
  );
}
