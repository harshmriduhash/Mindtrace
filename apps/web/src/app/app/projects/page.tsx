"use client";

import { FormEvent, useEffect, useState } from "react";
import { ApiError, api } from "@/lib/api/client";

type Project = {
  id: string;
  repo_full_name: string;
  repo_url: string;
  summary: string;
  languages: Record<string, number>;
};

export default function ProjectsPage() {
  const [rows, setRows] = useState<Project[]>([]);
  const [url, setUrl] = useState("");
  const [summary, setSummary] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    setRows(await api<Project[]>("/projects"));
  }

  useEffect(() => {
    refresh().catch(() => setError("Could not load projects"));
  }, []);

  async function onLink(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await api("/projects", { method: "POST", json: { repo_url: url, summary } });
      setUrl("");
      setSummary("");
      setMessage("Repository linked as project evidence.");
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Link failed");
    }
  }

  async function unlink(id: string) {
    await api(`/projects/${id}`, { method: "DELETE" });
    await refresh();
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-display text-4xl font-semibold text-ink-950">Project evidence</h1>
        <p className="mt-2 text-ink-600">Link public GitHub repositories you approve as skill evidence.</p>
      </div>

      <form onSubmit={onLink} className="panel space-y-3 p-6">
        <input
          className="input"
          placeholder="https://github.com/owner/repo"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          required
        />
        <textarea
          className="input min-h-24"
          placeholder="What does this repo demonstrate?"
          value={summary}
          onChange={(e) => setSummary(e.target.value)}
        />
        <button className="btn-primary">Link repository</button>
      </form>

      {message && <p className="text-sm text-accent-strong">{message}</p>}
      {error && <p className="text-sm text-red-700">{error}</p>}

      <section className="space-y-3">
        {rows.map((r) => (
          <div key={r.id} className="panel flex flex-wrap items-start justify-between gap-3 p-5">
            <div>
              <a href={r.repo_url} className="font-display text-xl text-ink-950 underline-offset-2 hover:underline" target="_blank" rel="noreferrer">
                {r.repo_full_name}
              </a>
              <p className="mt-2 text-sm text-ink-600">{r.summary || "No summary"}</p>
              <p className="mt-2 font-mono text-xs text-ink-500">
                {Object.keys(r.languages || {}).slice(0, 6).join(" · ") || "languages n/a"}
              </p>
            </div>
            <button className="btn-secondary" onClick={() => unlink(r.id)}>
              Remove
            </button>
          </div>
        ))}
      </section>
    </div>
  );
}
