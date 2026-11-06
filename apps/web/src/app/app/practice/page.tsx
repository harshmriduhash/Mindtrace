"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { PracticeItem, api } from "@/lib/api/client";

export default function PracticeIndexPage() {
  const [items, setItems] = useState<PracticeItem[]>([]);
  const [due, setDue] = useState<PracticeItem[]>([]);

  useEffect(() => {
    Promise.all([
      api<PracticeItem[]>("/practice-items"),
      api<PracticeItem[]>("/reviews/due"),
    ]).then(([all, d]) => {
      setItems(all);
      setDue(d);
    });
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-display text-4xl font-semibold text-ink-950">Practice</h1>
        <p className="mt-2 text-ink-600">Retrieve before revealing. Apply before claiming progress.</p>
      </div>

      <div className="flex flex-wrap gap-3">
        <Link href="/app/practice/baseline" className="btn-primary">
          Start baseline
        </Link>
        <Link href="/app/practice/voice" className="btn-secondary">
          Voice practice
        </Link>
        <Link href="/app/practice/review" className="btn-secondary">
          Due reviews ({due.length})
        </Link>
      </div>

      <section className="space-y-3">
        {items.map((item) => (
          <Link
            key={item.id}
            href={`/app/practice/assessment?item=${item.id}`}
            className="panel block p-5 transition hover:bg-white"
          >
            <p className="font-mono text-xs uppercase tracking-wider text-accent-strong">{item.type}</p>
            <h2 className="mt-2 font-display text-xl text-ink-950">{item.prompt}</h2>
            <p className="mt-2 text-sm text-ink-500">
              {item.expected_minutes} min · {item.difficulty}
            </p>
          </Link>
        ))}
      </section>
    </div>
  );
}
