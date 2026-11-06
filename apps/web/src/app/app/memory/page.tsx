"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api/client";

type Memory = {
  id: string;
  memory_type: string;
  content_json: Record<string, unknown>;
  confidence: number | null;
  status: string;
  created_at: string;
};

type ErrorRow = {
  id: string;
  error_code: string;
  description: string;
  severity: string;
  recurrence_count: number;
};

export default function MemoryPage() {
  const [memories, setMemories] = useState<Memory[]>([]);
  const [errors, setErrors] = useState<ErrorRow[]>([]);

  useEffect(() => {
    Promise.all([api<Memory[]>("/memory"), api<ErrorRow[]>("/memory/errors")]).then(([m, e]) => {
      setMemories(m);
      setErrors(e);
    });
  }, []);

  async function deleteMemory(id: string) {
    await api(`/memory/${id}`, { method: "DELETE" });
    setMemories((prev) => prev.filter((m) => m.id !== id));
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-display text-4xl font-semibold text-ink-950">Memory</h1>
        <p className="mt-2 text-ink-600">Inspect, correct, or delete stored learning memory. Derived memory is not unquestionable fact.</p>
      </div>

      <section>
        <h2 className="font-display text-2xl text-ink-950">Recurring errors</h2>
        <ul className="mt-3 space-y-2">
          {errors.length === 0 && <li className="text-sm text-ink-500">No error patterns yet.</li>}
          {errors.map((e) => (
            <li key={e.id} className="panel p-4">
              <p className="font-medium text-ink-900">{e.description}</p>
              <p className="mt-1 text-xs text-ink-500">
                {e.error_code} · {e.severity} · seen {e.recurrence_count}×
              </p>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="font-display text-2xl text-ink-950">Learner memory</h2>
        <ul className="mt-3 space-y-2">
          {memories.map((m) => (
            <li key={m.id} className="panel flex items-start justify-between gap-4 p-4">
              <div>
                <p className="font-mono text-xs uppercase tracking-wide text-accent-strong">{m.memory_type}</p>
                <pre className="mt-2 overflow-x-auto whitespace-pre-wrap font-sans text-sm text-ink-700">
                  {JSON.stringify(m.content_json, null, 2)}
                </pre>
              </div>
              <button className="btn-secondary shrink-0" onClick={() => deleteMemory(m.id)}>
                Delete
              </button>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
