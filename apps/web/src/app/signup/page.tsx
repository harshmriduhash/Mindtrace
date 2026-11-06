"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { Logo } from "@/components/brand/Logo";
import { ApiError, api } from "@/lib/api/client";

export default function SignupPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    const form = new FormData(e.currentTarget);
    try {
      await api("/auth/signup", {
        method: "POST",
        json: {
          email: form.get("email"),
          password: form.get("password"),
          display_name: form.get("display_name") || null,
        },
      });
      router.push("/app/onboarding");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Signup failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-6 py-12">
      <Logo className="mb-8" />
      <h1 className="font-display text-3xl font-semibold text-ink-950">Create your account</h1>
      <p className="mt-2 text-sm text-ink-500">Start with one skill path. Evidence first.</p>
      <form onSubmit={onSubmit} className="mt-8 space-y-4">
        <div>
          <label className="label" htmlFor="display_name">
            Display name
          </label>
          <input className="input" id="display_name" name="display_name" placeholder="Alex" />
        </div>
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
            minLength={8}
            autoComplete="new-password"
          />
        </div>
        {error && (
          <p className="rounded-xl bg-evidence-soft px-3 py-2 text-sm text-evidence" role="alert">
            {error}
          </p>
        )}
        <button className="btn-primary w-full" disabled={loading}>
          {loading ? "Creating…" : "Create account"}
        </button>
      </form>
      <p className="mt-6 text-sm text-ink-500">
        Already have an account?{" "}
        <Link href="/login" className="text-accent-strong underline-offset-2 hover:underline">
          Log in
        </Link>
      </p>
    </div>
  );
}
