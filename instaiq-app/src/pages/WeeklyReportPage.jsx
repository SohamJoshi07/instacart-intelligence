import { useCallback, useEffect, useState } from "react";
import PageShell from "../components/layout/PageShell";
import Card from "../components/ui/Card";
import Spinner from "../components/ui/Spinner";
import ErrorBanner from "../components/ui/ErrorBanner";
import ChurnRiskTable from "../components/report/ChurnRiskTable";
import { IcBot, IcRefresh } from "../components/ui/icons";
import { askQuestion, extractAnswer } from "../lib/api";

const EMPTY_RESOURCE = { loading: false, ok: false, data: null, error: null };

export default function WeeklyReportPage({ onMenuClick }) {
  const [state, setState] = useState(EMPTY_RESOURCE);
  const [generatedAt, setGeneratedAt] = useState(null);

  const generate = useCallback(async () => {
    setState({ ...EMPTY_RESOURCE, loading: true });
    const res = await askQuestion("Generate a weekly executive summary of the platform");
    if (res.ok) {
      setState({ loading: false, ok: true, data: res.data, error: null });
      setGeneratedAt(new Date());
    } else {
      setState({ loading: false, ok: false, data: null, error: res.error });
    }
  }, []);

  useEffect(() => {
    generate();
  }, [generate]);

  return (
    <PageShell title="Weekly Report" subtitle="LLM-generated executive summary, refreshed on demand" onMenuClick={onMenuClick}>
      <Card className="p-6 mb-6">
        <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center bg-brand-soft text-brand">
              <IcBot className="w-4.5 h-4.5" />
            </div>
            <div>
              <h3 className="font-display font-semibold text-base leading-tight">Executive Summary</h3>
              <p className="text-xs text-slate-500">{generatedAt ? `Generated ${generatedAt.toLocaleString()}` : "Not yet generated"}</p>
            </div>
          </div>
          <button
            onClick={generate}
            disabled={state.loading}
            className="px-4 py-2 rounded-xl text-sm font-semibold flex items-center gap-2 bg-brand transition-opacity hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <IcRefresh className={`w-4 h-4 ${state.loading ? "animate-spin" : ""}`} />
            Regenerate Report
          </button>
        </div>

        {state.loading && (
          <div className="py-10 flex justify-center">
            <Spinner label="Generating executive summary…" />
          </div>
        )}

        {!state.loading && !state.ok && state.error && <ErrorBanner message={`Couldn't generate the report: ${state.error}`} onRetry={generate} />}

        {!state.loading && state.ok && (
          <div className="rounded-xl p-5 text-sm leading-relaxed whitespace-pre-wrap text-slate-200 bg-base-surface border border-base-border">
            {extractAnswer(state.data)}
          </div>
        )}
      </Card>

      <Card className="p-5">
        <h3 className="font-display font-semibold text-base mb-1">Churn risk distribution</h3>
        <p className="text-sm text-slate-500 mb-4">Static snapshot from the most recent scoring run</p>
        <ChurnRiskTable />
      </Card>
    </PageShell>
  );
}
