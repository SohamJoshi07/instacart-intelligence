import { createContext, useContext, useState, useCallback } from "react";
import { DEMO_USER } from "../lib/constants";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = sessionStorage.getItem("instaiq_user");
    return saved ? JSON.parse(saved) : null;
  });
  const [error, setError] = useState("");

  const login = useCallback(async (email, password) => {
    setError("");
    // Simulate network delay
    await new Promise(r => setTimeout(r, 1200));
    if (email === DEMO_USER.email && password === DEMO_USER.password) {
      const userData = {
        ...DEMO_USER,
        lastLogin: new Date().toISOString(),
        sessionId: Math.random().toString(36).slice(2, 10).toUpperCase(),
      };
      sessionStorage.setItem("instaiq_user", JSON.stringify(userData));
      setUser(userData);
      return true;
    }
    setError("Invalid credentials. Try soham.joshi@atliq.com / atliq@2025");
    return false;
  }, []);

  const logout = useCallback(() => {
    sessionStorage.removeItem("instaiq_user");
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, logout, error, setError }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be inside AuthProvider");
  return ctx;
}