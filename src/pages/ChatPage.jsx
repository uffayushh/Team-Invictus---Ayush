import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useParams, useLocation } from "react-router-dom";
import { sendChatMessage } from "../lib/api";
import { Card, Button, ErrorBox, CitationTag } from "../components/Ui";

export default function ChatPage() {
  const { id } = useParams();
  const location = useLocation();

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState(location.state?.question || "");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  const messagesEndRef = useRef(null);
  const containerRef = useRef(null);
  const inputRef = useRef(null);
  const isAtBottomRef = useRef(true);

  const SUGGESTED_QUESTIONS = [
    "What are the main claims of this paper?",
    "Summarize the methodology used.",
    "What are the key results and findings?",
    "Explain the practical implications.",
  ];

  const handleScroll = () => {
    if (!containerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    const distanceToBottom = scrollHeight - scrollTop - clientHeight;
    isAtBottomRef.current = distanceToBottom < 100;
  };

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    if (isAtBottomRef.current) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, sending]);

  async function sendMessage(textToSend) {
    const question = (textToSend !== undefined ? textToSend : input).trim();
    if (!question || sending) return;

    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setInput("");
    setSending(true);
    setError("");
    isAtBottomRef.current = true;

    try {
      const res = await sendChatMessage(id, question);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: res.answer, citations: res.citations || [] },
      ]);
    } catch (err) {
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setSending(false);
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    sendMessage();
  }

  function handleInputChange(e) {
    setInput(e.target.value);
    if (error) setError("");
  }

  return (
    <div className="mx-auto max-w-3xl">
      <Card className="flex h-[72vh] flex-col border-slate-200 p-0 shadow-[0_18px_45px_-24px_rgba(15,23,42,0.3)] dark:border-slate-700">
        <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3 dark:border-slate-700">
          <div>
            <h2 className="font-semibold text-slate-900 dark:text-slate-100">Paper chat</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">Ask about the paper, its claims, and citations.</p>
          </div>
        </div>

        <div
          ref={containerRef}
          onScroll={handleScroll}
          className="mb-3 flex-1 space-y-3 overflow-y-auto px-4 py-4"
        >
          {messages.length === 0 && !sending && (
            <div className="mt-8 rounded-2xl border border-dashed border-slate-200 bg-slate-50/80 p-6 text-center text-sm text-slate-500 dark:border-slate-700 dark:bg-slate-800/70 dark:text-slate-400">
              <p className="mb-4 font-medium text-slate-700 dark:text-slate-300">
                Ask a question about this paper to get a grounded answer.
              </p>
              <div className="flex flex-wrap justify-center gap-2">
                {SUGGESTED_QUESTIONS.map((q, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => sendMessage(q)}
                    className="rounded-xl border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 shadow-sm transition-all hover:border-blue-300 hover:bg-blue-50 hover:text-blue-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:border-blue-500 dark:hover:bg-slate-700 dark:hover:text-blue-400"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((m, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: m.role === "user" ? 20 : -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3 }}
              className={m.role === "user" ? "text-right" : "text-left"}
            >
              <div className="flex items-end gap-2" style={{ justifyContent: m.role === "user" ? "flex-end" : "flex-start" }}>
                {m.role === "assistant" && <div className="text-xl">📚</div>}
                <motion.div
                  whileHover={{ scale: 1.02 }}
                  className={
                    "inline-block max-w-[85%] rounded-2xl px-4 py-3 text-sm shadow-md backdrop-blur " +
                    (m.role === "user"
                      ? "rounded-br-md bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-[0_4px_12px_rgba(37,99,235,0.3)]"
                      : "rounded-bl-md border border-slate-200/50 bg-gradient-to-br from-slate-50 to-slate-50/50 text-slate-700 dark:border-slate-700/50 dark:from-slate-800 dark:to-slate-800/50 dark:text-slate-200")
                  }
                >
                  <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="whitespace-pre-wrap leading-relaxed"
                  >
                    {m.text}
                  </motion.div>
                  {m.citations?.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-1 border-t border-current border-opacity-10 pt-2">
                      {m.citations.map((c, ci) => (
                        <CitationTag key={ci} page={c.page} />
                      ))}
                    </div>
                  )}
                </motion.div>
                {m.role === "user" && <div className="text-xl">👤</div>}
              </div>
            </motion.div>
          ))}

          <AnimatePresence>
            {sending && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="text-left"
              >
                <div className="inline-flex items-center gap-3 rounded-2xl rounded-bl-md border border-slate-200/50 bg-gradient-to-br from-slate-50 to-slate-50/50 px-4 py-3 text-sm text-slate-600 shadow-md dark:border-slate-700/50 dark:from-slate-800 dark:to-slate-800/50 dark:text-slate-300">
                  <div className="flex gap-1.5">
                    {[0, 1, 2].map((i) => (
                      <motion.div
                        key={i}
                        className="h-2 w-2 rounded-full bg-blue-500"
                        animate={{ y: [0, -8, 0] }}
                        transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.15 }}
                      />
                    ))}
                  </div>
                  <span className="font-medium">Thinking...</span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="border-t border-slate-200/50 bg-gradient-to-t from-white/40 to-white/20 px-4 py-3 backdrop-blur dark:border-slate-700/50 dark:from-slate-950/40 dark:to-slate-950/20">
          <ErrorBox message={error} />

          <div className="mt-3 flex gap-2">
            <motion.input
              ref={inputRef}
              whileFocus={{ scale: 1.01 }}
              value={input}
              onChange={handleInputChange}
              placeholder="Ask something about the paper..."
              className="flex-1 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm shadow-sm outline-none transition-all focus:border-blue-400 focus:ring-2 focus:ring-blue-400/20 dark:border-slate-700 dark:bg-slate-900/50 dark:text-slate-100 dark:focus:border-blue-400"
              disabled={sending}
            />
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button type="submit" disabled={sending} className="min-w-[100px]">
                {sending ? "Sending..." : "Send"}
              </Button>
            </motion.div>
          </div>
        </form>
      </Card>
    </div>
  );
}