"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api/client";

type UserSkill = {
  id: string;
  status: string;
  evidence_count: number;
  confidence: number | null;
  competency: { title: string; definition: string; slug: string } | null;
};

const STATUS_LABEL: Record<string, string> = {
  not_assessed: "Not assessed",
  emerging: "Emerging",
  developing: "Developing",
  demonstrated: "Demonstrated evidence",
  needs_review: "Needs review",
};

export default function SkillsPage() {
  const [skills, setSkills] = useState<UserSkill[]>([]);

  useEffect(() => {
    api<UserSkill[]>("/skills").then(setSkills).catch(() => setSkills([]));
  }, []);

  return (
    <div>
      <h1 className="font-display text-4xl font-semibold text-ink-950">My Skills</h1>
      <p className="mt-2 text-ink-600">Status reflects evidence, not a precise mastery percentage.</p>
      <div className="mt-8 space-y-3">
        {skills.length === 0 && <div className="panel p-6 text-ink-500">No skills yet. Complete onboarding first.</div>}
        {skills.map((s) => (
          <Link key={s.id} href={`/app/skills/${s.id}`} className="panel block p-5 transition hover:bg-white">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h2 className="font-display text-xl text-ink-950">{s.competency?.title}</h2>
                <p className="mt-1 max-w-2xl text-sm text-ink-600">{s.competency?.definition}</p>
              </div>
              <span className="rounded-lg bg-accent-soft px-2.5 py-1 text-xs font-medium text-accent-strong">
                {STATUS_LABEL[s.status] || s.status}
              </span>
            </div>
            <p className="mt-3 text-xs text-ink-500">
              Evidence count: {s.evidence_count}
              {s.confidence != null ? ` · Self-reported confidence: ${Math.round(s.confidence * 100)}%` : ""}
              {" · Open for prerequisites & dispute"}
            </p>
          </Link>
        ))}
      </div>
    </div>
  );
}
