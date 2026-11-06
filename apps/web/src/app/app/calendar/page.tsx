"use client";

import { useEffect, useState } from "react";
import { ApiError, api } from "@/lib/api/client";

type Connection = {
  feed_token: string;
  ics_url: string;
  google_url: string;
  provider: string;
  status: string;
};

type Upcoming = {
  due_at: string;
  title: string;
  remediation_mode: string;
  type: string | null;
};

export default function CalendarPage() {
  const [conn, setConn] = useState<Connection | null>(null);
  const [upcoming, setUpcoming] = useState<Upcoming[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      const [c, u] = await Promise.all([
        api<Connection>("/calendar/connection"),
        api<Upcoming[]>("/calendar/upcoming"),
      ]);
      setConn(c);
      setUpcoming(u);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load calendar");
    }
  }

  useEffect(() => {
    load().catch(() => undefined);
  }, []);

  async function rotate() {
    setConn(await api<Connection>("/calendar/connection/rotate", { method: "POST" }));
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-display text-4xl font-semibold text-ink-950">Calendar</h1>
        <p className="mt-2 text-ink-600">Subscribe to due reviews via ICS, or open in Google Calendar.</p>
      </div>

      {error && <p className="text-sm text-red-700">{error}</p>}

      {conn && (
        <section className="panel space-y-4 p-6">
          <p className="text-sm text-ink-600">ICS feed URL</p>
          <pre className="overflow-x-auto rounded-xl bg-ink-950 p-4 text-xs text-ink-100">{conn.ics_url}</pre>
          <div className="flex flex-wrap gap-3">
            <a className="btn-primary" href={conn.google_url} target="_blank" rel="noreferrer">
              Open Google Calendar
            </a>
            <button className="btn-secondary" onClick={rotate}>
              Rotate feed token
            </button>
          </div>
        </section>
      )}

      <section className="space-y-3">
        <h2 className="font-display text-2xl text-ink-950">Upcoming</h2>
        {upcoming.length === 0 && <p className="text-sm text-ink-500">No upcoming reviews.</p>}
        {upcoming.map((u, i) => (
          <div key={`${u.due_at}-${i}`} className="panel p-4">
            <p className="font-mono text-xs text-accent-strong">
              {new Date(u.due_at).toLocaleString()} · {u.type} · {u.remediation_mode}
            </p>
            <p className="mt-2 text-ink-900">{u.title}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
