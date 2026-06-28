import Badge from "../ui/Badge";
import { SEGMENT_COLORS } from "../../lib/constants";

export function SegmentBadge({ segment }) {
  const color = SEGMENT_COLORS[segment] || "#64748b";
  return <Badge color={color}>{segment}</Badge>;
}

export function StatPill({ label, value }) {
  return (
    <div className="rounded-xl px-4 py-3 bg-white/5 min-w-[110px]">
      <p className="text-[11px] uppercase tracking-wide text-slate-500 mb-1">{label}</p>
      <p className="font-display text-lg font-semibold tabular-nums">{value}</p>
    </div>
  );
}
