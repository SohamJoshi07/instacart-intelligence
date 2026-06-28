import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "../../contexts/AuthContext";
import { useNotif } from "../../contexts/NotifContext";
import { IcMenu, IcSearch } from "../ui/icons";

function BellIcon() {
  return (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
      <path d="M13.73 21a2 2 0 0 1-3.46 0" />
    </svg>
  );
}

function LogoutIcon() {
  return (
    <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
      <polyline points="16 17 21 12 16 7" />
      <line x1="21" y1="12" x2="9" y2="12" />
    </svg>
  );
}

const MENU_ITEMS = [
  { label: "Profile & Settings", path: "/settings" },
  { label: "Activity Log", path: "/activity" },
];

export default function TopBar({ title, subtitle, onMenuClick, onCommandPalette, topRight }) {
  const { user, logout } = useAuth();
  const { unreadCount, setPanelOpen } = useNotif();
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  useEffect(() => {
    if (!userMenuOpen) return;
    const handler = () => setUserMenuOpen(false);
    window.addEventListener("click", handler);
    return () => window.removeEventListener("click", handler);
  }, [userMenuOpen]);

  return (
    <div className="flex items-start justify-between mb-6 gap-4">

      <div className="flex items-center gap-3 min-w-0">
        <button onClick={onMenuClick} className="lg:hidden text-muted hover:text-white flex-shrink-0">
          <IcMenu className="w-5 h-5" />
        </button>
        <div className="min-w-0">
          <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-muted mb-0.5">{subtitle}</p>
          <h2 className="font-sans text-xl font-semibold text-white leading-tight truncate">{title}</h2>
        </div>
      </div>

      <div className="flex items-center gap-2 flex-shrink-0">

        {topRight}

        <button
          onClick={onCommandPalette}
          className="hidden sm:flex items-center gap-2 border border-border bg-surface px-3 py-1.5 font-mono text-[10px] text-muted hover:border-white/30 hover:text-white transition-colors"
        >
          <IcSearch className="w-3 h-3" />
          <span className="uppercase tracking-widest">Search</span>
          <kbd className="text-[9px] text-border border border-border px-1 py-0.5">Cmd K</kbd>
        </button>

        <button
          onClick={() => setPanelOpen(true)}
          className="relative p-2 text-muted hover:text-white transition-colors border border-transparent hover:border-border"
        >
          <BellIcon />
          {unreadCount > 0 && (
            <motion.span
              className="absolute top-1 right-1 w-3.5 h-3.5 bg-brand flex items-center justify-center font-mono text-[8px] text-white font-bold"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
            >
              {unreadCount}
            </motion.span>
          )}
        </button>

        <div className="relative" onClick={(e) => e.stopPropagation()}>
          <button
            onClick={() => setUserMenuOpen((o) => !o)}
            className="flex items-center gap-2 border border-border bg-surface px-2.5 py-1.5 hover:border-white/30 transition-colors"
          >
            <div className="w-6 h-6 bg-brand flex items-center justify-center font-mono text-[9px] font-bold text-white">
              {user?.avatar || "??"}
            </div>
            <div className="hidden sm:block text-left">
              <p className="font-mono text-[10px] text-white leading-none">{user?.name?.split(" ")[0]}</p>
              <p className="font-mono text-[9px] text-muted leading-none mt-0.5">BI Lead</p>
            </div>
          </button>

          <AnimatePresence>
            {userMenuOpen && (
              <motion.div
                className="absolute right-0 top-full mt-1 w-56 bg-surface border border-border shadow-xl z-50"
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -4 }}
                transition={{ duration: 0.12 }}
              >
                <div className="px-3 py-3 border-b border-border">
                  <p className="font-mono text-[11px] text-white font-semibold">{user?.name}</p>
                  <p className="font-mono text-[10px] text-muted mt-0.5">{user?.email}</p>
                  <p className="font-mono text-[9px] text-border uppercase tracking-widest mt-1">{user?.role}</p>
                </div>

                <div className="py-1">
                  {MENU_ITEMS.map((item) => (
                    <a
                      key={item.label}
                      href={item.path}
                      className="block px-3 py-2 font-mono text-[11px] text-muted hover:text-white hover:bg-white/[0.04] transition-colors uppercase tracking-widest"
                    >
                      {item.label}
                    </a>
                  ))}
                </div>

                <div className="border-t border-border py-1">
                  <button
                    onClick={logout}
                    className="w-full flex items-center gap-2 px-3 py-2 font-mono text-[11px] text-brand hover:bg-brand/10 transition-colors uppercase tracking-widest"
                  >
                    <LogoutIcon />
                    Sign Out
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

      </div>
    </div>
  );
}
