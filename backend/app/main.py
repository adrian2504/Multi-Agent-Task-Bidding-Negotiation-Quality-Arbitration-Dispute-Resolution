from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from .sim.demo import run_demo
from .llm.ollama import OllamaLLM
from .core.presenter import to_ui
import os

from .core.requests import RunRequest
from .core.models import Task
from .sim.demo import DEFAULT_WEIGHTS  # or move weights to config
from .agents.freelancer import FreelancerProfile, propose_bid
from .core.report import pick_winner
from .core.presenter import to_ui

app = FastAPI(title="TaskBounty DAO", version="0.1")

# CORS for frontend later (React/Vite runs on :5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_llm():
    if os.getenv("USE_LLM", "1") != "1":
        return None
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    return OllamaLLM(model=model, base_url="http://127.0.0.1:11434/api")

@app.get("/")
def root():
    return {"name": "TaskBounty DAO", "docs": "/docs", "health": "/health"}

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/demo/run")
async def demo_run():
    llm = get_llm()
    try:
        report = await run_demo(llm=llm)
        return report.model_dump()
    except Exception:
        report = await run_demo(llm=None)
        data = report.model_dump()
        data["rationale"].insert(0, "LLM unavailable; ran deterministic mode.")
        return data

#  frontend-friendly response
@app.post("/demo/run-ui")
async def demo_run_ui(seed: int = Query(42), rounds: int = Query(2)):
    llm = get_llm()
    try:
        report = await run_demo(llm=llm, seed=seed, rounds=rounds)
    except Exception:
        report = await run_demo(llm=None, seed=seed, rounds=rounds)
    return to_ui(report)


@app.post("/run-ui")
async def run_ui(req: RunRequest):
    task = Task(
        title=req.title,
        acceptance_criteria=req.acceptance_criteria,
        budget_usd=req.budget_usd,
    )

    weights = req.weights or {"price": 0.9, "eta": 0.35, "quality": 1.2, "risk": 1.1}

    llm = None
    if req.use_llm and os.getenv("USE_LLM", "1") == "1":
        llm = OllamaLLM(model=req.model, base_url="http://127.0.0.1:11434/api")

    freelancers = [
        FreelancerProfile("cheap_risky", 0.35, 2, 80,  ["low_test_coverage", "copy_paste_history"]),
        FreelancerProfile("steady_mid",  0.70, 3, 140, []),
        FreelancerProfile("fast_good",   0.78, 2, 165, ["tight_schedule"]),
        FreelancerProfile("slow_safe",   0.82, 5, 150, []),
        FreelancerProfile("premium",     0.92, 3, 210, []),
    ]

    bids = [await propose_bid(task, f, llm=llm) for f in freelancers]
    report = pick_winner(task, bids, weights)
    return to_ui(report)