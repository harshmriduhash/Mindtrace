import Link from "next/link";
import { Logo } from "@/components/brand/Logo";

export default function MethodologyPage() {
  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <Logo />
      <h1 className="mt-10 font-display text-4xl font-semibold text-ink-950">How progress is assessed</h1>
      <p className="mt-3 text-ink-600">
        Mindtrace never equates content consumed with mastery. Progress claims require evidence.
      </p>
      <ol className="mt-8 space-y-4">
        <li className="panel p-5">
          <h2 className="font-display text-xl text-ink-950">1. Baseline</h2>
          <p className="mt-2 text-ink-600">Establish starting capability with explain / design / diagnose tasks.</p>
        </li>
        <li className="panel p-5">
          <h2 className="font-display text-xl text-ink-950">2. Rubric dimensions</h2>
          <p className="mt-2 text-ink-600">Correctness, trade-off reasoning, and clarity — versioned and inspectable.</p>
        </li>
        <li className="panel p-5">
          <h2 className="font-display text-xl text-ink-950">3. Provisional coaching scores</h2>
          <p className="mt-2 text-ink-600">AI or deterministic scores are coaching signals with uncertainty — not hiring decisions.</p>
        </li>
        <li className="panel p-5">
          <h2 className="font-display text-xl text-ink-950">4. Longitudinal memory</h2>
          <p className="mt-2 text-ink-600">Errors recur in your memory; reviews are scheduled from performance, not streaks.</p>
        </li>
      </ol>
      <Link href="/signup" className="btn-primary mt-10 inline-flex">
        Build my skill plan
      </Link>
    </div>
  );
}
