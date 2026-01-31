export const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000";

export type UiReport = {
  task: {
    id: string;
    title: string;
    budgetUsd: number;
    acceptanceCriteria: string[];
  };
  weights: Record<string, number>;
  winner: {
    freelancerId: string;
    totalScore: number;
    highlights: string[];
  };
  referee: Record<string, any>;
  bids: Array<{
    freelancerId: string;
    priceUsd: number;
    etaDays: number;
    confidence: number;
    portfolioScore: number;
    riskFlags: string[];
    notes: string;
    score: {
      price: number;
      eta: number;
      quality: number;
      risk: number;
      total: number;
    };
    rank: number;
    isWinner: boolean;
  }>;
    events?: Array<{
    run_id: string;
    seq: number;
    type: string;
    ts: string;
    round: number;
    summary: string;
    data: Record<string, any>;
  }>;

};

export type RunRequest = {
  title: string;
  acceptance_criteria: string[];
  budget_usd: number;
  weights?: Record<string, number>;
  use_llm: boolean;
  model: string;
};

async function postJson<T>(path: string, body?: any): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : "{}",
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  return res.json();
}

export const api = {
  demoRunUi: (seed = 42, rounds = 2) => postJson<UiReport>(`/demo/run-ui?seed=${seed}&rounds=${rounds}`),
  runUi: (req: RunRequest) => postJson<UiReport>("/run-ui", req),
};
