export default function StatPill({ label, value }) {
  return (
    <div className="border border-border bg-ink px-4 py-3 min-w-[90px]">
      <p className="font-mono text-[9px] uppercase tracking-widest text-muted mb-1.5">{label}</p>
      <p className="font-mono text-lg font-bold text-white tabular-nums">{value ?? "—"}</p>
    </div>
  );
}
