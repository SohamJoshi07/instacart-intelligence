export default function Spinner({ label }) {
  return (
    <div className="flex items-center gap-2 text-slate-400 text-sm">
      <div className="spinner" />
      {label && <span>{label}</span>}
    </div>
  );
}
