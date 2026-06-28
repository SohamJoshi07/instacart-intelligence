import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import NavItem   from "./NavItem";
import StatusDot from "./StatusDot";
import { IcGrid, IcUser, IcBasket, IcChat, IcReport, IcX } from "../ui/icons";
import { useAuth } from "../../contexts/AuthContext";
import { TEAM_MEMBERS } from "../../lib/constants";

const NAV = [
  { to: "/",         label: "Dashboard",    icon: <IcGrid   className="w-4 h-4" /> },
  { to: "/explorer", label: "User Explorer",icon: <IcUser   className="w-4 h-4" /> },
  { to: "/basket",   label: "Basket",       icon: <IcBasket className="w-4 h-4" /> },
  { to: "/chat",     label: "AI Chat",      icon: <IcChat   className="w-4 h-4" /> },
  { to: "/report",   label: "Weekly Report",icon: <IcReport className="w-4 h-4" /> },
];

const NAV2 = [
  { to: "/activity", label: "Activity Log", icon: <IcGrid   className="w-4 h-4" /> },
  { to: "/settings", label: "Settings",     icon: <IcUser   className="w-4 h-4" /> },
];

function Clock() {
  const [t, setT] = React.useState(new Date());
  React.useEffect(() => {
    const id = setInterval(() => setT(new Date()), 1000);
    return () => clearInterval(id);
  }, []);
  return (
    <span className="font-mono text-[10px] text-muted tracking-wider">
      {t.toLocaleTimeString("en-IN", { hour12: false })} IST
    </span>
  );
}

export default function Sidebar({ open, onClose }) {
  const { user } = useAuth();

  return (
    <>
      <AnimatePresence>
        {open && (
          <motion.div
            className="fixed inset-0 bg-black/70 z-30 lg:hidden"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={onClose}
          />
        )}
      </AnimatePresence>

      <aside className={`fixed lg:sticky top-0 left-0 h-screen w-56 z-40 bg-surface border-r border-border flex flex-col transition-transform duration-200 ${open ? "translate-x-0" : "-translate-x-full"} lg:translate-x-0`}>

        {/* Logo + clock */}
        <div className="px-4 py-5 border-b border-border">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="w-5 h-5 bg-brand flex items-center justify-center text-[9px] font-mono font-bold text-white">iQ</div>
              <span className="font-mono text-[13px] font-bold tracking-widest text-white uppercase">InstaIQ</span>
            </div>
            <button onClick={onClose} className="lg:hidden text-muted hover:text-white">
              <IcX className="w-4 h-4" />
            </button>
          </div>
          <Clock />
        </div>

        {/* Main nav */}
        <nav className="px-2 py-3 border-b border-border">
          <p className="px-2 mb-1 text-[9px] font-mono tracking-widest text-border uppercase">Platform</p>
          {NAV.map(n => <NavItem key={n.to} {...n} />)}
        </nav>

        {/* Secondary nav */}
        <nav className="px-2 py-3 border-b border-border">
          <p className="px-2 mb-1 text-[9px] font-mono tracking-widest text-border uppercase">Workspace</p>
          {NAV2.map(n => <NavItem key={n.to} {...n} />)}
        </nav>

        {/* Team online */}
        <div className="px-4 py-3 border-b border-border flex-1 overflow-y-auto">
          <p className="text-[9px] font-mono tracking-widest text-border uppercase mb-2">Team Online</p>
          <div className="space-y-2">
            {TEAM_MEMBERS.map(m => (
              <div key={m.name} className="flex items-center gap-2">
                <div className="relative flex-shrink-0">
                  <div className="w-6 h-6 bg-panel border border-border flex items-center justify-center font-mono text-[9px] text-muted">
                    {m.avatar}
                  </div>
                  <span className={`absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full border border-surface ${m.online ? "bg-green-500" : "bg-border"}`} />
                </div>
                <div className="min-w-0">
                  <p className="font-mono text-[10px] text-white leading-none truncate">{m.name.split(" ")[0]}</p>
                  <p className="font-mono text-[9px] text-border leading-none mt-0.5 truncate">{m.role}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* User footer */}
        <div className="px-4 py-3 border-t border-border space-y-2">
          <StatusDot />
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-brand flex items-center justify-center font-mono text-[9px] font-bold text-white flex-shrink-0">
              {user?.avatar}
            </div>
            <div className="min-w-0">
              <p className="font-mono text-[10px] text-white leading-none truncate">{user?.name}</p>
              <p className="font-mono text-[9px] text-muted leading-none mt-0.5 truncate">{user?.role}</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}