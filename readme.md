# TaskBounty DAO (Offline-Simulated Chain)
**Multi-Agent Task Bidding + Negotiation + Quality Arbitration + Dispute Resolution**

> Most marketplaces optimize for the *lowest price* — and then everyone acts surprised when the quality is… *also low*.  
TaskBounty DAO simulates a “smart escrow marketplace” where **agents bid**, **negotiate**, and **get judged by an automated quality referee** before payouts happen.

---

## What This Is
TaskBounty DAO is a **serverless-friendly** system that lets a client post a task with acceptance criteria and budget.  
Multiple freelancer agents compete in a **multi-attribute auction** (not just price). A negotiation mediator runs 2–3 counteroffer rounds. A quality referee evaluates deliverables using tests + rubrics + style checks and produces a structured **Decision Report**. If things go wrong, a dispute agent proposes partial payouts or redo plans.

**Key idea:** *Explainable selection* — a cheap bid can lose because quality risk is too high.

---

## Why It’s Different
Most bidding systems choose the lowest price. TaskBounty chooses the **best expected outcome**:

**Score = w_price·Price + w_eta·ETA + w_quality·ExpectedQuality − w_risk·Risk**

The winner is the bid with the best combined score (configurable weights), and the referee outputs **exactly why** in a machine-readable report.

---

## Agents
- **Client Agent**: posts task (criteria + budget + rubric)
- **Freelancer Agents (N=5)**: bid with price, ETA, confidence, portfolio score, and risk flags
- **Negotiation Mediator**: runs 2–3 rounds of counteroffers
- **Quality Referee**: evaluates deliverables (tests, rubric scoring, style, similarity/plagiarism heuristic)
- **Dispute Agent**: proposes partial payouts / redo windows / reassignment

---

## “Offline-Simulated Chain” Ledger

This repo uses an **append-only event log** (“ledger”) so every action is auditable and replayable:
- TASK_POSTED
- BID_SUBMITTED
- COUNTEROFFER_MADE
- WINNER_SELECTED
- DELIVERABLE_SUBMITTED
- REFEREE_EVALUATED
- DISPUTE_OPENED
- PAYOUT_RESOLVED

The goal is transparency + reproducibility without gas fees.

---

## Demo Scenarios
### 1) Cheap bid loses (quality risk too high)
Run the same task with 5 freelancer agents:
- one offers the lowest price but has poor confidence + high risk flags
- another costs slightly more but passes tests and rubric scoring
**Result:** cheap bid loses and the Decision Report explains why.

### 2) Dispute resolution
- winning freelancer fails quality gates
- dispute agent proposes: partial payout (e.g., 30%) + redo window
- if redo fails: reassignment to second-best bidder

---

## Architecture
### Local (default)
CLI simulation + JSONL ledger + local evaluation harness

### Hosted (AWS serverless)
- Frontend: S3 + CloudFront
- Backend: API Gateway (HTTP API) + AWS Lambda
- State/Ledger: DynamoDB
- IaC: AWS SAM or CDK


## Features (Current v0.1)
- Multi-attribute auction scoring (price + ETA + expected quality − risk)
- 5 freelancer agents produce bids
- Ranked bids + winner selection
- UI-friendly JSON response (`/demo/run-ui`)
- React UI: winner card + ranked bids table + score breakdown modal
- **LLM-optional** bid notes via local Ollama (no API keys)

---

## Tech Stack
- **Backend:** Python, FastAPI, Uvicorn, Pydantic, httpx
- **Frontend:** React, Vite, TypeScript
- **LLM (optional):** Ollama + Llama (local)

---

# Running the Project (Local Dev)

## Prerequisites
- **Python 3.12+**
- **Node.js 18+**
- **Ollama** (optional — only needed if you want LLM-generated bid notes)

---

## 1) First-Time Setup

### A) Backend (FastAPI)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt 
```

## 2) Run the API
### USE_LLM=1 OLLAMA_MODEL=llama3.1:8b python -m uvicorn app.main:app --reload


## 3) Start ollama

### a) brew services start ollama
### b) ollama pull llama3.1:8b
### c) ollama list

## 4) Frontend (React + Vite)
### a) cd frontend
### b) npm install
### c) npm run dev

#### Frontend Url: http://localhost:5173


## * Running after first setup
### Terminal 1 Backend
#### cd backend
#### source .venv/bin/activate
#### USE_LLM=1 OLLAMA_MODEL=llama3.1:8b python -m uvicorn app.main:app --reload

### Terminal 2 Frontend
#### cd frontend
#### npm run dev

### Terminal 3
#### ollama serve





