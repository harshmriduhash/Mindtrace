"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { ApiError, api } from "@/lib/api/client";

type Baseline = {
  id: string;
  status: string;
  current_index: number;
  total_items: number;
  current_item: {
    id: string;
    type: string;
    prompt: string;
    expected_minutes: number;
  } | null;
  completed_item_ids: string[];
  summary: { average_score?: number; scores?: unknown[]; uncertainty_note?: string };
};

export default function BaselinePage() {
  const [session, setSession] = useState<Baseline | null>(null);
  const [draft, setDraft] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function boot() {
    setError(null);
    try {
      const active = await api<Baseline | null>("/baselines/active");
      if (active && active.status !== "completed") {
        setSession(active);
        return;
      }
      const started = await api<Baseline>("/baselines/start", { method: "POST" });
      setSession(started);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not start baseline");
    }
  }

  useEffect(() => {
    boot();
  }, []);

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!session) return;
    setLoading(true);
    setError(null);
    try {
      const next = await api<Baseline>(`/baselines/${session.id}/submit`, {
        method: "POST",
        json: { response_text: draft, confidence: 0.6 },
      });
      setSession(next);
      setDraft("");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Submit failed");
    } finally {
      setLoading(false);
    }
  }

  async function pause() {
    if (!session) return;
    const next = await api<Baseline>(`/baselines/${session.id}/pause`, { method: "POST" });
    setSession(next);
  }

  async function resume() {
    if (!session) return;
    const next = await api<Baseline>(`/baselines/${session.id}/resume`, { method: "POST" });
    setSession(next);
  }

  if (error && !session) {
    return <div className="panel p-6 text-evidence">{error}</div>;
  }
  if (!session) {
    return <div className="panel animate-pulse-soft p-8 text-ink-500">Preparing balanced baseline…</div>;
  }

  if (session.status === "completed") {
    return (
      <div className="space-y-6">
        <div className="panel p-6">
          <p className="font-mono text-xs uppercase tracking-wider text-accent-strong">Baseline complete</p>
          <h1 className="mt-2 font-display text-3xl text-ink-950">
            Average score {session.summary.average_score ?? "—"} / 5
          </h1>
          <p className="mt-2 text-sm text-ink-600">
            {session.summary.uncertainty_note || "Provisional coaching signal with uncertainty."}
          </p>
          <p className="mt-2 text-sm text-ink-500">
            Completed {session.completed_item_ids.length} / {session.total_items} balanced items across competencies.
          </p>
          <Link href="/app/today" className="btn-primary mt-6 inline-flex">
            Back to Today
          </Link>
        </div>
      </div>
    );
  }

  if (session.status === "paused") {
    return (
      <div className="panel space-y-4 p-6">
        <h1 className="font-display text-3xl text-ink-950">Baseline paused</h1>
        <p className="text-ink-600">
          Progress saved at item {session.current_index + 1} of {session.total_items}.
        </p>
        <button className="btn-primary" onClick={resume}>
          Resume baseline
        </button>
      </div>
    );
  }

  const item = session.current_item;
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="font-mono text-xs uppercase tracking-wider text-accent-strong">Baseline</p>
          <p className="text-sm text-ink-500">
            Item {session.current_index + 1} of {session.total_items} · balanced across competencies
          </p>
        </div>
        <button className="btn-secondary" onClick={pause}>
          Pause
        </button>
      </div>

      {item && (
        <form onSubmit={submit} className="space-y-4">
          <div className="panel p-6">
            <p className="font-mono text-xs uppercase tracking-wider text-accent-strong">{item.type}</p>
            <h1 className="mt-3 font-display text-2xl text-ink-950 md:text-3xl">{item.prompt}</h1>
            <p className="mt-2 text-sm text-ink-500">{item.expected_minutes} min · answer without notes</p>
          </div>
          <textarea
            className="input min-h-56"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            required
            placeholder="Write your answer…"
          />
          {error && <p className="text-sm text-evidence">{error}</p>}
          <button className="btn-primary" disabled={loading || draft.trim().length < 1}>
            {loading ? "Saving…" : session.current_index + 1 >= session.total_items ? "Submit final answer" : "Submit & continue"}
          </button>
        </form>
      )}
    </div>
  );
}
