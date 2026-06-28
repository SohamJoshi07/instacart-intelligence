import { IcBot } from "../ui/icons";

export default function ChatBubble({ role, content, isError }) {
  const isUser = role === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"} animate-fade-in`}>
      {!isUser && (
        <div
          className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 text-brand ${
            isError ? "bg-brand/20" : "bg-brand-soft"
          }`}
        >
          <IcBot className="w-4 h-4" />
        </div>
      )}
      <div
        className={`max-w-[80%] sm:max-w-[65%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
          isUser ? "rounded-br-md bg-brand text-white" : "rounded-bl-md border border-base-border"
        } ${!isUser && isError ? "bg-brand/10 text-red-300 border-brand/30" : ""} ${
          !isUser && !isError ? "bg-base-card text-slate-200" : ""
        }`}
      >
        {!isUser && (
          <p className={`text-[11px] font-semibold uppercase tracking-wide mb-1 ${isError ? "text-red-300" : "text-brand"}`}>
            Rohan (AI Assistant)
          </p>
        )}
        {content}
      </div>
    </div>
  );
}
