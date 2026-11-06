"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api/client";

type Progress = {
  attempts_count: number;
  evaluations_count: number;
  concepts_approved: number;
  error_patterns: number;
  skills: { status: string; competency: { title: string } | null; evidence_count: number }[];
  recent_attempts: {
    id: string;
    status: string;
    submitted_at: string | null;
    overall_score: number | null;
    is_provisional: boolean | null;
  }[];
};

export default function ProgressPage() {
  const [data, setData] = useState<Progress | null>(null);

  useEffect(() => {
    api<Progress>("/progress").then(setData);
  }, []);

  if (!data) return <div className="panel p-8 text-ink-500">Loading progress…</div>;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-display text-4xl font-semibold text-ink-950">Progress</h1>
        <p className="mt-2 text-ink-600">Evidence over activity. No opaque mastery percentage.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Stat label="Attempts" value={data.attempts_count} />
        <Stat label="Evaluations" value={data.evaluations_count} />
        <Stat label="Concepts approved" value={data.concepts_approved} />
        <Stat label="Error patterns" value={data.error_patterns} />
      </div>

      <section className="panel p-6">
        <h2 className="font-display text-2xl text-ink-950">Skill evidence</h2>
        <ul className="mt-4 space-y-3">
          {data.skills.map((s, idx) => (
            <li key={idx} className="flex items-center justify-between gap-3 border-b border-ink-100 pb-3 last:border-0">
              <span className="text-ink-800">{s.competency?.title}</span>
              <span className="text-sm text-ink-500">
                {s.status} · {s.evidence_count} evidence
              </span>
            </li>
          ))}
        </ul>
      </section>

      <section className="panel p-6">
        <h2 className="font-display text-2xl text-ink-950">Timeline</h2>
        <ul className="mt-4 space-y-3">
          {data.recent_attempts.length === 0 && <li className="text-sm text-ink-500">No attempts yet.</li>}
          {data.recent_attempts.map((a) => (
            <li key={a.id} className="flex flex-wrap items-center justify-between gap-2 text-sm">
              <span className="text-ink-800">{a.submitted_at || "In progress"}</span>
              <span className="text-ink-500">
                {a.status}
                {a.overall_score != null ? ` · score ${a.overall_score}` : ""}
                {a.is_provisional ? " · provisional" : ""}
              </span>
            </li>
          ))}
        </ul>
      </section>
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
