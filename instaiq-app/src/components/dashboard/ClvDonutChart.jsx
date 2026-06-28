import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import Card from "../ui/Card";
import ChartTooltip from "./ChartTooltip";
import { CLV_COLORS } from "../../lib/constants";

export default function ClvDonutChart({ data }) {
  return (
    <Card className="p-5">
      <h3 className="font-display font-semibold text-base mb-1">CLV tiers</h3>
      <p className="text-sm text-slate-500 mb-4">Customer lifetime value distribution</p>
      <div style={{ width: "100%", height: 280 }} className="flex items-center">
        <ResponsiveContainer>
          <PieChart>
            <Pie data={data} dataKey="users" nameKey="tier" innerRadius={60} outerRadius={95} paddingAngle={3} stroke="none">
              {data.map((entry) => (
                <Cell key={entry.tier} fill={CLV_COLORS[entry.tier]} />
              ))}
            </Pie>
            <Tooltip content={<ChartTooltip />} />
            <Legend
              verticalAlign="bottom"
              height={36}
              formatter={(value) => <span style={{ color: "#94a3b8", fontSize: 12 }}>{value}</span>}
              iconType="circle"
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
