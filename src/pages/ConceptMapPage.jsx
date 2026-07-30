import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useParams, useNavigate } from "react-router-dom";
import { getConceptMap } from "../lib/api";
import { Card, ErrorBox, SectionTitle, EmptyState } from "../components/Ui";

export default function ConceptMapPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getConceptMap(id)
      .then(setData)
      .catch((err) => setError(err.message));
  }, [id]);

  if (error) return <ErrorBox message={error} />;
  if (!data) return <p className="mt-10 text-center text-sm text-slate-400 dark:text-slate-500">Building the concept map...</p>;

  const nodes = data.nodes || [];

  function askAbout(label) {
    navigate(`/papers/${id}/chat`, { state: { question: `Tell me more about ${label}` } });
  }

  return (
    <div className="mx-auto max-w-3xl">
      <SectionTitle
        eyebrow="Learning map"
        title="Explore the paper through its ideas"
        description="Click any concept to ask the chat for a clearer explanation or a deeper example."
      />
      <Card className="shadow-[0_18px_45px_-24px_rgba(15,23,42,0.3)]">
        <div className="flex flex-wrap gap-2">
          {nodes.map((node) => (
            <motion.button
              key={node.id}
              whileHover={{ y: -2, scale: 1.02 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => askAbout(node.label)}
              className="rounded-full border border-slate-200 px-3 py-1.5 text-sm text-slate-700 transition hover:border-blue-300 hover:bg-blue-50 dark:border-slate-700 dark:text-slate-200 dark:hover:border-blue-500 dark:hover:bg-blue-950/40"
            >
              {node.label}
            </motion.button>
          ))}
          {nodes.length === 0 && (
            <EmptyState
              title="No concepts found yet"
              description="This paper may still be processing or it simply doesn’t have a concept map available yet."
            />
          )}
        </div>
      </Card>
    </div>
  );
}
