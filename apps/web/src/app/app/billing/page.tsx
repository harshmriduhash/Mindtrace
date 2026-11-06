"use client";

import { useEffect, useState } from "react";
import { ApiError, api } from "@/lib/api/client";

type Plans = {
  currency: string;
  provider: string;
  note: string;
  configured?: boolean;
  plans: { id: string; name: string; price_inr: number; features: string[] }[];
};

type Checkout = {
  key_id: string;
  order_id: string;
  amount_paise: number;
  currency: string;
  plan_id: string;
};

declare global {
  interface Window {
    Razorpay?: new (options: Record<string, unknown>) => { open: () => void };
  }
}

function loadRazorpay(): Promise<boolean> {
  return new Promise((resolve) => {
    if (window.Razorpay) {
      resolve(true);
      return;
    }
    const script = document.createElement("script");
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.onload = () => resolve(true);
    script.onerror = () => resolve(false);
    document.body.appendChild(script);
  });
}

export default function BillingPage() {
  const [plans, setPlans] = useState<Plans | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    api<Plans>("/billing/plans").then(setPlans);
  }, []);

  async function checkout(planId: string) {
    setMessage(null);
    try {
      const result = await api<Checkout>("/billing/checkout", {
        method: "POST",
        json: { plan_id: planId },
      });
      const ok = await loadRazorpay();
      if (!ok || !window.Razorpay) {
        setMessage(`Order created (${result.order_id}). Razorpay.js failed to load — complete payment when the script is available.`);
        return;
      }
      const rzp = new window.Razorpay({
        key: result.key_id,
        amount: result.amount_paise,
        currency: result.currency,
        order_id: result.order_id,
        name: "Mindtrace",
        description: `${result.plan_id} plan`,
        handler: () => {
          setMessage("Payment submitted. Entitlements update after Razorpay webhook confirmation.");
        },
      });
      rzp.open();
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
      <div className="grid gap-4 md:grid-cols-3">
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
