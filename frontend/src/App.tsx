import { useEffect, useMemo, useState } from "react";
import { api } from "./api";
import type { RunRequest, UiReport } from "./api";
import "./style.css";

function Badge({ children, tone = "neutral" }: { children: any; tone?: "neutral" | "danger" | "success" }) {
  return <span className={`badge ${tone}`}>{children}</span>;
}

function Card({ title, children }: { title?: string; children: any }) {
  return (
    <div className="card">
      {title ? <div className="cardTitle">{title}</div> : null}
      <div>{children}</div>
    </div>
  );
}

function fmt(n: number) {
  return Number.isFinite(n) ? n.toFixed(4).replace(/\.?0+$/, "") : String(n);
}

function WinnerCard({ report }: { report: UiReport }) {
  return (
    <Card title="Winner">
      <div className="row">
        <div className="big">{report.winner.freelancerId}</div>
        <Badge tone="success">Score: {fmt(report.winner.totalScore)}</Badge>
      </div>
      <ul className="list">
        {report.winner.highlights.map((h, i) => (
          <li key={i}>{h}</li>
        ))}
      </ul>
    </Card>
  );
}

function RefereeCard({ report }: { report: UiReport }) {
  const entries = Object.entries(report.referee ?? {});
  return (
    <Card title="Referee Summary">
      {entries.length === 0 ? (
        <div className="muted">No referee metrics.</div>
      ) : (
        <div className="kv">
          {entries.map(([k, v]) => (
            <div key={k} className="kvRow">
              <div className="kvKey">{k}</div>
              <div className="kvVal">{typeof v === "object" ? JSON.stringify(v) : String(v)}</div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}

function TaskCard({ report }: { report: UiReport }) {
  return (
    <Card title="Task">
      <div className="kv">
        <div className="kvRow">
          <div className="kvKey">Title</div>
          <div className="kvVal">{report.task.title}</div>
        </div>
        <div className="kvRow">
          <div className="kvKey">Budget</div>
          <div className="kvVal">${report.task.budgetUsd.toFixed(2)}</div>
        </div>
        <div className="kvRow">
          <div className="kvKey">Criteria</div>
          <div className="kvVal">
            <ul className="list">
              {report.task.acceptanceCriteria.map((c, i) => (
                <li key={i}>{c}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </Card>
  );
}

function WeightsCard({ report }: { report: UiReport }) {
  const rows = Object.entries(report.weights ?? {});
  return (
    <Card title="Weights">
      <div className="kv">
        {rows.map(([k, v]) => (
          <div className="kvRow" key={k}>
            <div className="kvKey">{k}</div>
            <div className="kvVal">{fmt(v)}</div>
          </div>
        ))}
      </div>
    </Card>
  );
}

function ScoreBreakdown({ bid, onClose }: { bid: UiReport["bids"][number]; onClose: () => void }) {
  return (
    <div className="modalBackdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modalHeader">
          <div className="modalTitle">Score breakdown: {bid.freelancerId}</div>
          <button className="btn" onClick={onClose}>
            Close
          </button>
        </div>
        <div className="kv">
          <div className="kvRow"><div className="kvKey">price_term</div><div className="kvVal">{fmt(bid.score.price)}</div></div>
          <div className="kvRow"><div className="kvKey">eta_term</div><div className="kvVal">{fmt(bid.score.eta)}</div></div>
          <div className="kvRow"><div className="kvKey">quality_term</div><div className="kvVal">{fmt(bid.score.quality)}</div></div>
          <div className="kvRow"><div className="kvKey">risk_term</div><div className="kvVal">{fmt(bid.score.risk)}</div></div>
          <div className="kvRow"><div className="kvKey"><b>total</b></div><div className="kvVal"><b>{fmt(bid.score.total)}</b></div></div>
        </div>

        {bid.notes ? (
          <>
            <div className="sectionTitle">LLM Bid Note</div>
            <div className="note">{bid.notes}</div>
          </>
        ) : (
          <div className="muted">No LLM note (deterministic mode).</div>
        )}

        {bid.riskFlags?.length ? (
          <>
            <div className="sectionTitle">Risk Flags</div>
            <div className="badges">
              {bid.riskFlags.map((rf) => (
                <Badge key={rf} tone="danger">{rf}</Badge>
              ))}
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
}

function BidsTable({ report }: { report: UiReport }) {
  const [selected, setSelected] = useState<UiReport["bids"][number] | null>(null);

  return (
    <Card title="Bids (ranked)">
      <div className="tableWrap">
        <table className="table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Freelancer</th>
              <th>Price</th>
              <th>ETA</th>
              <th>Confidence</th>
              <th>Portfolio</th>
              <th>Total Score</th>
              <th>Flags</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {report.bids.map((b) => (
              <tr key={b.freelancerId} className={b.isWinner ? "winnerRow" : ""}>
                <td>{b.rank}</td>
                <td className="mono">
                  {b.freelancerId} {b.isWinner ? <Badge tone="success">WIN</Badge> : null}
                </td>
                <td>${b.priceUsd.toFixed(2)}</td>
                <td>{b.etaDays}d</td>
                <td>{fmt(b.confidence)}</td>
                <td>{fmt(b.portfolioScore)}</td>
                <td><b>{fmt(b.score.total)}</b></td>
                <td>
                  <div className="badges">
                    {(b.riskFlags ?? []).slice(0, 2).map((rf) => (
                      <Badge key={rf} tone="danger">{rf}</Badge>
                    ))}
                    {(b.riskFlags?.length ?? 0) > 2 ? <Badge>+{b.riskFlags.length - 2}</Badge> : null}
                  </div>
                </td>
                <td>
                  <button className="btn" onClick={() => setSelected(b)}>
                    Details
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selected ? <ScoreBreakdown bid={selected} onClose={() => setSelected(null)} /> : null}
    </Card>
  );
}

  function TaskForm({ onRun, onRunDemo, }: { onRun: (req: RunRequest) => void; onRunDemo: (seed: number, rounds: number) => void; }) {
  
  const [seed, setSeed] = useState(42);
  const [rounds, setRounds] = useState(2);
  const [title, setTitle] = useState("Build a FastAPI endpoint + unit tests");
  const [budgetUsd, setBudgetUsd] = useState(250);
  const [criteriaText, setCriteriaText] = useState(
    "POST /tasks creates a task\nPOST /tasks/{id}/run selects winner\nReturn a JSON decision report\nInclude basic unit tests"
  );

  // weights
  const [wPrice, setWPrice] = useState(0.9);
  const [wEta, setWEta] = useState(0.35);
  const [wQuality, setWQuality] = useState(1.2);
  const [wRisk, setWRisk] = useState(1.1);

  const [useLlm, setUseLlm] = useState(true);
  const [model, setModel] = useState("llama3.1:8b");

  const acceptance = useMemo(
    () => criteriaText.split("\n").map((s) => s.trim()).filter(Boolean),
    [criteriaText]
  );

  return (
    <Card title="Run a Task">
      <div className="formGrid">
        <div className="field">
          <label>Title</label>
          <input value={title} onChange={(e) => setTitle(e.target.value)} />
        </div>

        <div className="field">
          <label>Budget (USD)</label>
          <input
            type="number"
            min={1}
            value={budgetUsd}
            onChange={(e) => setBudgetUsd(Number(e.target.value))}
          />
        </div>

        <div className="field full">
          <label>Acceptance Criteria (one per line)</label>
          <textarea rows={5} value={criteriaText} onChange={(e) => setCriteriaText(e.target.value)} />
        </div>

        <div className="field">
          <label>Weight: price</label>
          <input type="number" step="0.05" value={wPrice} onChange={(e) => setWPrice(Number(e.target.value))} />
        </div>
        <div className="field">
          <label>Weight: eta</label>
          <input type="number" step="0.05" value={wEta} onChange={(e) => setWEta(Number(e.target.value))} />
        </div>
        <div className="field">
          <label>Weight: quality</label>
          <input type="number" step="0.05" value={wQuality} onChange={(e) => setWQuality(Number(e.target.value))} />
        </div>
        <div className="field">
          <label>Weight: risk</label>
          <input type="number" step="0.05" value={wRisk} onChange={(e) => setWRisk(Number(e.target.value))} />
        </div>

        <div className="field">
          <label className="inline">
            <input type="checkbox" checked={useLlm} onChange={(e) => setUseLlm(e.target.checked)} />
            Use LLM (Ollama local)
          </label>
        </div>


        <div className="field">
          <label>Model</label>
          <input value={model} onChange={(e) => setModel(e.target.value)} placeholder="llama3.1:8b" />
        </div>
                <div className="field">
          <label>Seed (replayable)</label>
          <input type="number" value={seed} onChange={(e) => setSeed(Number(e.target.value))} />
        </div>

        <div className="field">
          <label>Negotiation Rounds</label>
          <input
            type="number"
            min={0}
            max={5}
            value={rounds}
            onChange={(e) => setRounds(Number(e.target.value))}
          />
        </div>

              <div className="actions full" style={{ gap: 10 }}>
          <button className="btn" onClick={() => onRunDemo(seed, rounds)}>
            Run Demo (seeded)
          </button>

          <button
            className="btn primary"
            onClick={() =>
              onRun({
                title,
                acceptance_criteria: acceptance,
                budget_usd: budgetUsd,
                weights: { price: wPrice, eta: wEta, quality: wQuality, risk: wRisk },
                use_llm: useLlm,
                model,
              })
            }
          >
            Run Custom Task
          </button>
        </div>

        
      </div>
    </Card>
  );
}

function ScoreTrendCard({ report }: { report: UiReport }) {
  const rows = report.scoreHistory ?? [];
  if (rows.length === 0) {
    return (
      <Card title="Score Trend">
        <div className="muted">No score history available.</div>
      </Card>
    );
  }

  // group by round
  const byRound = new Map<number, typeof rows>();
  for (const r of rows) {
    if (!byRound.has(r.round)) byRound.set(r.round, []);
    byRound.get(r.round)!.push(r);
  }

  const rounds = Array.from(byRound.keys()).sort((a, b) => a - b);

  return (
    <Card title="Score Trend (per round)">
      {rounds.map((round) => {
        const rrows = [...(byRound.get(round) ?? [])].sort((a, b) => b.total - a.total);
        return (
          <div key={round} style={{ marginBottom: 14 }}>
            <div className="row" style={{ marginBottom: 8 }}>
              <div className="mono"><b>Round {round}</b></div>
              <Badge>Top: {rrows[0]?.freelancerId}</Badge>
            </div>

            <div className="tableWrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>Freelancer</th>
                    <th>Total</th>
                    <th>price</th>
                    <th>eta</th>
                    <th>quality</th>
                    <th>risk</th>
                  </tr>
                </thead>
                <tbody>
                  {rrows.map((x, i) => (
                    <tr key={x.freelancerId} className={x.freelancerId === report.winner.freelancerId ? "winnerRow" : ""}>
                      <td>{i + 1}</td>
                      <td className="mono">{x.freelancerId}</td>
                      <td><b>{fmt(x.total)}</b></td>
                      <td>{fmt(x.price)}</td>
                      <td>{fmt(x.eta)}</td>
                      <td>{fmt(x.quality)}</td>
                      <td>{fmt(x.risk)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        );
      })}
    </Card>
  );
}



function TimelineCard({ report }: { report: UiReport }) {
  const events = report.events ?? [];
  let lastLeader: string | null = null;

  return (
    <Card title="Negotiation Timeline">
      {events.length === 0 ? (
        <div className="muted">No events.</div>
      ) : (
        <div className="timeline">
          {events.map((e) => {
            const leader = e.data?.leader ?? null;
            const leaderChanged = leader && lastLeader && leader !== lastLeader;
            if (leader) lastLeader = leader;

            const top3 = e.data?.top3 as [string, number][] | undefined;

            return (
              <div className="timelineItem" key={e.seq}>
                <div className="timelineDot" />
                <div className="timelineBody">
                  <div className="timelineTop">
                    <div className="mono">
                      <b>#{e.seq}</b> {e.type}
                    </div>
                    <div className="badges">
                      <Badge>Round {e.round}</Badge>
                      {leader ? <Badge tone="success">Leader: {leader}</Badge> : null}
                      {leaderChanged ? <Badge tone="danger">Leader changed</Badge> : null}
                    </div>
                  </div>

                  <div className="timelineSummary">{e.summary}</div>

                  {top3?.length ? (
                    <div className="top3">
                      <div className="muted" style={{ fontWeight: 800, marginTop: 8 }}>Top 3 snapshot</div>
                      <ol className="list">
                        {top3.map(([id, score]) => (
                          <li key={id} className="mono">
                            {id} — {fmt(score)}
                          </li>
                        ))}
                      </ol>
                    </div>
                  ) : null}

                  <details>
                    <summary className="timelineMore">payload</summary>
                    <pre className="code">{JSON.stringify(e.data, null, 2)}</pre>
                  </details>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
}




export default function App() {
  const [report, setReport] = useState<UiReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

    async function loadDemo(seed = 42, rounds = 2) {
    setLoading(true);
    setErr(null);
    try {
      const r = await api.demoRunUi(seed, rounds);
      setReport(r);
    } catch (e: any) {
      setErr(e.message ?? String(e));
    } finally {
      setLoading(false);
    }
  }


  async function runTask(req: RunRequest) {
    setLoading(true);
    setErr(null);
    try {
      const r = await api.runUi(req);
      setReport(r);
    } catch (e: any) {
      setErr(e.message ?? String(e));
    } finally {
      setLoading(false);
    }
  }

    useEffect(() => {
    loadDemo(42, 2);
  }, []);


  return (
    <div className="page">
      <div className="header">
        <div>
          <div className="title">TaskBounty DAO</div>
          <div className="subtitle">Multi-agent bidding + scoring + explainable winner selection</div>
        </div>
        <div className="headerActions">
          <button className="btn" onClick={() => loadDemo(42, 2)} disabled={loading}>
  Load Demo
</button>
        </div>
      </div>

      {err ? <div className="error">{err}</div> : null}
      {loading ? <div className="muted">Running…</div> : null}

      <div className="grid">
        <div className="col">
          <TaskForm onRun={runTask} onRunDemo={(seed, rounds) => loadDemo(seed, rounds)} />

          {report ? <BidsTable report={report} /> : null}
        </div>

        <div className="col">
          {report ? <WinnerCard report={report} /> : null}
          {report ? <TaskCard report={report} /> : null}
          {report ? <WeightsCard report={report} /> : null}

        </div>
        <div className="col">
          {report ? <RefereeCard report={report} /> : null}
          {report ? <TimelineCard report={report} /> : null}
          {report ? <ScoreTrendCard report={report} /> : null}
        </div>
        <div className="col">
          {report ? (
            <Card title="Raw JSON (debug)">
              <pre className="code">{JSON.stringify(report, null, 2)}</pre>
            </Card>
          ) : null}
        </div>
      </div>
    </div>
  );
}
