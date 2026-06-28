import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "../contexts/AuthContext";

function GoogleIcon() {
  return (
    <svg className="w-4 h-4" viewBox="0 0 24 24">
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
    </svg>
  );
}

export default function LoginPage() {
  const { login, error, setError } = useAuth();
  const [email, setEmail]         = useState("");
  const [password, setPassword]   = useState("");
  const [loading, setLoading]     = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [showPass, setShowPass]   = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});

  const validate = () => {
    const errs = {};
    if (!email)    errs.email    = "Email is required";
    if (!password) errs.password = "Password is required";
    if (email && !email.includes("@")) errs.email = "Enter a valid email";
    setFieldErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (!validate()) return;
    setLoading(true);
    await login(email, password);
    setLoading(false);
  };

  const handleGoogle = async () => {
    setGoogleLoading(true);
    await new Promise(r => setTimeout(r, 1500));
    setGoogleLoading(false);
    setError("Google SSO is not configured in this environment. Use email login.");
  };

  return (
    <div className="min-h-screen bg-ink flex grid-lines">
      {/* Left panel — branding */}
      <motion.div
        className="hidden lg:flex lg:w-1/2 flex-col justify-between p-12 border-r border-border relative overflow-hidden"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Background accent */}
        <div className="absolute top-0 left-0 w-96 h-96 bg-brand/5 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2 pointer-events-none" />
        <div className="absolute bottom-0 right-0 w-72 h-72 bg-brand/3 rounded-full blur-3xl translate-x-1/2 translate-y-1/2 pointer-events-none" />

        {/* Logo */}
        <div>
          <div className="flex items-center gap-3 mb-12">
            <div className="w-8 h-8 bg-brand flex items-center justify-center font-mono font-bold text-white text-sm">iQ</div>
            <div>
              <p className="font-mono font-bold text-white text-sm uppercase tracking-widest">InstaIQ</p>
              <p className="font-mono text-[10px] text-muted uppercase tracking-widest">AtliQ Technologies</p>
            </div>
          </div>

          <h1 className="font-sans text-4xl font-bold text-white leading-tight mb-4">
            Customer<br />Intelligence<br />Platform
          </h1>
          <p className="font-sans text-sm text-muted leading-relaxed max-w-sm">
            Advanced analytics, churn prediction, CLV modeling, and AI-powered insights — built for the AtliQ data team.
          </p>
        </div>

        {/* Stats strip */}
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: "Users Tracked", value: "206K+" },
            { label: "Model Accuracy", value: "91.2%" },
            { label: "Data Points",   value: "3.4M+"  },
          ].map(s => (
            <div key={s.label} className="border border-border bg-surface/60 p-3">
              <p className="font-mono text-xl font-bold text-white">{s.value}</p>
              <p className="font-mono text-[9px] text-muted uppercase tracking-widest mt-1">{s.label}</p>
            </div>
          ))}
        </div>

        {/* Bottom team info */}
        <div className="flex items-center gap-3">
          <div className="flex -space-x-2">
            {["SJ","PS","RM","VN"].map(a => (
              <div key={a} className="w-7 h-7 bg-surface border border-border flex items-center justify-center font-mono text-[9px] text-muted">
                {a}
              </div>
            ))}
          </div>
          <p className="font-mono text-[10px] text-muted">5 analysts active today</p>
        </div>
      </motion.div>

      {/* Right panel — login form */}
      <div className="flex-1 flex items-center justify-center p-6">
        <motion.div
          className="w-full max-w-sm"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          {/* Mobile logo */}
          <div className="flex items-center gap-2 mb-8 lg:hidden">
            <div className="w-7 h-7 bg-brand flex items-center justify-center font-mono font-bold text-white text-xs">iQ</div>
            <span className="font-mono font-bold text-white text-sm uppercase tracking-widest">InstaIQ</span>
          </div>

          <h2 className="font-sans text-2xl font-semibold text-white mb-1">Sign in</h2>
          <p className="font-mono text-[11px] text-muted uppercase tracking-widest mb-8">AtliQ internal access only</p>

          {/* Google SSO button */}
          <motion.button
            onClick={handleGoogle}
            disabled={googleLoading || loading}
            className="w-full flex items-center justify-center gap-3 border border-border bg-surface px-4 py-3 font-mono text-[11px] uppercase tracking-widest text-white hover:border-white/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed mb-6"
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
          >
            {googleLoading
              ? <span className="spinner" />
              : <GoogleIcon />
            }
            {googleLoading ? "Redirecting…" : "Continue with Google"}
          </motion.button>

          {/* Divider */}
          <div className="flex items-center gap-3 mb-6">
            <div className="flex-1 h-px bg-border" />
            <span className="font-mono text-[10px] text-border uppercase tracking-widest">or</span>
            <div className="flex-1 h-px bg-border" />
          </div>

          {/* Error banner */}
          <AnimatePresence>
            {error && (
              <motion.div
                className="mb-4 border border-brand/30 bg-brand/10 px-3 py-2.5"
                initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              >
                <p className="font-mono text-[11px] text-red-300">{error}</p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block font-mono text-[10px] uppercase tracking-widest text-muted mb-1.5">
                Work Email
              </label>
              <input
                type="text"
                value={email}
                onChange={e => { setEmail(e.target.value); setFieldErrors(f => ({ ...f, email: "" })); }}
                placeholder="you@atliq.com"
                className={`w-full px-3 py-2.5 bg-surface border font-mono text-[12px] text-white placeholder:text-border outline-none transition-colors ${
                  fieldErrors.email ? "border-brand" : "border-border focus:border-white/40"
                }`}
              />
              {fieldErrors.email && <p className="font-mono text-[10px] text-brand mt-1">{fieldErrors.email}</p>}
            </div>

            <div>
              <label className="block font-mono text-[10px] uppercase tracking-widest text-muted mb-1.5">
                Password
              </label>
              <div className="relative">
                <input
                  type={showPass ? "text" : "password"}
                  value={password}
                  onChange={e => { setPassword(e.target.value); setFieldErrors(f => ({ ...f, password: "" })); }}
                  placeholder="••••••••"
                  className={`w-full px-3 py-2.5 pr-10 bg-surface border font-mono text-[12px] text-white placeholder:text-border outline-none transition-colors ${
                    fieldErrors.password ? "border-brand" : "border-border focus:border-white/40"
                  }`}
                />
                <button
                  type="button"
                  onClick={() => setShowPass(s => !s)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 font-mono text-[9px] text-muted hover:text-white uppercase tracking-widest transition-colors"
                >
                  {showPass ? "HIDE" : "SHOW"}
                </button>
              </div>
              {fieldErrors.password && <p className="font-mono text-[10px] text-brand mt-1">{fieldErrors.password}</p>}
            </div>

            <motion.button
              type="submit"
              disabled={loading || googleLoading}
              className="w-full py-3 bg-brand font-mono text-[11px] uppercase tracking-widest text-white hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-2"
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
            >
              {loading ? <><span className="spinner" /> Authenticating…</> : "Sign In →"}
            </motion.button>
          </form>

          {/* Hint */}
          <div className="mt-6 border border-border bg-surface p-3">
            <p className="font-mono text-[9px] text-muted uppercase tracking-widest mb-1">Demo credentials</p>
            <p className="font-mono text-[10px] text-white">soham.joshi@atliq.com</p>
            <p className="font-mono text-[10px] text-white">atliq@2025</p>
          </div>

          <p className="font-mono text-[9px] text-border text-center mt-6 uppercase tracking-widest">
            AtliQ Technologies · Internal use only · v2.0
          </p>
        </motion.div>
      </div>
    </div>
  );
}