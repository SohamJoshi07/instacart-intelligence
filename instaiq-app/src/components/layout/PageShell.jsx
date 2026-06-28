import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import TopBar        from "./TopBar";
import CommandPalette from "./CommandPalette";
import NotifPanel    from "./NotifPanel";

export default function PageShell({ title, subtitle, onMenuClick, topRight, children }) {
  const [cmdOpen, setCmdOpen] = useState(false);

  // Global Cmd+K / Ctrl+K listener
  useEffect(() => {
    const handler = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setCmdOpen(o => !o);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  return (
    <>
      <motion.div
        className="flex-1 min-w-0 p-6 max-w-[1400px] w-full mx-auto"
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.2 }}
      >
        <TopBar
          title={title}
          subtitle={subtitle}
          onMenuClick={onMenuClick}
          onCommandPalette={() => setCmdOpen(true)}
          topRight={topRight}
        />
        {children}
      </motion.div>

      <CommandPalette open={cmdOpen} onClose={() => setCmdOpen(false)} />
      <NotifPanel />
    </>
  );
}