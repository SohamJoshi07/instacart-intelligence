export default function SuggestedQuestions({ questions, onSelect, disabled }) {
  return (
    <div className="px-5 py-4 border-b border-base-border flex-shrink-0">
      <p className="text-xs text-slate-500 mb-2.5">Suggested questions</p>
      <div className="flex flex-wrap gap-2">
        {questions.map((q) => (
          <button
            key={q}
            onClick={() => onSelect(q)}
            disabled={disabled}
            className="text-xs px-3 py-1.5 rounded-full border border-base-border bg-white/[0.03] text-slate-300 hover:text-white hover:border-brand transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
