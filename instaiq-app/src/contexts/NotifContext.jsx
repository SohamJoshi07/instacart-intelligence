import { createContext, useContext, useState, useCallback } from "react";
import { INITIAL_NOTIFICATIONS } from "../lib/constants";

const NotifContext = createContext(null);

export function NotifProvider({ children }) {
  const [notifs, setNotifs]     = useState(INITIAL_NOTIFICATIONS);
  const [panelOpen, setPanelOpen] = useState(false);

  const unreadCount = notifs.filter(n => !n.read).length;

  const markAllRead = useCallback(() => {
    setNotifs(n => n.map(x => ({ ...x, read: true })));
  }, []);

  const markRead = useCallback((id) => {
    setNotifs(n => n.map(x => x.id === id ? { ...x, read: true } : x));
  }, []);

  const dismiss = useCallback((id) => {
    setNotifs(n => n.filter(x => x.id !== id));
  }, []);

  return (
    <NotifContext.Provider value={{ notifs, unreadCount, panelOpen, setPanelOpen, markAllRead, markRead, dismiss }}>
      {children}
    </NotifContext.Provider>
  );
}

export function useNotif() {
  const ctx = useContext(NotifContext);
  if (!ctx) throw new Error("useNotif must be inside NotifProvider");
  return ctx;
}