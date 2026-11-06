"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api/client";

type Usage = {
  plan: string;
  period_start: string;
  period_end: string;
  features: Record<string, { used: number; limit: number | null; reset: string }>;
};

export default function UsagePage() {
  const [data, setData] = useState<Usage | null>(null);

  useEffect(() => {
    api<Usage>("/usage").then(setData);
  }, []);

  if (!data) return <div className="panel p-8 text-ink-500">Loading usage…</div>;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-display text-4xl font-semibold text-ink-950">Usage</h1>
        <p className="mt-2 text-ink-600">
          Transparent quotas for the free beta. Payments are not required in this build (Stripe not enabled for India).
        </p>
      </div>

      <div className="panel p-6">
        <p className="text-sm text-ink-500">Current plan</p>
        <p className="mt-1 font-display text-3xl capitalize text-ink-950">{data.plan}</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {Object.entries(data.features).map(([key, feature]) => (
          <div key={key} className="panel p-5">
            <p className="text-xs uppercase tracking-wide text-ink-500">{key.replaceAll("_", " ")}</p>
            <p className="mt-2 font-display text-3xl text-ink-950">
              {feature.used}
              <span className="text-lg text-ink-400"> / {feature.limit ?? "∞"}</span>
            </p>
            <p className="mt-2 text-sm text-ink-500">Resets {feature.reset}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
