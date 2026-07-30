import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useParams } from "react-router-dom";
import { getSummary, API_BASE } from "../lib/api";
import { Card, Button, ErrorBox, SectionTitle, EmptyState } from "../components/Ui";

export default function SlidesPage() {
  const { id } = useParams();

  const [slides, setSlides] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getSummary(id)
      .then((data) => setSlides(data.slides || []))
      .catch((err) => setError(err.message));
  }, [id]);

  if (error) return <ErrorBox message={error} />;

  return (
    <div>
      <SectionTitle
        eyebrow="Presentation mode"
        title="Turn the paper into a quick talk track"
        description="Preview the generated slides and download them whenever you’re ready to share."
        action={
          <a href={`${API_BASE}/papers/${id}/slides/download`}>
            <Button>Download .pptx</Button>
          </a>
        }
      />

      {slides.length === 0 && (
        <EmptyState
          title="No slides generated yet"
          description="The briefing is still being prepared, or this paper hasn’t produced a slide deck yet."
        />
      )}

      <div className="mt-4 grid gap-4 md:grid-cols-2">
        {slides.map((slide, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2, delay: i * 0.05 }}>
            <Card className="shadow-[0_18px_45px_-24px_rgba(15,23,42,0.3)]">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400 dark:text-slate-500">Slide {i + 1}</p>
              <h3 className="mb-2 mt-1 text-sm font-semibold text-slate-800 dark:text-slate-100">{slide.title}</h3>
              <ul className="list-inside list-disc space-y-1 text-sm text-slate-600 dark:text-slate-300">
                {(slide.bullets || []).map((b, bi) => <li key={bi}>{b}</li>)}
              </ul>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
