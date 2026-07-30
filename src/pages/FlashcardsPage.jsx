import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate, useParams } from "react-router-dom";
import { getSummary, API_BASE } from "../lib/api";
import { Card, Button, ErrorBox, SectionTitle, EmptyState } from "../components/Ui";

export default function FlashcardsPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [cards, setCards] = useState([]);
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getSummary(id)
      .then((data) => {
        const built = (data.claims || []).map((c) => ({
          front: c.question || `What does the paper say about ${c.claim_type}?`,
          back: c.text,
        }));
        setCards(built);
      })
      .catch((err) => setError(err.message));
  }, [id]);

  if (error) return <ErrorBox message={error} />;

  if (cards.length === 0) {
    return (
      <div className="mx-auto max-w-lg">
        <SectionTitle
          eyebrow="Study tools"
          title="Flashcards ready when you are"
          description="Turn the paper’s main claims into quick study prompts you can review anywhere."
        />
        <EmptyState
          title="No study cards yet"
          description="The paper may still be processing, or it hasn’t surfaced enough claims for a deck yet."
          action={<Button onClick={() => navigate(`/papers/${id}/chat`, { state: { question: "Create a short set of flashcards from this paper." } })}>Ask for flashcards</Button>}
        />
      </div>
    );
  }

  const card = cards[index];
  const progress = ((index + 1) / cards.length) * 100;

  return (
    <div className="mx-auto max-w-md">
      <SectionTitle
        eyebrow="Study tools"
        title="Review the paper one idea at a time"
        description="Tap the card to flip it and move through the deck at your own pace."
      />

      <div className="mb-6 space-y-2">
        <div className="flex items-center justify-between">
          <p className="text-sm font-semibold text-slate-600 dark:text-slate-300">Card {index + 1} of {cards.length}</p>
          <p className="text-sm font-medium text-blue-600 dark:text-blue-400">{Math.round(progress)}%</p>
        </div>
        <div className="h-2 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
          <motion.div
            className="h-full bg-gradient-to-r from-blue-500 to-blue-600"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.6, ease: "easeOut" }}
          />
        </div>
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={index}
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -50 }}
          transition={{ duration: 0.3 }}
          onClick={() => setFlipped(!flipped)}
          className="group relative cursor-pointer"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 to-purple-600/20 rounded-3xl blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          
          <motion.div
            className="relative rounded-3xl border border-slate-200/50 bg-gradient-to-br from-slate-50 via-white to-blue-50/30 p-8 shadow-[0_8px_32px_rgba(0,0,0,0.08)] transition-all duration-300 group-hover:shadow-[0_20px_40px_rgba(37,99,235,0.15)] group-hover:border-blue-200/50 dark:border-slate-700/50 dark:from-slate-900/50 dark:via-slate-900 dark:to-blue-950/20 dark:shadow-[0_8px_32px_rgba(0,0,0,0.4)] dark:group-hover:shadow-[0_20px_40px_rgba(59,130,246,0.2)]"
          >
            <div className="mb-4 flex items-center justify-between text-sm">
              <span className="inline-flex rounded-full border border-blue-200/50 bg-blue-50/50 px-2.5 py-1 text-xs font-semibold text-blue-700 dark:border-blue-900/50 dark:bg-blue-950/40 dark:text-blue-300">
                {flipped ? "Answer" : "Question"}
              </span>
              <span className="text-xs text-slate-500 dark:text-slate-400">↻ Flip</span>
            </div>

            <motion.div
              key={`${index}-${flipped}`}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.2 }}
              className="min-h-[200px] flex items-center justify-center"
            >
              <p className="text-lg font-medium leading-relaxed text-slate-800 dark:text-slate-100">
                {flipped ? card.back : card.front}
              </p>
            </motion.div>

            <div className="mt-6 text-xs text-slate-500 dark:text-slate-400">
              Tap to {flipped ? "see question" : "reveal answer"}
            </div>
          </motion.div>
        </motion.div>
      </AnimatePresence>

      <div className="mt-8 space-y-4">
        <div className="flex justify-center gap-3">
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button 
              disabled={index === 0} 
              onClick={() => { setFlipped(false); setIndex(index - 1); }}
              className="min-w-[140px]"
            >
              ← Previous
            </Button>
          </motion.div>
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button 
              disabled={index === cards.length - 1} 
              onClick={() => { setFlipped(false); setIndex(index + 1); }}
              className="min-w-[140px]"
            >
              Next →
            </Button>
          </motion.div>
        </div>

        <a 
          href={`${API_BASE}/papers/${id}/flashcards/download`} 
          className="block rounded-xl border border-slate-200/50 bg-gradient-to-r from-slate-50 to-slate-50/50 px-4 py-2.5 text-center text-sm font-semibold text-slate-700 transition-all hover:border-blue-200/50 hover:bg-blue-50/30 dark:border-slate-700/50 dark:from-slate-900/40 dark:to-slate-900/20 dark:text-slate-200 dark:hover:border-blue-900/50 dark:hover:bg-blue-950/20"
        >
          📥 Download Anki deck
        </a>
      </div>
    </div>
  );
}
