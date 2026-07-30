import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useParams, useNavigate } from "react-router-dom";
import { getStatus, getSummary, processPaper } from "../lib/api";
import { Card, Button, ErrorBox, CitationTag, SectionTitle, EmptyState, Badge, ProcessingState } from "../components/Ui";

export default function PaperPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [status, setStatus] = useState(null);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let timer;

    async function poll() {
      try {
        const s = await getStatus(id);
        setStatus(s);
        if (s.status === "ready") {
          const sum = await getSummary(id);
          setSummary(sum);
        } else if (s.status !== "failed") {
          timer = setTimeout(poll, 1500);
        }
      } catch (err) {
        setError(err.message);
        timer = setTimeout(poll, 3000);
      }
    }

    poll();
    return () => clearTimeout(timer);
  }, [id]);

  async function retry() {
    setError("");
    setStatus(null);
    await processPaper(id);
  }

  if (!summary) {
    const failed = status?.status === "failed";
    return (
      <div className="mx-auto mt-8 max-w-2xl">
        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }}>
        <Card className="text-center shadow-[0_18px_45px_-24px_rgba(15,23,42,0.3)]">
          <p className="mb-1 text-sm font-semibold uppercase tracking-[0.2em] text-blue-600 dark:text-blue-400">Working on it</p>
          <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100">
            {failed ? "We hit a snag while preparing your briefing" : "We’re getting your paper ready"}
          </h2>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
            {failed
              ? "A quick retry usually clears it up."
              : "This usually takes a moment while we extract the main ideas and citations."}
          </p>
          <p className="mt-3 text-sm text-slate-600 dark:text-slate-300">{status?.current_step || "Starting up"}</p>
          <div className="mt-3 h-2 w-full rounded-full bg-slate-100 dark:bg-slate-800">
            <div
              className="h-2 rounded-full bg-blue-600"
              style={{ width: `${Math.max(status?.progress || 5, 5)}%` }}
            />
          </div>
          {failed && (
            <>
              <ErrorBox message={status?.error_message || "Something went wrong."} />
              <Button className="mt-4" onClick={retry}>Try again</Button>
            </>
          )}
          {error && <ErrorBox message={error} />}
        </Card>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <SectionTitle
        eyebrow="Paper briefing"
        title={summary.title || "Paper overview"}
        description="Here’s a warm, readable summary of the paper with its key claims and a few easy next steps."
        action={
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => navigate(`/papers/${id}/chat`, { state: { question: "Summarize the main ideas in this paper." } })}>Ask the paper</Button>
            <Button onClick={() => navigate(`/papers/${id}/flashcards`)}>Open flashcards</Button>
          </div>
        }
      />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card className="overflow-hidden p-0">
          <div className="border-b border-slate-200 bg-slate-50/80 p-4 dark:border-slate-700 dark:bg-slate-800/70">
            <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">Paper preview</h2>
          </div>
          {summary.pdf_url ? (
            <iframe src={summary.pdf_url} className="h-[500px] w-full" title="pdf" />
          ) : (
            <div className="flex h-[500px] items-center justify-center bg-slate-50 text-sm text-slate-400 dark:bg-slate-800/60 dark:text-slate-500">
              PDF preview isn’t available right now.
            </div>
          )}
        </Card>

        <div className="space-y-4">
          <Card>
            <h3 className="mb-2 text-sm font-semibold uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">At a glance</h3>
            <p className="text-sm text-slate-500 dark:text-slate-400">{summary.authors?.join(", ") || "Author information unavailable"}</p>
            <p className="mt-3 text-sm leading-6 text-slate-700 dark:text-slate-300">{summary.abstract_summary}</p>
          </Card>

          <Card>
            <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">Key claims</h3>
            <ul className="space-y-3">
              {(summary.claims || []).map((claim, idx) => (
                <motion.li
                  key={claim.id}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="group list-none rounded-xl border border-slate-200/50 bg-gradient-to-r from-slate-50/40 to-transparent p-3 transition-all hover:border-blue-200/70 hover:bg-gradient-to-r hover:from-blue-50/30 hover:to-blue-50/10 dark:border-slate-700/50 dark:hover:border-blue-900/50 dark:hover:from-blue-950/20"
                >
                  <div className="flex items-start justify-between gap-2">
                    <p className="flex-1 text-sm font-medium text-slate-700 dark:text-slate-200">{claim.text}</p>
                    <Badge label={`${claim.citations?.length || 0} cite`} type="info" />
                  </div>
                  <div className="mt-2 flex flex-wrap items-center gap-2">
                    {(claim.citations || []).map((c, i) => (
                      <CitationTag key={i} page={c.page} />
                    ))}
                    <button
                      className="ml-auto text-xs font-semibold text-blue-600 opacity-0 transition-opacity group-hover:opacity-100 dark:text-blue-400"
                      onClick={() => navigate(`/papers/${id}/chat`, { state: { question: `Tell me more about: ${claim.text}` } })}
                    >
                      Ask about this →
                    </button>
                  </div>
                </motion.li>
              ))}
              {(!summary.claims || summary.claims.length === 0) && (
                <EmptyState
                  title="No claims extracted yet"
                  description="The paper is still loading or the backend hasn’t surfaced any claims yet."
                />
              )}
            </ul>
          </Card>
        </div>
      </div>
    </div>
  );
}
