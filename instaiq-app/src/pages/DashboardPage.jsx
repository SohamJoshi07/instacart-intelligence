import { useHealth } from "../hooks/useHealth";
import { useAuth }   from "../contexts/AuthContext";
import PageShell     from "../components/layout/PageShell";
import Card          from "../components/ui/Card";
import Badge         from "../components/ui/Badge";
import ErrorBanner   from "../components/ui/ErrorBanner";
import MetricCard    from "../components/dashboard/MetricCard";
import SegmentBarChart from "../components/dashboard/SegmentBarChart";
import ClvDonutChart   from "../components/dashboard/ClvDonutChart";
import { IcUser, IcZap, IcBasket, IcTrend } from "../components/ui/icons";
import { SUMMARY_STATS } from "../lib/constants";
import { buildSegmentData, buildClvData } from "../lib/mockData";

function greeting() {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 17) return "Good afternoon";
  return "Good evening";
}

const METRICS = (total) => [
  { label: "Total Users",    value: total.toLocaleString(),                           sub: "indexed in model",  accent: "#3b82f6", icon: <IcUser   className="w-4 h-4" /> },
  { label: "Critical Churn", value: SUMMARY_STATS.criticalChurnUsers.toLocaleString(),sub: "need intervention", accent: "#e31837", icon: <IcZap    className="w-4 h-4" /> },
  { label: "Reorder Rate",   value: `${(SUMMARY_STATS.globalReorderRate*100).toFixed(1)}%`, sub: "global baseline", accent: "#22c55e", icon: <IcBasket className="w-4 h-4" /> },
  { label: "Avg CLV",        value: `$${SUMMARY_STATS.avgCLV.toFixed(0)}`,           sub: "per customer",      accent: "#e3b341", icon: <IcTrend  className="w-4 h-4" /> },
];

export default function DashboardPage({ onMenuClick }) {
  const health = useHealth();
  const { user } = useAuth();
  const total = health.data?.users ?? SUMMARY_STATS.totalUsers;

  const lastLogin = user?.lastLogin
    ? new Date(user.lastLogin).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" })
    : "—";

  return (
    <PageShell title="Dashboard" subtitle="Customer Intelligence Platform" onMenuClick={onMenuClick}>

      {/* Greeting banner */}
      <Card className="px-5 py-4 mb-5 flex items-center justify-between flex-wrap gap-3">
        <div>
          <p className="font-sans text-base font-semibold text-white">
            {greeting()}, {user?.name?.split(" ")[0]} 👋
          </p>
          <p className="font-mono text-[10px] text-muted uppercase tracking-widest mt-0.5">
            {user?.role} · {user?.dept} · Session {user?.sessionId}
          </p>
        </div>
        <div className="text-right">
          <p className="font-mono text-[9px] text-border uppercase tracking-widest">Last login</p>
          <p className="font-mono text-[11px] text-muted mt-0.5">{lastLogin}</p>
        </div>
      </Card>

      {!health.loading && !health.ok && (
        <div className="mb-5"><ErrorBanner message={`Health check failed — ${health.error}`} onRetry={health.reload} /></div>
      )}

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
        {METRICS(total).map((m, i) => <MetricCard key={m.label} {...m} index={i} />)}
      </div>

      {health.ok && (
        <Card className="px-4 py-2.5 mb-5 flex flex-wrap items-center gap-x-6 gap-y-1.5">
          <span className="font-mono text-[9px] uppercase tracking-widest text-muted">Model</span>
          <Badge color="#22c55e">{health.data.status || "HEALTHY"}</Badge>
          {health.data.trees    && <span className="font-mono text-[10px] text-muted">TREES <span className="text-white">{health.data.trees}</span></span>}
          {health.data.features && <span className="font-mono text-[10px] text-muted">FEATURES <span className="text-white">{health.data.features}</span></span>}
          {health.data.users    && <span className="font-mono text-[10px] text-muted">USERS <span className="text-white">{health.data.users.toLocaleString()}</span></span>}
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <SegmentBarChart data={buildSegmentData(total)} />
        <ClvDonutChart   data={buildClvData(total)} />
      </div>
    </PageShell>
  );
}