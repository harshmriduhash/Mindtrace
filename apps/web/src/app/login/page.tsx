"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { Logo } from "@/components/brand/Logo";
import { ApiError, Me, api } from "@/lib/api/client";

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

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
        },
      });
      router.push(me.user.onboarding_completed_at ? "/app/today" : "/app/onboarding");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Login failed");
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
        {error && (
          <p className="rounded-xl bg-evidence-soft px-3 py-2 text-sm text-evidence" role="alert">
            {error}
          </p>
        )}
        <button className="btn-primary w-full" disabled={loading}>
          {loading ? "Signing in…" : "Log in"}
        </button>
      </form>
      <p className="mt-6 text-sm text-ink-500">
        New here?{" "}
        <Link href="/signup" className="text-accent-strong underline-offset-2 hover:underline">
          Create an account
        </Link>
      </p>
    </div>
  );
}
