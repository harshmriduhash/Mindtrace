"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { ApiError, api } from "@/lib/api/client";

type Source = { id: string; title: string; type: string; status: string; created_at: string };
type Concept = { id: string; title: string; definition: string; status: string; confidence: number | null };
type ConceptDetail = Concept & {
  provenance: {
    source_title: string | null;
    source_type: string | null;
    page_or_timestamp: string | null;
    excerpt: string;
  }[];
};
type Mode = "text" | "url" | "youtube" | "pdf";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

export default function LearnPage() {
  const [mode, setMode] = useState<Mode>("text");
  const [sources, setSources] = useState<Source[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [details, setDetails] = useState<Record<string, ConceptDetail>>({});
  const [editing, setEditing] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editDef, setEditDef] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [tutorOut, setTutorOut] = useState<string | null>(null);

  async function refresh() {
    const rows = await api<Source[]>("/sources");
    setSources(rows);
  }

  useEffect(() => {
    refresh().catch(() => setError("Could not load sources"));
  }, []);

  async function onImport(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);
    setTutorOut(null);
    const form = new FormData(e.currentTarget);
    try {
      let source: Source;
      if (mode === "pdf") {
        const body = new FormData();
        body.set("title", String(form.get("title") || "PDF upload"));
        body.set("idempotency_key", crypto.randomUUID());
        const file = form.get("file");
        if (!(file instanceof File) || file.size === 0) throw new Error("Choose a PDF file");
        body.set("file", file);
        const res = await fetch(`${API_BASE}/sources/upload`, {
          method: "POST",
          body,
          credentials: "include",
        });
        if (!res.ok) {
          const data = await res.json().catch(() => null);
          throw new ApiError(res.status, data?.error?.code || "upload_failed", data?.error?.message || "Upload failed");
        }
        source = await res.json();
      } else {
        source = await api<Source>("/sources", {
          method: "POST",
          json: {
            type: mode === "youtube" ? "youtube" : mode,
            title: form.get("title"),
            text: mode === "text" ? form.get("text") : undefined,
            url: mode === "url" || mode === "youtube" ? form.get("url") : undefined,
            idempotency_key: crypto.randomUUID(),
          },
        });
      }
      await refresh();
      setSelected(source.id);
      const extracted = await api<Concept[]>(`/sources/${source.id}/concepts`);
      setConcepts(extracted);
      setMessage("Concepts extracted — review and approve before they enter your learning graph.");
      e.currentTarget.reset();
    } catch (err) {
      setError(err instanceof ApiError || err instanceof Error ? err.message : "Import failed");
    } finally {
      setLoading(false);
    }
  }

  async function loadConcepts(id: string) {
    setSelected(id);
    const rows = await api<Concept[]>(`/sources/${id}/concepts`);
    setConcepts(rows);
    const detailEntries = await Promise.all(
      rows.map(async (c) => {
        const d = await api<ConceptDetail>(`/concepts/${c.id}`);
        return [c.id, d] as const;
      }),
    );
    setDetails(Object.fromEntries(detailEntries));
  }

  function startEdit(c: Concept) {
    setEditing(c.id);
    setEditTitle(c.title);
    setEditDef(c.definition);
  }

  async function saveEdit(conceptId: string) {
    const updated = await api<ConceptDetail>(`/concepts/${conceptId}`, {
      method: "PATCH",
      json: { title: editTitle, definition: editDef },
    });
    setDetails((prev) => ({ ...prev, [conceptId]: updated }));
    setConcepts((prev) =>
      prev.map((c) => (c.id === conceptId ? { ...c, title: updated.title, definition: updated.definition } : c)),
    );
    setEditing(null);
    setMessage("Concept updated before approval.");
  }

  async function approveAll() {
    if (!selected) return;
    const proposed = concepts.filter((c) => c.status === "proposed");
    await api(`/sources/${selected}/approve-concepts`, {
      method: "POST",
      json: { concept_ids: proposed.map((c) => c.id), reject_ids: [] },
    });
    await loadConcepts(selected);
    setMessage("Concepts approved and committed to your learning graph.");
  }

  async function askTutor(conceptId: string) {
    const result = await api<{ explanation: string }>("/tutor/explain", {
      method: "POST",
      json: { concept_id: conceptId },
    });
    setTutorOut(result.explanation);
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-display text-4xl font-semibold text-ink-950">Learn</h1>
        <p className="mt-2 text-ink-600">Import material (text, URL, YouTube captions, or PDF), approve concepts, keep provenance.</p>
      </div>

      <form onSubmit={onImport} className="panel space-y-4 p-6">
        <div className="flex flex-wrap gap-2">
          {(["text", "url", "youtube", "pdf"] as Mode[]).map((m) => (
            <button
              key={m}
              type="button"
              onClick={() => setMode(m)}
              className={`rounded-xl px-3 py-1.5 text-sm ${mode === m ? "bg-accent-soft text-accent-strong" : "bg-white text-ink-600"}`}
            >
              {m.toUpperCase()}
            </button>
          ))}
        </div>
        <div>
          <label className="label" htmlFor="title">
            Source title
          </label>
          <input className="input" id="title" name="title" required placeholder="Notes on cache invalidation" />
        </div>
        {mode === "text" && (
          <div>
            <label className="label" htmlFor="text">
              Paste text / excerpt
            </label>
            <textarea className="input min-h-40" id="text" name="text" required placeholder="Paste study notes or excerpts you have rights to use." />
          </div>
        )}
        {mode === "url" && (
          <div>
            <label className="label" htmlFor="url">
              Public article URL
            </label>
            <input className="input" id="url" name="url" type="url" required placeholder="https://example.com/article" />
            <p className="mt-1 text-xs text-ink-500">Private/internal hosts are blocked (SSRF protection). Paywalls are not bypassed.</p>
          </div>
        )}
        {mode === "youtube" && (
          <div>
            <label className="label" htmlFor="url">
              YouTube URL (public captions)
            </label>
            <input
              className="input"
              id="url"
              name="url"
              type="url"
              required
              placeholder="https://www.youtube.com/watch?v=…"
            />
            <p className="mt-1 text-xs text-ink-500">Only public caption tracks. No paywall or private video bypass.</p>
          </div>
        )}
        {mode === "pdf" && (
          <div>
            <label className="label" htmlFor="file">
              PDF upload (max 25MB / 200 pages)
            </label>
            <input className="input" id="file" name="file" type="file" accept="application/pdf,.pdf" required />
          </div>
        )}
        {error && <p className="text-sm text-evidence">{error}</p>}
        {message && <p className="text-sm text-accent-strong">{message}</p>}
        <button className="btn-primary" disabled={loading}>
          {loading ? "Extracting…" : "Import & extract concepts"}
        </button>
      </form>

      <div className="grid gap-6 lg:grid-cols-2">
        <section>
          <h2 className="font-display text-2xl text-ink-950">Sources</h2>
          <ul className="mt-3 space-y-2">
            {sources.map((s) => (
              <li key={s.id}>
                <button
                  onClick={() => loadConcepts(s.id)}
                  className={`panel w-full p-4 text-left transition hover:bg-white ${selected === s.id ? "ring-2 ring-accent/30" : ""}`}
                >
                  <p className="font-medium text-ink-900">{s.title}</p>
                  <p className="text-xs text-ink-500">
                    {s.type} · {s.status}
                  </p>
                </button>
              </li>
            ))}
          </ul>
        </section>

        <section>
          <div className="flex items-center justify-between gap-3">
            <h2 className="font-display text-2xl text-ink-950">Concepts</h2>
            {concepts.some((c) => c.status === "proposed") && (
              <button className="btn-secondary" onClick={approveAll}>
                Approve all
              </button>
            )}
          </div>
          <ul className="mt-3 space-y-3">
            {concepts.map((c) => {
              const detail = details[c.id];
              return (
                <li key={c.id} className="panel p-4">
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-medium text-ink-900">{c.title}</h3>
                    <span className="text-xs text-ink-500">{c.status}</span>
                  </div>
                  {editing === c.id ? (
                    <div className="mt-3 space-y-2">
                      <input className="input" value={editTitle} onChange={(e) => setEditTitle(e.target.value)} />
                      <textarea className="input min-h-24" value={editDef} onChange={(e) => setEditDef(e.target.value)} />
                      <div className="flex gap-2">
                        <button type="button" className="btn-primary" onClick={() => saveEdit(c.id)}>
                          Save edits
                        </button>
                        <button type="button" className="btn-secondary" onClick={() => setEditing(null)}>
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <p className="mt-2 text-sm text-ink-600">{c.definition}</p>
                      {detail?.provenance?.length ? (
                        <div className="mt-3 rounded-xl bg-ink-50 p-3 text-xs text-ink-600">
                          <p className="font-medium text-ink-800">Provenance</p>
                          {detail.provenance.map((p, idx) => (
                            <p key={idx} className="mt-1">
                              {p.source_title || "Source"} ({p.source_type}
                              {p.page_or_timestamp ? ` · p.${p.page_or_timestamp}` : ""}): “{p.excerpt}”
                            </p>
                          ))}
                        </div>
                      ) : null}
                      <div className="mt-3 flex flex-wrap gap-2">
                        {c.status === "proposed" && (
                          <button type="button" className="btn-secondary" onClick={() => startEdit(c)}>
                            Edit before approve
                          </button>
                        )}
                        {c.status === "approved" && (
                          <button type="button" className="btn-secondary" onClick={() => askTutor(c.id)}>
                            Explain with tutor
                          </button>
                        )}
                      </div>
                    </>
                  )}
                </li>
              );
            })}
          </ul>
          {tutorOut && (
            <div className="panel mt-4 whitespace-pre-wrap p-4 text-sm text-ink-700">{tutorOut}</div>
          )}
          <Link href="/app/practice" className="btn-primary mt-4 inline-flex">
            Practice what you learned
          </Link>
        </section>
      </div>
    </div>
  );
}
