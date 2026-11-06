"use client";

import { useEffect, useState } from "react";
import { ApiError, api } from "@/lib/api/client";

type Overview = {
  users: number;
  users_pending_deletion: number;
  jobs_queued: number;
  jobs_failed: number;
  feedback_open: number;
  active_paid: number;
  admin_email?: string;
};

type JobRow = { id: string; type: string; status: string; attempts: number; error_code: string | null };
type UserRow = { id: string; email: string; plan: string; status: string; mfa_enabled: boolean; is_admin: boolean };

export default function AdminPage() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [jobs, setJobs] = useState<JobRow[]>([]);
  const [users, setUsers] = useState<UserRow[]>([]);
  const [mfa, setMfa] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setError(null);
    try {
      const headers: HeadersInit = mfa ? { "X-Admin-MFA": mfa } : {};
      const [ov, j, u] = await Promise.all([
        api<Overview>("/admin/overview/session", { headers }),
        api<JobRow[]>("/admin/jobs/session", { headers }),
        api<UserRow[]>("/admin/users/session", { headers }),
      ]);
      setOverview(ov);
      setJobs(j);
      setUsers(u);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Admin access denied");
    }
  }

  useEffect(() => {
    load().catch(() => undefined);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function retry(jobId: string) {
    try {
      const headers: HeadersInit = mfa ? { "X-Admin-MFA": mfa } : {};
      await api(`/admin/jobs/${jobId}/retry/session`, { method: "POST", headers });
      setMessage(`Retried ${jobId}`);
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Retry failed");
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-display text-4xl font-semibold text-ink-950">Admin</h1>
        <p className="mt-2 text-ink-600">
          Session-authenticated console for users with <code className="font-mono text-xs">is_admin</code>. MFA required
          when enabled (pass code below).
        </p>
      </div>

      <div className="panel flex flex-wrap items-end gap-3 p-4">
        <label className="text-sm text-ink-600">
          Admin MFA code
          <input className="input mt-1" value={mfa} onChange={(e) => setMfa(e.target.value)} placeholder="123456" />
        </label>
        <button className="btn-primary" onClick={() => load()}>
          Refresh
        </button>
      </div>

      {error && <p className="text-sm text-red-700">{error}</p>}
      {message && <p className="text-sm text-accent-strong">{message}</p>}

      {overview && (
        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {(
            [
              ["Users", overview.users],
              ["Pending deletion", overview.users_pending_deletion],
              ["Jobs queued", overview.jobs_queued],
              ["Jobs failed", overview.jobs_failed],
              ["Open feedback", overview.feedback_open],
              ["Paid plans", overview.active_paid],
            ] as const
          ).map(([label, value]) => (
            <div key={label} className="panel p-5">
              <p className="text-sm text-ink-500">{label}</p>
              <p className="mt-2 font-display text-3xl text-ink-950">{value}</p>
            </div>
          ))}
        </section>
      )}

      <section className="space-y-3">
        <h2 className="font-display text-2xl text-ink-950">Jobs</h2>
        {jobs.map((j) => (
          <div key={j.id} className="panel flex flex-wrap items-center justify-between gap-3 p-4">
            <div>
              <p className="font-mono text-xs text-ink-500">{j.id}</p>
              <p className="text-sm text-ink-800">
                {j.type} · {j.status} · attempts {j.attempts}
                {j.error_code ? ` · ${j.error_code}` : ""}
              </p>
            </div>
            {j.status === "failed" && (
              <button className="btn-secondary" onClick={() => retry(j.id)}>
                Retry
              </button>
            )}
          </div>
        ))}
      </section>

      <section className="space-y-3">
        <h2 className="font-display text-2xl text-ink-950">Users</h2>
        <div className="panel overflow-x-auto p-2">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="text-ink-500">
                <th className="p-2">Email</th>
                <th className="p-2">Plan</th>
                <th className="p-2">Status</th>
                <th className="p-2">MFA</th>
                <th className="p-2">Admin</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-t border-ink-100">
                  <td className="p-2">{u.email}</td>
                  <td className="p-2">{u.plan}</td>
                  <td className="p-2">{u.status}</td>
                  <td className="p-2">{u.mfa_enabled ? "yes" : "no"}</td>
                  <td className="p-2">{u.is_admin ? "yes" : "no"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
