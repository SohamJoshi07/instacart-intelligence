import { motion, AnimatePresence } from "framer-motion";
import { useNotif } from "../../contexts/NotifContext";
import { IcX, IcAlert } from "../ui/icons";

const TYPE_META = {
  alert:   { color: "#e31837", label: "ALERT"   },
  info:    { color: "#3b82f6", label: "INFO"    },
  mention: { color: "#f59e0b", label: "MENTION" },
  success: { color: "#22c55e", label: "SUCCESS" },
};

export default function NotifPanel() {
  const { notifs, panelOpen, setPanelOpen, markAllRead, markRead, dismiss } = useNotif();

  return (
    <AnimatePresence>
      {panelOpen && (
        <>
          <motion.div
            className="fixed inset-0 z-40"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={() => setPanelOpen(false)}
          />
          <motion.div
            className="fixed top-0 right-0 h-full w-80 bg-surface border-l border-border z-50 flex flex-col"
            initial={{ x: "100%" }} animate={{ x: 0 }} exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 28, stiffness: 300 }}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-4 border-b border-border">
              <div>
                <p className="font-mono text-[10px] uppercase tracking-widest text-muted">Notifications</p>
                <p className="font-sans text-sm font-semibold text-white mt-0.5">{notifs.filter(n => !n.read).length} unread</p>
              </div>
              <div className="flex items-center gap-3">
                <button onClick={markAllRead} className="font-mono text-[9px] text-muted hover:text-white uppercase tracking-widest transition-colors">
                  MARK ALL READ
                </button>
                <button onClick={() => setPanelOpen(false)} className="text-muted hover:text-white transition-colors">
                  <IcX className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* List */}
            <div className="flex-1 overflow-y-auto">
              {notifs.length === 0 && (
                <div className="flex flex-col items-center justify-center h-full gap-2 text-muted">
                  <IcAlert className="w-8 h-8 opacity-20" />
                  <p className="font-mono text-[10px] uppercase tracking-widest">No notifications</p>
                </div>
              )}
              {notifs.map((n, i) => {
                const m = TYPE_META[n.type] || TYPE_META.info;
                return (
                  <motion.div
                    key={n.id}
                    className={`px-4 py-3.5 border-b border-border/50 cursor-pointer hover:bg-panel transition-colors relative ${!n.read ? "bg-white/[0.02]" : ""}`}
                    initial={{ opacity: 0, x: 10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.04 }}
                    onClick={() => markRead(n.id)}
                  >
                    {!n.read && <span className="absolute left-2 top-1/2 -translate-y-1/2 w-1 h-1 rounded-full bg-brand" />}
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <div className="flex items-center gap-1.5">
                        <span className="font-mono text-[8px] uppercase tracking-widest px-1.5 py-0.5" style={{ color: m.color, backgroundColor: `${m.color}18`, border: `1px solid ${m.color}30` }}>
                          {m.label}
                        </span>
                        <span className="font-mono text-[9px] text-border">{n.time}</span>
                      </div>
                      <button
                        onClick={e => { e.stopPropagation(); dismiss(n.id); }}
                        className="text-border hover:text-muted transition-colors flex-shrink-0"
                      >
                        <IcX className="w-3 h-3" />
                      </button>
                    </div>
                    <p className="font-sans text-[12px] font-medium text-white mb-0.5">{n.title}</p>
                    <p className="font-mono text-[10px] text-muted leading-relaxed">{n.body}</p>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}