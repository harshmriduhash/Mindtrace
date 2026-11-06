"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Me, Recommendation, api } from "@/lib/api/client";

export default function TodayPage() {
  const [me, setMe] = useState<Me | null>(null);
  const [rec, setRec] = useState<Recommendation | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api<Me>("/me"), api<Recommendation>("/recommendations/next")])
      .then(([m, r]) => {
        setMe(m);
        setRec(r);
      })
      .catch(() => setError("Could not load your dashboard. Please log in again."));
  }, []);

  if (error) {
    return (
      <div className="panel p-6">
        <p className="text-evidence">{error}</p>
        <Link href="/login" className="btn-secondary mt-4 inline-flex">
          Log in
        </Link>
      </div>
    );
  }

  if (!me || !rec) {
    return <div className="panel animate-pulse-soft p-8 text-ink-500">Loading your next action…</div>;
  }

  return (
    <div className="space-y-8">
      <div>
        <p className="text-ink-500">
          Good {greeting()}, {me.profile?.display_name || "learner"}
        </p>
        <h1 className="mt-1 font-display text-4xl font-semibold text-ink-950">Your next best action</h1>
      </div>

      <section className="panel p-6 md:p-8">
        <p className="font-mono text-xs uppercase tracking-[0.18em] text-accent-strong">{rec.action_type}</p>
        <h2 className="mt-3 max-w-2xl font-display text-2xl text-ink-950 md:text-3xl">{rec.title}</h2>
        <p className="mt-3 max-w-2xl text-ink-600">
          <span className="font-medium text-ink-800">Why: </span>
          {rec.reason}
        </p>
        <p className="mt-2 text-sm text-ink-500">{rec.estimated_minutes} min · evidence-linked recommendation</p>
        <Link href={rec.href} className="btn-primary mt-6 inline-flex">
          Start practice
        </Link>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <QuickLink href="/app/practice/baseline" title="Baseline" body="Establish starting evidence" />
        <QuickLink href="/app/learn" title="Import a source" body="Paste notes or article text" />
        <QuickLink href="/app/progress" title="Progress" body="Inspect evidence over time" />
      </section>

      <p className="text-sm text-ink-500">
        Current goal: <span className="text-ink-800">{me.profile?.role_target || "Set during onboarding"}</span>
      </p>
    </div>
  );
}

function QuickLink({ href, title, body }: { href: string; title: string; body: string }) {
  return (
    <Link href={href} className="panel block p-5 transition hover:bg-white">
      <h3 className="font-medium text-ink-900">{title}</h3>
      <p className="mt-1 text-sm text-ink-500">{body}</p>
    </Link>
  );
}

function greeting() {
  const h = new Date().getHours();
  if (h < 12) return "morning";
  if (h < 18) return "afternoon";
  return "evening";
}
