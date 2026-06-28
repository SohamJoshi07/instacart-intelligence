import { useState } from "react";
import { motion } from "framer-motion";
import PageShell from "../components/layout/PageShell";
import Card      from "../components/ui/Card";
import { useAuth } from "../contexts/AuthContext";

function Section({ title, children }) {
  return (
    <Card className="p-5 mb-4">
      <p className="font-mono text-[10px] uppercase tracking-widest text-muted mb-4 pb-3 border-b border-border">{title}</p>
      {children}
    </Card>
  );
}

function Field({ label, value, hint }) {
  const [val, setVal] = useState(value || "");
  return (
    <div className="flex flex-col sm:flex-row sm:items-center gap-2 py-3 border-b border-border/50 last:border-0">
      <div className="sm:w-40 flex-shrink-0">
        <p className="font-mono text-[10px] uppercase tracking-widest text-muted">{label}</p>
        {hint && <p className="font-mono text-[9px] text-border mt-0.5">{hint}</p>}
      </div>
      <input
        value={val}
        onChange={e => setVal(e.target.value)}
        className="flex-1 px-3 py-2 bg-ink border border-border font-mono text-[12px] text-white outline-none focus:border-white/30 transition-colors"
      />
    </div>
  );
}

function Toggle({ label, sub, defaultOn = false }) {
  const [on, setOn] = useState(defaultOn);
  return (
    <div className="flex items-center justify-between py-3 border-b border-border/50 last:border-0">
      <div>
        <p className="font-mono text-[11px] text-white uppercase tracking-widest">{label}</p>
        {sub && <p className="font-mono text-[10px] text-muted mt-0.5">{sub}</p>}
      </div>
      <button
        onClick={() => setOn(o => !o)}
        className={`w-10 h-5 border transition-colors relative flex-shrink-0 ${on ? "bg-brand border-brand" : "bg-ink border-border"}`}
      >
        <motion.span
          className="absolute top-0.5 w-4 h-4 bg-white"
          animate={{ left: on ? "calc(100% - 18px)" : "2px" }}
          transition={{ duration: 0.15 }}
        />
      </button>
    </div>
  );
}

export default function SettingsPage({ onMenuClick }) {
  const { user, logout } = useAuth();
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <PageShell
      title="Settings"
      subtitle="Workspace · Configuration"
      onMenuClick={onMenuClick}
      topRight={
        <button
          onClick={handleSave}
          className="px-4 py-2 bg-brand font-mono text-[10px] uppercase tracking-widest text-white hover:bg-red-700 transition-colors"
        >
          {saved ? "✓ Saved" : "Save Changes"}
        </button>
      }
    >
      {/* Profile */}
      <Section title="Profile">
        <div className="flex items-center gap-4 mb-4 pb-4 border-b border-border">
          <div className="w-12 h-12 bg-brand flex items-center justify-center font-mono font-bold text-white text-lg">
            {user?.avatar}
          </div>
          <div>
            <p className="font-sans text-sm font-semibold text-white">{user?.name}</p>
            <p className="font-mono text-[10px] text-muted mt-0.5">{user?.role} · {user?.dept}</p>
            <p className="font-mono text-[9px] text-border mt-1 uppercase tracking-widest">Joined {user?.joined}</p>
          </div>
        </div>
        <Field label="Full Name"   value={user?.name}  />
        <Field label="Email"       value={user?.email} hint="Managed by AtliQ IT" />
        <Field label="Role"        value={user?.role}  hint="Contact HR to change" />
        <Field label="Department"  value={user?.dept}  />
      </Section>

      {/* API */}
      <Section title="API Configuration">
        <Field label="API Base URL" value="http://localhost:8000" hint="FastAPI backend endpoint" />
        <Field label="Groq API Key" value="gsk_••••••••••••••••" hint="LLM inference key" />
        <Field label="Model ID"     value="llama-3.1-8b-instant" hint="Active inference model" />
        <Field label="Timeout (s)"  value="30" />
      </Section>

      {/* Notifications */}
      <Section title="Notifications">
        <Toggle label="Churn Alerts"      sub="Alert when critical churn spikes > 2%"  defaultOn={true}  />
        <Toggle label="Model Updates"     sub="Notify when models are retrained"        defaultOn={true}  />
        <Toggle label="Team Mentions"     sub="Alert when someone tags you"             defaultOn={true}  />
        <Toggle label="Batch Job Alerts"  sub="Pipeline success / failure"              defaultOn={false} />
        <Toggle label="Weekly Digest"     sub="Email summary every Monday 9AM"          defaultOn={false} />
      </Section>

      {/* Appearance */}
      <Section title="Appearance">
        <Toggle label="Monospace Numbers" sub="Use JetBrains Mono for all data values" defaultOn={true}  />
        <Toggle label="Reduced Motion"    sub="Disable Framer Motion animations"       defaultOn={false} />
        <Toggle label="Compact Mode"      sub="Tighter padding across all cards"       defaultOn={false} />
      </Section>

      {/* Danger zone */}
      <Card className="p-5 border-brand/30">
        <p className="font-mono text-[10px] uppercase tracking-widest text-brand mb-4">Danger Zone</p>
        <div className="flex items-center justify-between">
          <div>
            <p className="font-mono text-[11px] text-white uppercase tracking-widest">Sign Out</p>
            <p className="font-mono text-[10px] text-muted mt-0.5">End your current session</p>
          </div>
          <button
            onClick={logout}
            className="px-4 py-2 border border-brand font-mono text-[10px] uppercase tracking-widest text-brand hover:bg-brand hover:text-white transition-colors"
          >
            Sign Out
          </button>
        </div>
      </Card>
    </PageShell>
  );
}