# Paper Briefing Agent — Frontend

## Setup

```
npm install
cp .env.example .env   # set VITE_API_URL to your FastAPI backend
npm run dev
```

## Pages

- `/` — upload a PDF, starts processing
- `/papers/:id` — viewer (summary + claims), shows processing progress until ready
- `/papers/:id/chat` — chat with citations
- `/papers/:id/flashcards` — flip-card quiz + Anki download
- `/papers/:id/concept-map` — clickable concept list, feeds into chat
- `/papers/:id/slides` — slide bullet preview + pptx download
- `/compare` — pick 2+ papers, see a comparison table

All backend calls go through `src/lib/api.js`.
