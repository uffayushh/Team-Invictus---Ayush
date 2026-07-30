// all backend calls go through here so we only have one base url to change

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const demoPaper = {
  id: "demo",
  title: "Designing Calm AI Study Tools",
  authors: ["A. Rivera", "J. Chen"],
  abstract_summary:
    "This demo paper explores how thoughtful AI interfaces can reduce cognitive overload and help learners move from dense reading to useful study outputs.",
  pdf_url: null,
  claims: [
    {
      id: 1,
      text: "Calm interfaces improve focus by reducing visual noise and unnecessary friction.",
      citations: [{ page: 3 }],
    },
    {
      id: 2,
      text: "Study tools work best when they guide the learner step by step instead of overwhelming them.",
      citations: [{ page: 7 }],
    },
    {
      id: 3,
      text: "Generated slides and flashcards become more useful when they are grounded in the original paper.",
      citations: [{ page: 11 }],
    },
  ],
  slides: [
    { title: "Why the experience matters", bullets: ["Less friction", "More clarity", "Better focus"] },
    { title: "From reading to study", bullets: ["Summaries", "Questions", "Flashcards"] },
    { title: "A gentle workflow", bullets: ["Upload", "Review", "Share"] },
  ],
};

function isDemoPaper(paperId) {
  return String(paperId).toLowerCase() === "demo";
}

async function request(path, options = {}) {
  const res = await fetch(BASE_URL + path, {
    ...options,
    headers: {
      ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...options.headers,
    },
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }

  return res.json();
}

export function uploadPaper(formData) {
  return request("/papers/upload", { method: "POST", body: formData });
}

export function processPaper(paperId) {
  if (isDemoPaper(paperId)) {
    return Promise.resolve({ ok: true, paper_id: paperId });
  }
  return request(`/papers/${paperId}/process`, { method: "POST" });
}

export function getStatus(paperId) {
  if (isDemoPaper(paperId)) {
    return Promise.resolve({ status: "ready", current_step: "Demo paper ready", progress: 100 });
  }
  return request(`/papers/${paperId}/status`);
}

export function getSummary(paperId) {
  if (isDemoPaper(paperId)) {
    return Promise.resolve(demoPaper);
  }
  return request(`/papers/${paperId}/summary`);
}

export function sendChatMessage(paperId, message) {
  if (isDemoPaper(paperId)) {
    return Promise.resolve({
      answer: `This demo response explains the paper in a calm, study-friendly way. For your question, “${message}”, the main point is that the interface should reduce friction and make it easy to move from reading to action.`,
      citations: [{ page: 3 }, { page: 7 }],
    });
  }

  return request("/chat", {
    method: "POST",
    body: JSON.stringify({ paper_id: paperId, message }),
  });
}

export function getConceptMap(paperId) {
  if (isDemoPaper(paperId)) {
    return Promise.resolve({
      nodes: [
        { id: 1, label: "Focus" },
        { id: 2, label: "Clarity" },
        { id: 3, label: "Study flow" },
        { id: 4, label: "AI support" },
      ],
    });
  }
  return request(`/papers/${paperId}/concept-map`);
}

export function comparePapers(paperIds) {
  if (paperIds?.includes("demo")) {
    return Promise.resolve({
      papers: [demoPaper],
      rows: [
        { dimension: "Core idea", cells: [{ text: "Better study interfaces reduce cognitive overload." }] },
        { dimension: "Best for", cells: [{ text: "Learners who want a smoother reading-to-study workflow." }] },
      ],
    });
  }

  return request("/compare", {
    method: "POST",
    body: JSON.stringify({ paper_ids: paperIds }),
  });
}

export function listPapers() {
  return Promise.resolve({ papers: [demoPaper] });
}

export const API_BASE = BASE_URL;
