import Card from "../ui/Card";
import { IcLeaf } from "../ui/icons";

export default function SimilarItemCard({ item }) {
  const score = item.similarity_score ?? item.similarity ?? item.score ?? 0;
  const pct = Math.round(Math.max(0, Math.min(1, score)) * 100);

  return (
    <Card className="p-4 flex flex-col gap-3 animate-fade-in">
      <div className="flex items-start justify-between gap-2">
        <p className="font-medium text-slate-100 leading-snug">{item.product_name || item.name || "Unknown product"}</p>
        {item.is_organic && (
          <span className="flex-shrink-0" title="Organic">
            <IcLeaf className="w-4 h-4 text-green-400" />
          </span>
        )}
      </div>
      <p className="text-xs text-slate-500">{item.department || "Department unknown"}</p>
      <div className="mt-auto">
        <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
          <span>Similarity</span>
          <span className="text-slate-300 font-medium tabular-nums">{pct}%</span>
        </div>
        <div className="h-1.5 rounded-full bg-white/10 overflow-hidden">
          <div className="h-full rounded-full bg-brand" style={{ width: `${pct}%` }} />
        </div>
      </div>
    </Card>
  );
}
