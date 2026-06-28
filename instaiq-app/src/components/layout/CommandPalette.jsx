import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { IcSearch, IcGrid, IcUser, IcBasket, IcChat, IcReport } from "../ui/icons";

const COMMANDS = [
  { id: "dash",     label: "Dashboard",        sub: "Platform overview",                 path: "/",         icon: <IcGrid    className="w-3.5 h-3.5" /> },
  { id: "explorer", label: "User Explorer",     sub: "Look up any user segment + recs",  path: "/explorer", icon: <IcUser    className="w-3.5 h-3.5" /> },
  { id: "basket",   label: "Basket Completion", sub: "Find co-purchased products",        path: "/basket",   icon: <IcBasket  className="w-3.5 h-3.5" /> },
  { id: "chat",     label: "Analytics Chat",    sub: "Ask Rohan anything",               path: "/chat",     icon: <IcChat    className="w-3.5 h-3.5" /> },
  { id: "report",   label: "Weekly Report",     sub: "Executive summary",                path: "/report",   icon: <IcReport  className="w-3.5 h-3.5" /> },
  { id: "settings", label: "Settings",          sub: "Profile, API, preferences",        path: "/settings", icon: <IcGrid    className="w-3.5 h-3.5" /> },
  { id: "activity", label: "Activity Log",      sub: "Team audit trail",                 path: "/activity", icon: <IcGrid    className="w-3.5 h-3.5" /> },
];

export default function CommandPalette({ open, onClose }) {
  const [query, setQuery]     = useState("");
  const [selected, setSelected] = useState(0);
  const navigate              = useNavigate();

  const filtered = COMMANDS.filter(c =>
    c.label.toLowerCase().includes(query.toLowerCase()) ||
    c.sub.toLowerCase().includes(query.toLowerCase())
  );

  const go = useCallback((path) => {
    navigate(path);
    onClose();
    setQuery("");
    setSelected(0);
  }, [navigate, onClose]);

  useEffect(() => {
    if (!open) return;
    const handler = (e) => {
      if (e.key === "ArrowDown") { e.preventDefault(); setSelected(s => Math.min(s + 1, filtered.length - 1)); }
      if (e.key === "ArrowUp")   { e.preventDefault(); setSelected(s => Math.max(s - 1, 0)); }
      if (e.key === "Enter")     { e.preventDefault(); if (filtered[selected]) go(filtered[selected].path); }
      if (e.key === "Escape")    onClose();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [open, filtered, selected, go, onClose]);

  useEffect(() => { setSelected(0); }, [query]);

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            className="fixed inset-0 bg-black/70 z-50 backdrop-blur-sm"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <motion.div
            className="fixed top-1/4 left-1/2 -translate-x-1/2 w-full max-w-lg z-50"
            initial={{ opacity: 0, scale: 0.96, y: -8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96 }}
            transition={{ duration: 0.15 }}
          >
            <div className="bg-surface border border-border shadow-2xl overflow-hidden">
              {/* Search input */}
              <div className="flex items-center gap-3 px-4 py-3 border-b border-border">
                <IcSearch className="w-4 h-4 text-muted flex-shrink-0" />
                <input
                  autoFocus
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  placeholder="Search pages, actions…"
                  className="flex-1 bg-transparent font-mono text-[13px] text-white placeholder:text-border outline-none"
                />
                <kbd className="font-mono text-[9px] text-border border border-border px-1.5 py-0.5 uppercase">ESC</kbd>
              </div>

              {/* Results */}
              <div className="py-1 max-h-72 overflow-y-auto">
                {filtered.length === 0 && (
                  <p className="px-4 py-6 font-mono text-[11px] text-border text-center uppercase tracking-widest">No results</p>
                )}
                {filtered.map((c, i) => (
                  <motion.button
                    key={c.id}
                    className={`w-full flex items-center gap-3 px-4 py-2.5 text-left transition-colors ${
                      i === selected ? "bg-white/[0.06]" : "hover:bg-white/[0.03]"
                    }`}
                    onClick={() => go(c.path)}
                    onMouseEnter={() => setSelected(i)}
                    initial={{ opacity: 0, x: -4 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.03 }}
                  >
                    <span className="text-muted">{c.icon}</span>
                    <div className="flex-1 min-w-0">
                      <p className="font-sans text-[13px] text-white font-medium">{c.label}</p>
                      <p className="font-mono text-[10px] text-muted truncate">{c.sub}</p>
                    </div>
                    {i === selected && (
                      <kbd className="font-mono text-[9px] text-border border border-border px-1.5 py-0.5">↵</kbd>
                    )}
                  </motion.button>
                ))}
              </div>

              <div className="px-4 py-2 border-t border-border flex items-center gap-4">
                {[["↑↓", "Navigate"], ["↵", "Open"], ["ESC", "Close"]].map(([k, l]) => (
                  <span key={k} className="flex items-center gap-1.5">
                    <kbd className="font-mono text-[9px] text-border border border-border px-1.5 py-0.5">{k}</kbd>
                    <span className="font-mono text-[9px] text-border uppercase tracking-widest">{l}</span>
                  </span>
                ))}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}