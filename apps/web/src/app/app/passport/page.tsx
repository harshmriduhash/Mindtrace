"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api/client";

type Passport = {
  generated_at: string;
  learner: { display_name: string | null; role_target: string | null; plan: string };
  goal: { title: string; weekly_time_budget_minutes: number } | null;
  skill_path: { slug: string; title: string; version: string } | null;
  summary: {
    competency_counts: Record<string, number>;
    disputed_count: number;
    attempts_total: number;
    demonstrated_count: number;
  };
  competencies: {
    slug: string;
    title: string;
    definition: string;
    status: string;
    evidence_count: number;
    disputed: boolean;
    recent_evidence: { overall_score: number | null; submitted_at: string | null; is_provisional: boolean }[];
  }[];
  disclaimer: string;
};

export default function PassportPage() {
  const [data, setData] = useState<Passport | null>(null);

  useEffect(() => {
    api<Passport>("/passport").then(setData);
  }, []);

  function downloadJson() {
    if (!data) return;
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `mindtrace-passport-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  if (!data) return <div className="panel p-8 text-ink-500">Building your Skill Passport…</div>;

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="font-mono text-xs uppercase tracking-[0.18em] text-accent-strong">Skill Passport</p>
          <h1 className="mt-2 font-display text-4xl font-semibold text-ink-950">
            {data.learner.display_name || "Learner"}
          </h1>
          <p className="mt-2 text-ink-600">{data.learner.role_target || "No role target set"}</p>
          <p className="mt-1 text-sm text-ink-500">
            {data.skill_path?.title || "No path"} · generated {new Date(data.generated_at).toLocaleString()}
          </p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary" onClick={() => window.print()}>
            Print
          </button>
          <button className="btn-primary" onClick={downloadJson}>
            Export JSON
          </button>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Stat label="Demonstrated evidence" value={data.summary.demonstrated_count} />
        <Stat label="Developing" value={data.summary.competency_counts.developing || 0} />
        <Stat label="Attempts" value={data.summary.attempts_total} />
        <Stat label="Disputed" value={data.summary.disputed_count} />
      </div>

      {data.goal && (
        <div className="panel p-5 text-sm text-ink-700">
          Goal: <span className="font-medium text-ink-900">{data.goal.title}</span> ·{" "}
          {data.goal.weekly_time_budget_minutes} min / week
        </div>
      )}

      <section className="space-y-3">
        {data.competencies.map((c) => (
          <article key={c.slug} className="panel p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h2 className="font-display text-xl text-ink-950">{c.title}</h2>
                <p className="mt-1 text-sm text-ink-600">{c.definition}</p>
              </div>
              <span className="rounded-lg bg-accent-soft px-2.5 py-1 text-xs font-medium text-accent-strong">
                {c.status}
                {c.disputed ? " · disputed" : ""}
              </span>
            </div>
            <p className="mt-3 text-xs text-ink-500">Evidence count: {c.evidence_count}</p>
            {c.recent_evidence.length > 0 && (
              <ul className="mt-2 space-y-1 text-xs text-ink-500">
                {c.recent_evidence.map((e, i) => (
                  <li key={i}>
                    {e.submitted_at || "—"} · score {e.overall_score ?? "—"}
                    {e.is_provisional ? " · provisional" : ""}
                  </li>
                ))}
              </ul>
            )}
          </article>
        ))}
      </section>

      <p className="rounded-xl border border-ink-100 bg-white/70 p-4 text-sm text-ink-600">{data.disclaimer}</p>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="panel p-5">
      <p className="text-xs uppercase tracking-wide text-ink-500">{label}</p>
      <p className="mt-2 font-display text-3xl text-ink-950">{value}</p>
    </div>
  );
}
