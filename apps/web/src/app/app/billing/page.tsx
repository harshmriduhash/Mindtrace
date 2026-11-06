"use client";

import { useEffect, useState } from "react";
import { ApiError, api } from "@/lib/api/client";

type Plans = {
  currency: string;
  provider: string;
  note: string;
  plans: { id: string; name: string; price_inr: number; features: string[] }[];
};

export default function BillingPage() {
  const [plans, setPlans] = useState<Plans | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    api<Plans>("/billing/plans").then(setPlans);
  }, []);

  async function checkout(planId: string) {
    setMessage(null);
    try {
      const result = await api<{ order_id: string; amount_paise: number }>("/billing/checkout", {
        method: "POST",
        json: { plan_id: planId },
      });
      setMessage(`Razorpay order ready: ${result.order_id} (${result.amount_paise / 100} INR). Complete checkout when keys are live.`);
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Checkout unavailable");
    }
  }

  if (!plans) return <div className="panel p-8 text-ink-500">Loading plans…</div>;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-display text-4xl font-semibold text-ink-950">Billing</h1>
        <p className="mt-2 text-ink-600">{plans.note}</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {plans.plans.map((p) => (
          <div key={p.id} className="panel p-6">
            <h2 className="font-display text-2xl text-ink-950">{p.name}</h2>
            <p className="mt-2 text-ink-600">
              ₹{p.price_inr}
              {p.price_inr > 0 ? "/mo" : ""}
            </p>
            <ul className="mt-4 space-y-1 text-sm text-ink-600">
              {p.features.map((f) => (
                <li key={f}>{f}</li>
              ))}
            </ul>
            {p.id !== "free" && (
              <button className="btn-primary mt-6" onClick={() => checkout(p.id)}>
                Upgrade with Razorpay
              </button>
            )}
          </div>
        ))}
      </div>
      {message && <p className="text-sm text-accent-strong">{message}</p>}
    </div>
  );
}
