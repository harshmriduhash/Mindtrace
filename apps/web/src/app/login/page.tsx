"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { Logo } from "@/components/brand/Logo";
import { ApiError, Me, api } from "@/lib/api/client";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [needMfa, setNeedMfa] = useState(false);
  const [providers, setProviders] = useState<{ google: boolean; github: boolean }>({ google: false, github: false });

  useEffect(() => {
    api<{ google: boolean; github: boolean }>("/auth/oauth/providers")
      .then(setProviders)
      .catch(() => undefined);
  }, []);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    const form = new FormData(e.currentTarget);
    try {
      const me = await api<Me>("/auth/login", {
        method: "POST",
        json: {
          email: form.get("email"),
          password: form.get("password"),
          mfa_code: form.get("mfa_code") || undefined,
        },
      });
      router.push(me.user.onboarding_completed_at ? "/app/today" : "/app/onboarding");
    } catch (err) {
      if (err instanceof ApiError && err.code === "mfa_required") {
        setNeedMfa(true);
        setError("Enter your authenticator code to continue.");
      } else {
        setError(err instanceof ApiError ? err.message : "Login failed");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-6 py-12">
      <Logo className="mb-8" />
      <h1 className="font-display text-3xl font-semibold text-ink-950">Welcome back</h1>
      <p className="mt-2 text-sm text-ink-500">Resume from your current skill state.</p>
      <form onSubmit={onSubmit} className="mt-8 space-y-4">
        <div>
          <label className="label" htmlFor="email">
            Email
          </label>
          <input className="input" id="email" name="email" type="email" required autoComplete="email" />
        </div>
        <div>
          <label className="label" htmlFor="password">
            Password
          </label>
          <input
            className="input"
            id="password"
            name="password"
            type="password"
            required
            autoComplete="current-password"
          />
        </div>
        <div>
          <label className="label" htmlFor="mfa_code">
            MFA code {needMfa ? "(required)" : "(optional)"}
          </label>
          <input className="input" id="mfa_code" name="mfa_code" inputMode="numeric" autoComplete="one-time-code" />
        </div>
        {error && (
          <p className="rounded-xl bg-evidence-soft px-3 py-2 text-sm text-evidence" role="alert">
            {error}
          </p>
        )}
        <button className="btn-primary w-full" disabled={loading}>
          {loading ? "Signing in…" : "Log in"}
        </button>
      </form>

      {(providers.google || providers.github) && (
        <div className="mt-6 space-y-2">
          <p className="text-center text-xs uppercase tracking-wider text-ink-400">Or continue with</p>
          {providers.google && (
            <a className="btn-secondary flex w-full justify-center" href={`${API_BASE}/auth/oauth/google/start`}>
              Google
            </a>
          )}
          {providers.github && (
            <a className="btn-secondary flex w-full justify-center" href={`${API_BASE}/auth/oauth/github/start`}>
              GitHub
            </a>
          )}
        </div>
      )}

      <p className="mt-6 text-sm text-ink-500">
        New here?{" "}
        <Link href="/signup" className="text-accent-strong underline-offset-2 hover:underline">
          Create an account
        </Link>
      </p>
    </div>
  );
}
