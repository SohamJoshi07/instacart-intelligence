export default function Card({ children, className = "" }) {
  return (
    <div className={`rounded-2xl border border-base-border bg-base-card shadow-lg shadow-black/20 ${className}`}>
      {children}
    </div>
  );
}
