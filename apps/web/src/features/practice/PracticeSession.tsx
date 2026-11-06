"use client";

import { FormEvent, useEffect, useState } from "react";
import { ApiError, Evaluation, PracticeItem, api } from "@/lib/api/client";

export function PracticeSession({
  itemId,
  fallbackType,
}: {
  itemId?: string | null;
  fallbackType?: string;
}) {
  const [item, setItem] = useState<PracticeItem | null>(null);
  const [attemptId, setAttemptId] = useState<string | null>(null);
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [draft, setDraft] = useState("");

  useEffect(() => {
    async function boot() {
      setError(null);
      setEvaluation(null);
      let targetId = itemId;
      if (!targetId && fallbackType) {
        const items = await api<PracticeItem[]>(`/practice-items?type=${fallbackType}`);
        targetId = items[0]?.id;
      }
      if (!targetId) {
        setError("No practice item available yet. Seed the System Design path.");
        return;
      }
      const practice = await api<PracticeItem>(`/practice-items/${targetId}`);
      setItem(practice);
      const attempt = await api<{ id: string }>("/assessments", {
        method: "POST",
        json: { practice_item_id: practice.id, idempotency_key: crypto.randomUUID() },
      });
      setAttemptId(attempt.id);
      const saved = localStorage.getItem(`mindtrace-draft-${practice.id}`);
      if (saved) setDraft(saved);
    }
    boot().catch((err) => setError(err instanceof ApiError ? err.message : "Could not start practice"));
  }, [itemId, fallbackType]);

  useEffect(() => {
    if (!item) return;
    localStorage.setItem(`mindtrace-draft-${item.id}`, draft);
  }, [draft, item]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!attemptId) return;
    setLoading(true);
    setError(null);
    try {
      const result = await api<Evaluation>(`/assessments/${attemptId}/submit`, {
        method: "POST",
        json: {
          response_text: draft,
          confidence: 0.6,
          hint_used: false,
        },
      });
      setEvaluation(result);
      if (item) localStorage.removeItem(`mindtrace-draft-${item.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Submit failed — your draft is preserved");
    } finally {
      setLoading(false);
    }
  }

  if (error && !item) {
    return <div className="panel p-6 text-evidence">{error}</div>;
  }

  if (!item) {
    return <div className="panel animate-pulse-soft p-8 text-ink-500">Preparing practice session…</div>;
  }

  if (evaluation) {
    const r = evaluation.result_json;
    return (
      <div className="space-y-6">
        <div className="panel p-6">
          <p className="font-mono text-xs uppercase tracking-wider text-accent-strong">Feedback</p>
          <h2 className="mt-2 font-display text-3xl text-ink-950">
            Score {r.overall_score}/{r.overall_max || 5}
            {evaluation.is_provisional ? " · provisional" : ""}
          </h2>
          <p className="mt-2 text-sm text-ink-500">
            Uncertainty {Math.round((r.uncertainty || 0) * 100)}% · model {evaluation.model_version}
          </p>
          <p className="mt-3 text-ink-600">{r.disclaimer}</p>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {Object.entries(r.dimensions || {}).map(([key, dim]) => (
            <div key={key} className="panel p-4">
              <p className="text-xs uppercase tracking-wide text-ink-500">{key}</p>
              <p className="mt-1 font-display text-2xl text-ink-950">
                {dim.score}/{dim.max}
              </p>
              <p className="mt-2 text-sm text-ink-600">{dim.feedback}</p>
            </div>
          ))}
        </div>

        <div className="panel space-y-3 p-6">
          <h3 className="font-medium text-ink-900">Gaps</h3>
          <ul className="list-disc space-y-1 pl-5 text-sm text-ink-600">
            {(r.gaps || []).map((g) => (
              <li key={g}>{g}</li>
            ))}
          </ul>
          {(r.errors || []).length > 0 && (
            <>
              <h3 className="pt-2 font-medium text-ink-900">Error memory</h3>
              <ul className="space-y-2">
                {r.errors!.map((err) => (
                  <li key={err.error_code} className="rounded-xl bg-evidence-soft px-3 py-2 text-sm text-evidence">
                    {err.description}
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={onSubmit} className="space-y-6">
      <div className="panel p-6">
        <p className="font-mono text-xs uppercase tracking-wider text-accent-strong">{item.type}</p>
        <h1 className="mt-3 font-display text-3xl text-ink-950">{item.prompt}</h1>
        <p className="mt-3 text-sm text-ink-500">
          {item.expected_minutes} min · Answer without looking up notes. Draft autosaves locally.
        </p>
      </div>
      <div>
        <label className="label" htmlFor="response">
          Your response
        </label>
        <textarea
          id="response"
          className="input min-h-64 font-sans"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          required
          placeholder="Write your explanation, design, or diagnosis…"
        />
      </div>
      {error && <p className="text-sm text-evidence">{error}</p>}
      <button className="btn-primary" disabled={loading || draft.trim().length < 1}>
        {loading ? "Evaluating…" : "Submit for feedback"}
      </button>
    </form>
  );
}
