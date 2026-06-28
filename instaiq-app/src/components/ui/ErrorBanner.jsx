import { IcAlert } from "./icons";

export default function ErrorBanner({ message, onRetry }) {
  return (
    <div className="rounded-xl border border-brand/40 bg-brand/[0.08] px-4 py-3 flex items-start gap-3 animate-fade-in">
      <IcAlert className="w-5 h-5 mt-0.5 flex-shrink-0 text-brand" />
      <div className="flex-1 min-w-0">
        <p className="text-sm text-red-100">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-2 text-xs font-semibold uppercase tracking-wide text-red-200 hover:text-white transition-colors"
          >
            Try again →
          </button>
        )}
      </div>
    </div>
  );
}
