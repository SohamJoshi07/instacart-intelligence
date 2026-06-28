import { useCallback, useState } from "react";
import PageShell from "../components/layout/PageShell";
import Card from "../components/ui/Card";
import Spinner from "../components/ui/Spinner";
import ErrorBanner from "../components/ui/ErrorBanner";
import EmptyState from "../components/ui/EmptyState";
import SimilarItemCard from "../components/basket/SimilarItemCard";
import { IcBasket } from "../components/ui/icons";
import { getSimilarItems } from "../lib/api";

const EMPTY_RESOURCE = { loading: false, ok: false, data: null, error: null };

export default function BasketCompletionPage({ onMenuClick }) {
  const [input, setInput] = useState("");
  const [productId, setProductId] = useState(null);
  const [state, setState] = useState(EMPTY_RESOURCE);

  const search = useCallback(async (id) => {
    setProductId(id);
    setState({ ...EMPTY_RESOURCE, loading: true });
    const res = await getSimilarItems(id, 5);
    setState(res.ok ? { loading: false, ok: true, data: res.data, error: null } : { loading: false, ok: false, data: null, error: res.error });
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (trimmed) search(trimmed);
  };

  const items = Array.isArray(state.data) ? state.data : state.data?.similar_items || state.data?.items || [];

  return (
    <PageShell title="Complete the Basket" subtitle="Find products frequently paired with a given item" onMenuClick={onMenuClick}>
      <form onSubmit={handleSubmit} className="flex gap-3 mb-6">
        <div className="relative flex-1 max-w-md">
          <IcBasket className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter a product ID, e.g. 24852"
            className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm outline-none border border-base-border bg-base-card focus:border-brand transition-colors placeholder:text-slate-500"
          />
        </div>
        <button type="submit" className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-brand transition-opacity hover:opacity-90 flex-shrink-0">
          Find similar
        </button>
      </form>

      {!productId && (
        <Card className="p-5">
          <EmptyState
            icon={<IcBasket className="w-full h-full" />}
            title="Look up a product to complete the basket"
            subtitle="Enter a product ID above to see five products commonly bought alongside it."
          />
        </Card>
      )}

      {productId && state.loading && (
        <Card className="p-8 flex justify-center">
          <Spinner label="Finding similar products…" />
        </Card>
      )}

      {productId && !state.loading && !state.ok && <ErrorBanner message={`Couldn't load similar items: ${state.error}`} onRetry={() => search(productId)} />}

      {productId && !state.loading && state.ok && items.length === 0 && (
        <Card className="p-5">
          <EmptyState
            icon={<IcBasket className="w-full h-full" />}
            title="No similar products found"
            subtitle={`No co-purchase data was available for product ${productId}.`}
          />
        </Card>
      )}

      {productId && !state.loading && state.ok && items.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          {items.map((item, i) => (
            <SimilarItemCard key={item.product_id ?? i} item={item} />
          ))}
        </div>
      )}
    </PageShell>
  );
}
