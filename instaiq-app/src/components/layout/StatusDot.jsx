import { useHealth } from "../../hooks/useHealth";

export default function StatusDot() {
  const health = useHealth();
  let color = "#64748b";
  let label = "Checking…";
  if (!health.loading) {
    color = health.ok ? "#22c55e" : "#e31837";
    label = health.ok ? "API connected" : "API unreachable";
  }
  return (
    <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-black/20">
      <span className="relative flex h-2 w-2">
        <span className="absolute inline-flex h-full w-full rounded-full opacity-60" style={{ backgroundColor: color }} />
      </span>
      <span className="text-xs text-slate-400">{label}</span>
    </div>
  );
}
