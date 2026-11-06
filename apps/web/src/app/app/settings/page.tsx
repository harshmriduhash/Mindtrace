"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api/client";

export default function SettingsPage() {
  const router = useRouter();
  const [exportJson, setExportJson] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

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

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-display text-4xl font-semibold text-ink-950">Settings</h1>
        <p className="mt-2 text-ink-600">Privacy controls, export, and deletion.</p>
      </div>

      <section className="panel space-y-4 p-6">
        <h2 className="font-display text-2xl text-ink-950">Your data</h2>
        <p className="text-sm text-ink-600">
          Export includes concepts, memories, skills, attempts, and source metadata. Practice response bodies are omitted
          from this MVP export payload for safety; expand carefully later.
        </p>
        <div className="flex flex-wrap gap-3">
          <button className="btn-primary" onClick={exportData}>
            Export my data
          </button>
          <button className="btn-secondary" onClick={deleteAccount}>
            Request deletion
          </button>
        </div>
        {message && <p className="text-sm text-accent-strong">{message}</p>}
        {exportJson && (
          <pre className="max-h-96 overflow-auto rounded-xl bg-ink-950 p-4 text-xs text-ink-100">{exportJson}</pre>
        )}
      </section>
    </div>
  );
}
