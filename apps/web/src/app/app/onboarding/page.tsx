"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ApiError, api } from "@/lib/api/client";

type SkillPath = { id: string; slug: string; title: string; description: string };

export default function OnboardingPage() {
  const router = useRouter();
  const [paths, setPaths] = useState<SkillPath[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api<SkillPath[]>("/skill-paths")
      .then(setPaths)
      .catch(() => setError("Could not load skill paths. Is the API running?"));
  }, []);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    const form = new FormData(e.currentTarget);
    try {
      await api("/onboarding/complete", {
        method: "POST",
        json: {
          display_name: form.get("display_name"),
          role_target: form.get("role_target"),
          skill_path_slug: form.get("skill_path_slug"),
          weekly_time_budget_minutes: Number(form.get("weekly_time_budget_minutes")),
          goal_title: form.get("goal_title"),
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC",
        },
      });
      router.push("/app/today");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Onboarding failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-accent-strong">Onboarding</p>
      <h1 className="mt-2 font-display text-4xl font-semibold text-ink-950">Set your skill goal</h1>
      <p className="mt-2 text-ink-600">One focused path. We&apos;ll establish baseline evidence next.</p>

      <form onSubmit={onSubmit} className="panel mt-8 space-y-5 p-6">
        <div>
          <label className="label" htmlFor="display_name">
            What should we call you?
          </label>
          <input className="input" id="display_name" name="display_name" required />
        </div>
        <div>
          <label className="label" htmlFor="role_target">
            Target role / outcome
          </label>
          <input
            className="input"
            id="role_target"
            name="role_target"
            placeholder="Senior backend engineer interviews"
            required
          />
        </div>
        <div>
          <label className="label" htmlFor="goal_title">
            Goal title
          </label>
          <input
            className="input"
            id="goal_title"
            name="goal_title"
            defaultValue="Demonstrate senior system design capability"
            required
          />
        </div>
        <div>
          <label className="label" htmlFor="skill_path_slug">
            Skill path
          </label>
          <select className="input" id="skill_path_slug" name="skill_path_slug" required defaultValue="system-design-senior">
            {paths.map((p) => (
              <option key={p.id} value={p.slug}>
                {p.title}
              </option>
            ))}
          </select>
          {paths[0] && <p className="mt-2 text-sm text-ink-500">{paths[0].description}</p>}
        </div>
        <div>
          <label className="label" htmlFor="weekly_time_budget_minutes">
            Weekly time budget (minutes)
          </label>
          <input
            className="input"
            id="weekly_time_budget_minutes"
            name="weekly_time_budget_minutes"
            type="number"
            min={30}
            max={1400}
            defaultValue={180}
            required
          />
        </div>
        {error && (
          <p className="rounded-xl bg-evidence-soft px-3 py-2 text-sm text-evidence" role="alert">
            {error}
          </p>
        )}
        <button className="btn-primary" disabled={loading}>
          {loading ? "Saving…" : "Continue to Today"}
        </button>
      </form>
    </div>
  );
}
