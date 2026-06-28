import { useCallback, useState } from "react";
import PageShell from "../components/layout/PageShell";
import Card from "../components/ui/Card";
import Spinner from "../components/ui/Spinner";
import ErrorBanner from "../components/ui/ErrorBanner";
import EmptyState from "../components/ui/EmptyState";
import { SegmentBadge, StatPill } from "../components/explorer/SegmentBadge";
import RecommendationsTable from "../components/explorer/RecommendationsTable";
import { IcSearch, IcUser } from "../components/ui/icons";
import { getSegment, getRecommendations } from "../lib/api";

const EMPTY_RESOURCE = { loading: false, ok: false, data: null, error: null };

export default function UserExplorerPage({ onMenuClick }) {
  const [input, setInput] = useState("");
  const [userId, setUserId] = useState(null);
  const [segment, setSegment] = useState(EMPTY_RESOURCE);
  const [recs, setRecs] = useState(EMPTY_RESOURCE);

  const lookup = useCallback(async (id) => {
    if (!id) return;
    setUserId(id);
    setSegment({ ...EMPTY_RESOURCE, loading: true });
    setRecs({ ...EMPTY_RESOURCE, loading: true });

    const [segRes, recRes] = await Promise.all([getSegment(id), getRecommendations(id, 10)]);

    setSegment(
      segRes.ok ? { loading: false, ok: true, data: segRes.data, error: null } : { loading: false, ok: false, data: null, error: segRes.error }
    );
    setRecs(
      recRes.ok ? { loading: false, ok: true, data: recRes.data, error: null } : { loading: false, ok: false, data: null, error: recRes.error }
    );
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (trimmed) lookup(trimmed);
  };

  const recRows = Array.isArray(recs.data) ? recs.data : recs.data?.recommendations || recs.data?.items || [];

  return (
    <PageShell title="User Explorer" subtitle="Look up a user's segment, RFM scores, and top reorder predictions" onMenuClick={onMenuClick}>
      <form onSubmit={handleSubmit} className="flex gap-3 mb-6">
        <div className="relative flex-1 max-w-md">
          <IcSearch className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter a user ID, e.g. 14"
            className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm outline-none border border-base-border bg-base-card focus:border-brand transition-colors placeholder:text-slate-500"
          />
        </div>
        <button type="submit" className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-brand transition-opacity hover:opacity-90 flex-shrink-0">
          Search
        </button>
      </form>

      {!userId && (
        <Card className="p-5">
          <EmptyState
            icon={<IcUser className="w-full h-full" />}
            title="Search for a user to get started"
            subtitle="Enter a user ID above and press Enter or click Search to view their segment and personalized recommendations."
          />
        </Card>
      )}

      {userId && (
        <div className="space-y-5">
          <Card className="p-5">
            <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
              <h3 className="font-display font-semibold text-base">User #{userId}</h3>
              {segment.loading && <Spinner label="Loading profile…" />}
            </div>

            {!segment.loading && !segment.ok && (
              <ErrorBanner message={`Couldn't load segment data: ${segment.error}`} onRetry={() => lookup(userId)} />
            )}

            {!segment.loading && segment.ok && segment.data && (
              <div className="flex flex-wrap items-center gap-3">
                <SegmentBadge segment={segment.data.segment || segment.data.segment_label} />
                <StatPill label="RFM-R" value={segment.data.rfm_r ?? "—"} />
                <StatPill label="RFM-F" value={segment.data.rfm_f ?? "—"} />
                <StatPill label="Recency" value={segment.data.recency ?? "—"} />
                <StatPill label="Frequency" value={segment.data.frequency ?? "—"} />
              </div>
            )}
          </Card>

          <Card className="p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-display font-semibold text-base">Top recommended products</h3>
              {recs.loading && <Spinner label="Loading recommendations…" />}
            </div>

            {!recs.loading && !recs.ok && (
              <ErrorBanner message={`Couldn't load recommendations: ${recs.error}`} onRetry={() => lookup(userId)} />
            )}

            {!recs.loading && recs.ok && <RecommendationsTable rows={recRows} />}
          </Card>
        </div>
      )}
    </PageShell>
  );
}
