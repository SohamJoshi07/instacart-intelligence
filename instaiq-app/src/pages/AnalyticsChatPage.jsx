import { useCallback, useEffect, useRef, useState } from "react";
import PageShell from "../components/layout/PageShell";
import Card from "../components/ui/Card";
import EmptyState from "../components/ui/EmptyState";
import ChatBubble from "../components/chat/ChatBubble";
import ThinkingBubble from "../components/chat/ThinkingBubble";
import SuggestedQuestions from "../components/chat/SuggestedQuestions";
import { IcChat, IcSend } from "../components/ui/icons";
import { askQuestion, extractAnswer } from "../lib/api";
import { SUGGESTED_QUESTIONS } from "../lib/constants";

export default function AnalyticsChatPage({ onMenuClick }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, thinking]);

  const send = useCallback(
    async (question) => {
      const trimmed = question.trim();
      if (!trimmed || thinking) return;

      setMessages((prev) => [...prev, { role: "user", content: trimmed }]);
      setInput("");
      setThinking(true);

      const res = await askQuestion(trimmed);
      setThinking(false);

      if (res.ok) {
        setMessages((prev) => [...prev, { role: "assistant", content: extractAnswer(res.data) }]);
      } else {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: `I couldn't reach the analytics engine: ${res.error}`, isError: true },
        ]);
      }
    },
    [thinking]
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    send(input);
  };

  return (
    <PageShell title="Analytics Chat" subtitle="Ask natural-language questions about the platform, answered by Rohan" onMenuClick={onMenuClick}>
      <Card className="flex flex-col h-[calc(100vh-220px)] min-h-[420px]">
        <SuggestedQuestions questions={SUGGESTED_QUESTIONS} onSelect={send} disabled={thinking} />

        <div ref={scrollRef} className="flex-1 overflow-y-auto px-5 py-5 space-y-4">
          {messages.length === 0 && (
            <EmptyState
              icon={<IcChat className="w-full h-full" />}
              title="Ask Rohan anything about your platform"
              subtitle="Try one of the suggested questions above, or type your own below."
            />
          )}
          {messages.map((m, i) => (
            <ChatBubble key={i} {...m} />
          ))}
          {thinking && <ThinkingBubble />}
        </div>

        <form onSubmit={handleSubmit} className="p-4 border-t border-base-border flex gap-3 flex-shrink-0">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about churn, CLV, segments, reorder rates…"
            className="flex-1 px-4 py-2.5 rounded-xl text-sm outline-none border border-base-border bg-base-surface focus:border-brand transition-colors placeholder:text-slate-500"
          />
          <button
            type="submit"
            disabled={thinking || !input.trim()}
            className="px-4 py-2.5 rounded-xl font-semibold flex items-center gap-2 bg-brand transition-opacity hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed flex-shrink-0"
          >
            <IcSend className="w-4 h-4" />
            <span className="hidden sm:inline">Send</span>
          </button>
        </form>
      </Card>
    </PageShell>
  );
}
