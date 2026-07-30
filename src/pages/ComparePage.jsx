import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { listPapers, comparePapers } from "../lib/api";
import { Card, Button, ErrorBox, SectionTitle, EmptyState } from "../components/Ui";

export default function ComparePage() {
  const navigate = useNavigate();

  const [papers, setPapers] = useState([]);
  const [selected, setSelected] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    listPapers()
      .then((data) => setPapers(data.papers || data || []))
      .catch((err) => setError(err.message));
  }, []);

  function toggle(paperId) {
    setSelected((prev) =>
      prev.includes(paperId) ? prev.filter((p) => p !== paperId) : [...prev, paperId]
    );
  }

  async function runCompare() {
    setError("");
    try {
      const res = await comparePapers(selected);
      setResult(res);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="mx-auto max-w-4xl">
      <SectionTitle
        eyebrow="Side-by-side view"
        title="Compare papers without the usual spreadsheet headache"
        description="Pick a few papers and get a curated comparison of their ideas, claims, and differences."
      />

      {papers.length === 0 ? (
        <EmptyState
          title="No papers to compare yet"
          description="Upload at least two papers first and then come back here for a side-by-side view."
        />
      ) : (
        <>
          <Card>
            <p className="mb-3 text-sm text-slate-500">
              {selected.length > 0
                ? `${selected.length} paper${selected.length > 1 ? "s" : ""} selected for comparison.`
                : "Choose at least two papers to start comparing them."}
            </p>
            <div className="flex flex-wrap gap-2">
              {papers.map((p) => (
                <button
                  key={p.id}
                  onClick={() => toggle(p.id)}
                  className={
                    "rounded-full border px-3 py-1.5 text-sm transition " +
                    (selected.includes(p.id)
                      ? "border-blue-600 bg-blue-600 text-white"
                      : "border-slate-200 text-slate-700 hover:border-blue-300")
                  }
                >
                  {p.title || p.id}
                </button>
              ))}
            </div>

            <div className="mt-4 flex flex-wrap items-center gap-3">
              <Button onClick={runCompare} disabled={selected.length < 2}>
                Compare selected papers
              </Button>
              <p className="text-sm text-slate-500">{selected.length < 2 ? "Pick two or more papers to continue." : "Ready to compare."}</p>
            </div>
          </Card>

          <ErrorBox message={error} />

          {result && (
            <Card className="mt-4 overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr>
                    <th className="p-2 text-left text-slate-500">Dimension</th>
                    {result.papers?.map((p) => (
                      <th key={p.id} className="p-2 text-left">
                        <button className="text-blue-600 hover:underline" onClick={() => navigate(`/papers/${p.id}`)}>
                          {p.title}
                        </button>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {result.rows?.map((row, i) => (
                    <tr key={i} className="border-t border-slate-100">
                      <td className="p-2 font-medium text-slate-700">{row.dimension}</td>
                      {row.cells?.map((cell, ci) => (
                        <td key={ci} className="p-2 text-slate-600">{cell.text}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
