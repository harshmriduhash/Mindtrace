"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ApiError, api } from "@/lib/api/client";

export default function SettingsPage() {
  const router = useRouter();
  const [exportJson, setExportJson] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [feedback, setFeedback] = useState("");

  async function exportData() {
    const data = await api<Record<string, unknown>>("/exports", { method: "POST" });
    setExportJson(JSON.stringify(data, null, 2));
    setMessage("Export ready. Download or copy below.");
  }

  async function deleteAccount() {
    if (!confirm("Request account deletion? Active learning memory will be deactivated.")) return;
    await api("/account/deletion", { method: "POST" });
    setMessage("Deletion requested.");
    router.push("/");
  }

  async function sendFeedback(e: FormEvent) {
    e.preventDefault();
    try {
      await api("/feedback/authenticated", {
        method: "POST",
        json: { message: feedback, category: "beta" },
      });
      setFeedback("");
      setMessage("Feedback sent — thank you.");
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Could not send feedback");
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-display text-4xl font-semibold text-ink-950">Settings</h1>
        <p className="mt-2 text-ink-600">Privacy controls, export, deletion, and beta feedback.</p>
      </div>

      <section className="panel space-y-4 p-6">
        <h2 className="font-display text-2xl text-ink-950">Your data</h2>
        <div className="flex flex-wrap gap-3">
          <button className="btn-primary" onClick={exportData}>
            Export my data
          </button>
          <button className="btn-secondary" onClick={deleteAccount}>
            Request deletion
          </button>
          <Link href="/app/billing" className="btn-secondary">
            Billing
          </Link>
          <Link href="/terms" className="btn-secondary">
            Terms
          </Link>
        </div>
        {message && <p className="text-sm text-accent-strong">{message}</p>}
        {exportJson && (
          <pre className="max-h-96 overflow-auto rounded-xl bg-ink-950 p-4 text-xs text-ink-100">{exportJson}</pre>
        )}
      </section>

      <section className="panel space-y-4 p-6">
        <h2 className="font-display text-2xl text-ink-950">Beta feedback</h2>
        <form onSubmit={sendFeedback} className="space-y-3">
          <textarea
            className="input min-h-28"
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            required
            minLength={5}
            placeholder="What should we improve for private beta?"
          />
          <button className="btn-primary">Send feedback</button>
        </form>
      </section>
    </div>
  );
}
