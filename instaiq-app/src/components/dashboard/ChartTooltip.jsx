export default function ChartTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) return null;
  return (
    <div className="rounded-lg border border-base-border bg-base-surface px-3 py-2 text-sm shadow-xl">
      <p className="text-slate-400 text-xs mb-1">{label || payload[0].name}</p>
      <p className="font-semibold text-white">{payload[0].value.toLocaleString()} users</p>
    </div>
  );
}
