"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { Logo } from "@/components/brand/Logo";
import { ApiError, api } from "@/lib/api/client";

function VerifyInner() {
  const params = useSearchParams();
  const token = params.get("token");
  const [message, setMessage] = useState("Verifying…");
  const [ok, setOk] = useState(false);

  useEffect(() => {
    if (!token) {
      setMessage("Missing verification token.");
      return;
    }
    api("/auth/verify-email", { method: "POST", json: { token } })
      .then(() => {
        setOk(true);
        setMessage("Email verified. You can continue learning.");
      })
      .catch((err) => setMessage(err instanceof ApiError ? err.message : "Verification failed"));
  }, [token]);

  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-6">
      <Logo className="mb-8" />
      <h1 className="font-display text-3xl text-ink-950">Email verification</h1>
      <p className={`mt-4 text-sm ${ok ? "text-accent-strong" : "text-ink-600"}`}>{message}</p>
      <Link href="/app/today" className="btn-primary mt-8 inline-flex w-fit">
        Go to Today
      </Link>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<div className="p-8 text-ink-500">Loading…</div>}>
      <VerifyInner />
    </Suspense>
  );
}
