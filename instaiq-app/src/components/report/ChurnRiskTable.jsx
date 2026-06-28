import { CHURN_DISTRIBUTION, RISK_META } from "../../lib/constants";

export default function ChurnRiskTable() {
  return (
    <div className="overflow-x-auto -mx-5 px-5">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-slate-500 text-xs uppercase tracking-wider border-b border-base-border">
            <th className="py-2.5 pr-4 font-semibold">Risk tier</th>
            <th className="py-2.5 pr-4 font-semibold">Users</th>
            <th className="py-2.5 pr-4 font-semibold">% of base</th>
            <th className="py-2.5 pr-2 font-semibold">Recommended action</th>
          </tr>
        </thead>
        <tbody>
          {CHURN_DISTRIBUTION.map((row) => {
            const c = RISK_META[row.risk];
            return (
              <tr key={row.risk} style={{ backgroundColor: c.row }} className="border-b border-white/5">
                <td className="py-3 pr-4">
                  <span className="inline-flex items-center gap-2 font-semibold" style={{ color: c.text }}>
                    <span className="w-2 h-2 rounded-full" style={{ backgroundColor: c.dot }} />
                    {row.risk}
                  </span>
                </td>
                <td className="py-3 pr-4 font-medium text-slate-100 tabular-nums">{row.users.toLocaleString()}</td>
                <td className="py-3 pr-4 text-slate-300 tabular-nums">{row.pctOfBase}</td>
                <td className="py-3 pr-2 text-slate-400">{row.action}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
