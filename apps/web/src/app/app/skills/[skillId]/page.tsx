"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { ApiError, api } from "@/lib/api/client";

type Detail = {
  skill: {
    id: string;
    status: string;
    evidence_count: number;
    competency: { title: string; definition: string; slug: string } | null;
  };
  prerequisites: { title: string; slug: string }[];
  dependents: { title: string; slug: string }[];
  evidence: {
    attempt_id: string;
    submitted_at: string | null;
    prompt: string | null;
    overall_score: number | null;
    is_provisional: boolean | null;
    challenge_status: string | null;
  }[];
  disputed: boolean;
  dispute_note: string | null;
};

export default function SkillDetailPage() {
  const params = useParams();
  const skillId = String(params.skillId);
  const [data, setData] = useState<Detail | null>(null);
  const [reason, setReason] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api<Detail>(`/skills/${skillId}`).then(setData).catch(() => setError("Could not load skill"));
  }, [skillId]);

  async function dispute(e: FormEvent) {
    e.preventDefault();
    try {
      const next = await api<Detail>(`/skills/${skillId}/dispute`, {
        method: "POST",
        json: { reason },
      });
      setData(next);
      setReason("");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Dispute failed");
    }
  }

  if (error && !data) return <div className="panel p-6 text-evidence">{error}</div>;
  if (!data) return <div className="panel p-8 text-ink-500">Loading skill…</div>;

  return (
    <div className="space-y-8">
      <Link href="/app/skills" className="text-sm text-accent-strong">
        ← My Skills
      </Link>
      <div>
        <h1 className="font-display text-4xl font-semibold text-ink-950">{data.skill.competency?.title}</h1>
        <p className="mt-2 text-ink-600">{data.skill.competency?.definition}</p>
        <p className="mt-3 text-sm text-ink-500">
          Status: {data.skill.status} · Evidence: {data.skill.evidence_count}
          {data.disputed ? " · Disputed" : ""}
        </p>
      </div>

      <section className="grid gap-4 md:grid-cols-2">
        <div className="panel p-5">
          <h2 className="font-display text-xl text-ink-950">Prerequisites</h2>
          <ul className="mt-3 space-y-2 text-sm text-ink-700">
            {data.prerequisites.length === 0 && <li>None</li>}
            {data.prerequisites.map((p) => (
              <li key={p.slug}>{p.title}</li>
            ))}
          </ul>
        </div>
        <div className="panel p-5">
          <h2 className="font-display text-xl text-ink-950">Builds toward</h2>
          <ul className="mt-3 space-y-2 text-sm text-ink-700">
            {data.dependents.length === 0 && <li>None</li>}
            {data.dependents.map((p) => (
              <li key={p.slug}>{p.title}</li>
            ))}
          </ul>
        </div>
      </section>

      <section className="panel p-6">
        <h2 className="font-display text-2xl text-ink-950">Evidence</h2>
        <ul className="mt-4 space-y-3">
          {data.evidence.length === 0 && <li className="text-sm text-ink-500">No attempts yet.</li>}
          {data.evidence.map((e) => (
            <li key={e.attempt_id} className="border-b border-ink-100 pb-3 text-sm last:border-0">
              <p className="text-ink-800">{e.prompt}</p>
              <p className="mt-1 text-ink-500">
                {e.submitted_at || "—"} · score {e.overall_score ?? "—"}
                {e.is_provisional ? " · provisional" : ""}
                {e.challenge_status && e.challenge_status !== "none" ? ` · ${e.challenge_status}` : ""}
              </p>
            </li>
          ))}
        </ul>
      </section>

      <section className="panel p-6">
        <h2 className="font-display text-2xl text-ink-950">Dispute status</h2>
        <p className="mt-2 text-sm text-ink-600">
          If you believe the competency status is wrong, dispute it with evidence. Disputed “demonstrated” statuses move
          to needs review.
        </p>
        {data.dispute_note && <p className="mt-3 rounded-xl bg-evidence-soft p-3 text-sm text-evidence">{data.dispute_note}</p>}
        <form onSubmit={dispute} className="mt-4 space-y-3">
          <textarea className="input min-h-24" value={reason} onChange={(e) => setReason(e.target.value)} required minLength={10} placeholder="Why is this status incorrect?" />
          <button className="btn-secondary">Submit dispute</button>
        </form>
      </section>
    </div>
  );
}
