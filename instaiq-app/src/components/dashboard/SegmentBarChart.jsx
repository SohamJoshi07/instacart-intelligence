import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import Card from "../ui/Card";
import ChartTooltip from "./ChartTooltip";
import { SEGMENT_COLORS } from "../../lib/constants";

export default function SegmentBarChart({ data }) {
  return (
    <Card className="p-5">
      <h3 className="font-display font-semibold text-base mb-1">Segment distribution</h3>
      <p className="text-sm text-slate-500 mb-4">User counts across behavioral segments</p>
      <div style={{ width: "100%", height: 280 }}>
        <ResponsiveContainer>
          <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#293548" vertical={false} />
            <XAxis
              dataKey="segment"
              tick={{ fill: "#94a3b8", fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: "#293548" }}
              interval={0}
              angle={-12}
              textAnchor="end"
              height={50}
            />
            <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} tickLine={false} axisLine={{ stroke: "#293548" }} />
            <Tooltip content={<ChartTooltip />} cursor={{ fill: "rgba(255,255,255,0.04)" }} />
            <Bar dataKey="users" radius={[6, 6, 0, 0]}>
              {data.map((entry) => (
                <Cell key={entry.segment} fill={SEGMENT_COLORS[entry.segment]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
