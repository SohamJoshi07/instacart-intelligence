import Badge from "../ui/Badge";
import EmptyState from "../ui/EmptyState";
import ProgressBar from "./ProgressBar";
import { IcBasket, IcLeaf } from "../ui/icons";

export default function RecommendationsTable({ rows }) {
  if (!rows || rows.length === 0) {
    return (
      <EmptyState
        icon={<IcBasket className="w-full h-full" />}
        title="No recommendations available"
        subtitle="This user may not have enough order history for the model to generate predictions."
      />
    );
  }

  return (
    <div className="overflow-x-auto -mx-5 px-5">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-slate-500 text-xs uppercase tracking-wider border-b border-base-border">
            <th className="py-2.5 pr-4 font-semibold">Product</th>
            <th className="py-2.5 pr-4 font-semibold">Department</th>
            <th className="py-2.5 pr-4 font-semibold">Reorder probability</th>
            <th className="py-2.5 pr-2 font-semibold">Organic</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={r.product_id ?? r.product_name ?? i} className="border-b border-white/5 hover:bg-white/[0.03] transition-colors">
              <td className="py-3 pr-4 font-medium text-slate-100">{r.product_name || r.name || "—"}</td>
              <td className="py-3 pr-4 text-slate-400">{r.department || "—"}</td>
              <td className="py-3 pr-4">
                <ProgressBar value={r.reorder_probability ?? r.probability ?? 0} />
              </td>
              <td className="py-3 pr-2">
                {r.is_organic ? (
                  <Badge color="#22c55e">
                    <IcLeaf className="w-3 h-3 inline mr-1 -mt-0.5" />
                    Organic
                  </Badge>
                ) : (
                  <span className="text-slate-600">—</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
