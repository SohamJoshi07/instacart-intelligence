import { useState } from "react";
import { motion } from "framer-motion";
import PageShell from "../components/layout/PageShell";
import Card      from "../components/ui/Card";
import { ACTIVITY_LOG } from "../lib/constants";

const TYPE_META = {
  query:    { color: "#3b82f6", label: "QUERY"    },
  model:    { color: "#f59e0b", label: "MODEL"    },
  export:   { color: "#22c55e", label: "EXPORT"   },
  pipeline: { color: "#a78bfa", label: "PIPELINE" },
};

const ALL_TYPES = ["all", "query", "model", "export", "pipeline"];

export default function ActivityPage({ onMenuClick }) {
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");

  const filtered = ACTIVITY_LOG.filter(a => {
    const matchType   = filter === "all" || a.type === filter;
    const matchSearch = !search || [a.user, a.action, a.target].some(s => s.toLowerCase().includes(search.toLowerCase()));
    return matchType && matchSearch;
  });

  return (
    <PageShell title="Activity Log" subtitle="Workspace · Audit Trail" onMenuClick={onMenuClick}>
      <Card className="p-5 mb-4 flex flex-wrap items-center gap-3">
        {/* Filter chips */}
        <div className="flex flex-wrap gap-2">
          {ALL_TYPES.map(t => (
            <button
              key={t}
              onClick={() => setFilter(t)}
              className={`font-mono text-[9px] uppercase tracking-widest px-2.5 py-1.5 border transition-colors ${
                filter === t ? "border-brand text-brand bg-brand/10" : "border-border text-muted hover:border-white/30 hover:text-white"
              }`}
            >
              {t}
            </button>
          ))}
        </div>

        <div className="flex-1 min-w-[160px]">
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search actions, users…"
            className="w-full px-3 py-1.5 bg-ink border border-border font-mono text-[11px] text-white placeholder:text-border outline-none focus:border-white/30 transition-colors"
          />
        </div>

        <span className="font-mono text-[10px] text-muted uppercase tracking-widest ml-auto">
          {filtered.length} entries
        </span>
      </Card>

      <Card>
        <table className="w-full">
          <thead>
            <tr className="border-b border-border">
              {["#", "User", "Action", "Target", "Type", "Time"].map(h => (
                <th key={h} className="px-4 py-3 text-left font-mono text-[9px] uppercase tracking-widest text-muted first:w-10">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((row, i) => {
              const m = TYPE_META[row.type] || TYPE_META.query;
              return (
                <motion.tr
                  key={row.id}
                  className="border-b border-border/40 hover:bg-white/[0.02] transition-colors"
                  initial={{ opacity: 0, x: -4 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.025 }}
                >
                  <td className="px-4 py-3 font-mono text-[10px] text-border">{String(row.id).padStart(2,"0")}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-5 h-5 bg-panel border border-border flex items-center justify-center font-mono text-[8px] text-muted flex-shrink-0">
                        {row.user.split(" ").map(n=>n[0]).join("")}
                      </div>
                      <span className="font-sans text-[12px] text-white">{row.user}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 font-sans text-[12px] text-white">{row.action}</td>
                  <td className="px-4 py-3 font-mono text-[11px] text-muted">{row.target}</td>
                  <td className="px-4 py-3">
                    <span className="font-mono text-[9px] uppercase tracking-widest px-1.5 py-0.5"
                      style={{ color: m.color, backgroundColor: `${m.color}18`, border: `1px solid ${m.color}30` }}>
                      {m.label}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-mono text-[10px] text-muted">{row.time}</td>
                </motion.tr>
              );
            })}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <p className="text-center font-mono text-[11px] text-border uppercase tracking-widest py-12">No matching entries</p>
        )}
      </Card>
    </PageShell>
  );
}