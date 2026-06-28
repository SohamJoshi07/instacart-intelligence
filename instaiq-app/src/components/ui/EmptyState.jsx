export default function EmptyState({ icon, title, subtitle }) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-16 px-6 text-slate-500">
      <div className="w-12 h-12 mb-3 opacity-60">{icon}</div>
      <p className="text-slate-300 font-medium">{title}</p>
      {subtitle && <p className="text-sm text-slate-500 mt-1 max-w-sm">{subtitle}</p>}
    </div>
  );
}
