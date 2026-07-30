import { useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { uploadPaper, processPaper } from "../lib/api";
import { Button, Card, ErrorBox, SectionTitle } from "../components/Ui";

const workflowSteps = ["Upload your PDF", "We process the paper", "You explore it through chat, notes, and slides"];

const highlights = [
  { title: "Instant overview", description: "Get a clear summary of the paper’s main ideas in plain language." },
  { title: "Ask anything", description: "Follow up with questions and keep the conversation moving naturally." },
  { title: "Study-ready outputs", description: "Turn complex reading into flashcards, concept maps, and slide-ready content." },
];

const quickOptions = [
  { label: "Quick summary", hint: "Ask for the core takeaway" },
  { label: "Key claims", hint: "Surface the paper’s main arguments" },
  { label: "Study deck", hint: "Turn it into flashcards" },
];

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const navigate = useNavigate();

  function handleFileSelection(selectedFile) {
    if (!selectedFile) return;

    if (selectedFile.type !== "application/pdf") {
      setError("Only PDF files are supported.");
      return;
    }

    setFile(selectedFile);
    setError("");
  }

  async function handleSubmit() {
    if (!file) {
      setError("Please choose a PDF file first.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const form = new FormData();
      form.append("file", file);

      const { paper_id } = await uploadPaper(form);
      await processPaper(paper_id);

      navigate(`/papers/${paper_id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto mt-3 max-w-4xl space-y-5">
      <SectionTitle
        eyebrow="Welcome"
        title="Turn a paper into a calm study companion"
        description="Upload a PDF and let the app guide you from first read-through to notes, chat, and presentation-ready material."
      />

      <div className="grid gap-3 rounded-2xl border border-slate-200 bg-white/80 p-4 shadow-sm dark:border-slate-700 dark:bg-slate-900/80 md:grid-cols-[1.2fr_0.8fr]">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-600 dark:text-blue-400">Start here</p>
          <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
            Pick a paper, upload it, and start with one of the most useful next steps below.
          </p>
        </div>
        <div className="flex flex-wrap gap-2 md:justify-end">
          {quickOptions.map((option) => (
            <button
              key={option.label}
              type="button"
              className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-sm text-slate-700 transition hover:border-blue-300 hover:bg-blue-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:border-blue-500 dark:hover:bg-blue-950/40"
            >
              <span className="font-medium">{option.label}</span>
              <span className="ml-2 text-xs text-slate-500 dark:text-slate-400">{option.hint}</span>
            </button>
          ))}
        </div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, ease: "easeOut" }}
      >
      <Card className="overflow-hidden border-slate-200/70 bg-white/80 p-0 shadow-[0_18px_45px_-24px_rgba(15,23,42,0.35)] dark:border-slate-700 dark:bg-slate-900/80">
        <div className="grid gap-0 lg:grid-cols-[1.15fr_0.85fr]">
          <div className="p-6 sm:p-8">
            <div className="inline-flex items-center rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-blue-700 dark:border-blue-900 dark:bg-blue-950/40 dark:text-blue-300">
              New • PDF to briefing
            </div>

            <h3 className="mt-4 text-2xl font-semibold text-slate-900 dark:text-slate-100">
              Drop in a paper and let the experience unfold gently.
            </h3>
            <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">
              Upload once and turn dense reading into a clearer, more human study flow with summaries, follow-up chat, and polished outputs.
            </p>

            <label
              onDragOver={(e) => {
                e.preventDefault();
                setDragActive(true);
              }}
              onDragLeave={() => setDragActive(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragActive(false);
                handleFileSelection(e.dataTransfer.files?.[0]);
              }}
              className={`mt-6 flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-10 text-center transition ${
                dragActive
                  ? "border-blue-500 bg-blue-50 dark:border-blue-400 dark:bg-blue-950/30"
                  : "border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-800/70"
              }`}
            >
              <input
                type="file"
                accept="application/pdf"
                onChange={(e) => handleFileSelection(e.target.files?.[0])}
                className="hidden"
              />
              <div className="text-4xl">📄</div>
              <p className="mt-3 font-medium text-slate-700 dark:text-slate-200">
                {dragActive ? "Drop your PDF here" : "Drag and drop a PDF or click to browse"}
              </p>
              <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Single PDF files only</p>
            </label>

            {file && (
              <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200">
                Selected: <span className="font-medium">{file.name}</span>
              </div>
            )}

            <div className="mt-5 flex flex-wrap items-center gap-3">
              <Button className="min-w-[220px]" onClick={handleSubmit} disabled={loading}>
                {loading ? "Preparing your briefing..." : "Upload & build my briefing"}
              </Button>
              <Button className="min-w-[200px]" onClick={() => navigate("/papers/demo")}>
                Try the demo preview
              </Button>
              <span className="rounded-full border border-slate-200 bg-white px-3 py-1 text-sm text-slate-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300">
                Fast, private, and simple
              </span>
            </div>

            <ErrorBox message={error} />
          </div>

          <div className="border-t border-slate-200 bg-slate-50/70 p-6 dark:border-slate-700 dark:bg-slate-800/40 lg:border-l lg:border-t-0">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">What you’ll get</p>
            <ul className="mt-4 space-y-3 text-sm text-slate-600 dark:text-slate-300">
              {highlights.map((item) => (
                <li key={item.title} className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm dark:border-slate-700 dark:bg-slate-900">
                  <p className="font-semibold text-slate-800 dark:text-slate-100">{item.title}</p>
                  <p className="mt-1 text-slate-600 dark:text-slate-400">{item.description}</p>
                </li>
              ))}
            </ul>

            <div className="mt-6 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-900">
              <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">Quick workflow</p>
              <div className="mt-3 space-y-2">
                {workflowSteps.map((step, index) => (
                  <div key={step} className="flex items-center gap-3 text-sm text-slate-600 dark:text-slate-300">
                    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-xs font-semibold text-blue-700 dark:bg-blue-950/60 dark:text-blue-300">
                      {index + 1}
                    </span>
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </Card>
      </motion.div>
    </div>
  );
}
