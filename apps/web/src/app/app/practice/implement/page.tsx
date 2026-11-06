"use client";

import { FormEvent, Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { ApiError, PracticeItem, api } from "@/lib/api/client";

type ImplementResult = {
  attempt_id: string;
  evaluation_id: string;
  sandbox: {
    passed?: boolean;
    tests_passed?: number;
    tests_total?: number;
    results?: { i: number; ok: boolean; got?: string; expected?: string; error?: string }[];
    error?: string;
    message?: string;
  };
  result_json: { summary?: string; overall_score?: number };
};

function ImplementInner() {
  const params = useSearchParams();
  const itemId = params.get("item");
  const [item, setItem] = useState<PracticeItem & { metadata_json?: Record<string, unknown> } | null>(null);
  const [code, setCode] = useState("");
  const [result, setResult] = useState<ImplementResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!itemId) return;
    api<PracticeItem & { metadata_json?: Record<string, unknown> }>(`/practice-items/${itemId}`)
      .then((row) => {
        setItem(row);
        const starter = String(row.metadata_json?.starter_code || "");
        setCode(starter);
      })
      .catch(() => setError("Could not load implement task"));
  }, [itemId]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!itemId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api<ImplementResult>(`/practice-items/${itemId}/implement`, {
        method: "POST",
        json: { code, confidence: 0.7, idempotency_key: crypto.randomUUID() },
      });
      setResult(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Sandbox run failed");
    } finally {
      setLoading(false);
    }
  }

  if (!itemId) {
    return (
      <div className="panel p-8">
        <p className="text-ink-600">Pick an implement task from Practice.</p>
        <Link href="/app/practice" className="btn-secondary mt-4 inline-flex">
          Back to practice
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <p className="font-mono text-xs uppercase tracking-wider text-accent-strong">Implement · sandbox</p>
        <h1 className="mt-2 font-display text-3xl font-semibold text-ink-950">{item?.prompt || "Loading…"}</h1>
        <p className="mt-2 text-sm text-ink-600">
          Restricted Python sandbox (no network/filesystem). AST-blocked dangerous imports. Not a production isolator.
        </p>
      </div>

      <form onSubmit={onSubmit} className="space-y-4">
        <textarea
          className="input min-h-[320px] font-mono text-sm"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          spellCheck={false}
          required
        />
        <button className="btn-primary" disabled={loading}>
          {loading ? "Running…" : "Run tests"}
        </button>
      </form>

      {error && <p className="text-sm text-red-700">{error}</p>}

      {result && (
        <section className="panel space-y-3 p-6">
          <h2 className="font-display text-2xl text-ink-950">
            {result.sandbox.passed ? "Passed" : "Failed"} · {result.sandbox.tests_passed ?? 0}/
            {result.sandbox.tests_total ?? 0} tests
          </h2>
          <p className="text-sm text-ink-600">{result.result_json.summary}</p>
          <ul className="space-y-2 text-sm">
            {(result.sandbox.results || []).map((r) => (
              <li key={r.i} className={r.ok ? "text-accent-strong" : "text-red-700"}>
                #{r.i} {r.ok ? "ok" : "fail"}
                {r.error ? ` — ${r.error}` : r.got != null ? ` — got ${r.got}, expected ${r.expected}` : ""}
              </li>
            ))}
          </ul>
          <Link href="/app/today" className="btn-secondary inline-flex">
            Back to Today
          </Link>
        </section>
      )}
    </div>
  );
}

export default function ImplementPage() {
  return (
    <Suspense fallback={<div className="panel p-8 text-ink-500">Loading…</div>}>
      <ImplementInner />
    </Suspense>
  );
}
