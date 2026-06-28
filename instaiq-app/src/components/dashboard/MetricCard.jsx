import Card from "../ui/Card";

export default function MetricCard({ label, value, accent, icon }) {
  return (
    <Card className="p-5 flex items-start justify-between">
      <div className="min-w-0">
        <p className="text-xs uppercase tracking-wider text-slate-500 font-semibold mb-2">{label}</p>
        <p className="font-display text-2xl sm:text-3xl font-bold tracking-tight truncate">{value}</p>
      </div>
      <div
        className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
        style={{ backgroundColor: accent ? `${accent}1f` : "rgba(255,255,255,0.06)", color: accent || "#94a3b8" }}
      >
        {icon}
      </div>
    </Card>
  );
}
