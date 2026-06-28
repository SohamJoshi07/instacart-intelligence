import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { getHealth } from "../lib/api";

const HealthContext = createContext(null);

export function HealthProvider({ children }) {
  const [state, setState] = useState({ loading: true, ok: false, data: null, error: null });

  const load = useCallback(async () => {
    setState((s) => ({ ...s, loading: true }));
    const res = await getHealth();
    if (res.ok) {
      setState({ loading: false, ok: true, data: res.data, error: null });
    } else {
      setState({ loading: false, ok: false, data: null, error: res.error });
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return <HealthContext.Provider value={{ ...state, reload: load }}>{children}</HealthContext.Provider>;
}

export function useHealth() {
  const ctx = useContext(HealthContext);
  if (!ctx) {
    throw new Error("useHealth must be used within a HealthProvider");
  }
  return ctx;
}
