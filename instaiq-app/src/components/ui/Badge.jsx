export default function Badge({ children, color = "#e31837", soft = true }) {
  return (
    <span
      className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold tracking-wide"
      style={{
        backgroundColor: soft ? `${color}26` : color,
        color: soft ? color : "#fff",
        border: `1px solid ${color}40`,
      }}
    >
      {children}
    </span>
  );
}
