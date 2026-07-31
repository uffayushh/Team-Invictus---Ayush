from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import paper, jobs , outputs

app = FastAPI(title="Research Paper Briefing Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=getattr(settings, "CORS_ORIGINS", ["http://localhost:3000"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(paper.router)
app.include_router(jobs.router)
app.include_router(outputs.router)

@app.get("/health")
def health():
    return {"status": "ok"}