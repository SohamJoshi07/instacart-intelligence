import { IcBot } from "../ui/icons";

export default function ThinkingBubble() {
  return (
    <div className="flex gap-3 justify-start animate-fade-in">
      <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 bg-brand-soft text-brand">
        <IcBot className="w-4 h-4" />
      </div>
      <div className="rounded-2xl rounded-bl-md px-4 py-3 border border-base-border bg-base-card flex items-center gap-1.5">
        <span className="typing-dot w-1.5 h-1.5 rounded-full bg-slate-400" />
        <span className="typing-dot w-1.5 h-1.5 rounded-full bg-slate-400" />
        <span className="typing-dot w-1.5 h-1.5 rounded-full bg-slate-400" />
      </div>
    </div>
  );
}
