"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ApiError, api } from "@/lib/api/client";

export default function SettingsPage() {
  const router = useRouter();
  const [exportJson, setExportJson] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [feedback, setFeedback] = useState("");
  const [extToken, setExtToken] = useState<string | null>(null);
  const [mfaEnabled, setMfaEnabled] = useState(false);
  const [mfaSetup, setMfaSetup] = useState<{ otpauth_url: string; recovery_codes: string[]; secret: string } | null>(
    null,
  );
  const [mfaCode, setMfaCode] = useState("");

  useEffect(() => {
    api<{ enabled: boolean }>("/auth/mfa/status")
      .then((s) => setMfaEnabled(s.enabled))
      .catch(() => undefined);
  }, []);

  async function exportData() {
    const data = await api<Record<string, unknown>>("/exports", { method: "POST" });
    setExportJson(JSON.stringify(data, null, 2));
    setMessage("Export ready. Download or copy below.");
  }

  async function deleteAccount() {
    if (!confirm("Permanently delete your account and all learning data?")) return;
    await api("/account/deletion?hard=true", { method: "POST" });
    setMessage("Account purged.");
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

  async function createExtensionToken() {
    try {
      const data = await api<{ token: string; api_base_hint: string; expires_in_days: number }>(
        "/auth/extension-token",
        { method: "POST" },
      );
      setExtToken(data.token);
      setMessage(`Extension token created (expires in ${data.expires_in_days} days). API: ${data.api_base_hint}`);
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Could not create token");
    }
  }

  async function setupMfa() {
    try {
      const data = await api<{ otpauth_url: string; recovery_codes: string[]; secret: string }>("/auth/mfa/setup", {
        method: "POST",
      });
      setMfaSetup(data);
      setMessage("Scan the otpauth URL in your authenticator, then confirm with a code.");
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "MFA setup failed");
    }
  }

  async function confirmMfa(e: FormEvent) {
    e.preventDefault();
    try {
      await api("/auth/mfa/confirm", { method: "POST", json: { code: mfaCode } });
      setMfaEnabled(true);
      setMfaSetup(null);
      setMfaCode("");
      setMessage("MFA enabled.");
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Invalid code");
    }
  }

  async function disableMfa(e: FormEvent) {
    e.preventDefault();
    try {
      await api("/auth/mfa/disable", { method: "POST", json: { code: mfaCode } });
      setMfaEnabled(false);
      setMfaCode("");
      setMessage("MFA disabled.");
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Could not disable MFA");
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-display text-4xl font-semibold text-ink-950">Settings</h1>
        <p className="mt-2 text-ink-600">Privacy, MFA, export, deletion, and beta feedback.</p>
      </div>

      <section className="panel space-y-4 p-6">
        <h2 className="font-display text-2xl text-ink-950">Your data</h2>
        <div className="flex flex-wrap gap-3">
          <button className="btn-primary" onClick={exportData}>
            Export my data
          </button>
          <button className="btn-secondary" onClick={deleteAccount}>
            Delete account (hard purge)
          </button>
          <Link href="/app/billing" className="btn-secondary">
            Billing
          </Link>
          <Link href="/app/projects" className="btn-secondary">
            Projects
          </Link>
          <Link href="/app/calendar" className="btn-secondary">
            Calendar
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
        <h2 className="font-display text-2xl text-ink-950">Two-factor authentication</h2>
        <p className="text-sm text-ink-600">Status: {mfaEnabled ? "enabled" : "disabled"}</p>
        {!mfaEnabled && !mfaSetup && (
          <button className="btn-secondary" onClick={setupMfa}>
            Enable MFA
          </button>
        )}
        {mfaSetup && (
          <div className="space-y-3">
            <p className="break-all font-mono text-xs text-ink-700">{mfaSetup.otpauth_url}</p>
            <p className="text-sm text-ink-600">Save recovery codes:</p>
            <pre className="rounded-xl bg-ink-950 p-4 text-xs text-ink-100">{mfaSetup.recovery_codes.join("\n")}</pre>
            <form onSubmit={confirmMfa} className="flex flex-wrap gap-3">
              <input
                className="input max-w-xs"
                value={mfaCode}
                onChange={(e) => setMfaCode(e.target.value)}
                placeholder="Authenticator code"
                required
              />
              <button className="btn-primary">Confirm MFA</button>
            </form>
          </div>
        )}
        {mfaEnabled && (
          <form onSubmit={disableMfa} className="flex flex-wrap gap-3">
            <input
              className="input max-w-xs"
              value={mfaCode}
              onChange={(e) => setMfaCode(e.target.value)}
              placeholder="Code or recovery code"
              required
            />
            <button className="btn-secondary">Disable MFA</button>
          </form>
        )}
      </section>

      <section className="panel space-y-4 p-6">
        <h2 className="font-display text-2xl text-ink-950">Browser extension</h2>
        <p className="text-sm text-ink-600">
          Load <code className="font-mono text-xs">extensions/mindtrace-capture</code> as an unpacked Chrome extension.
          Generate a token here and paste it into the extension options.
        </p>
        <button className="btn-secondary" onClick={createExtensionToken}>
          Generate extension token
        </button>
        {extToken && (
          <pre className="max-h-40 overflow-auto break-all whitespace-pre-wrap rounded-xl bg-ink-950 p-4 text-xs text-ink-100">
            {extToken}
          </pre>
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
