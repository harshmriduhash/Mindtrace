import Link from "next/link";
import { Logo } from "@/components/brand/Logo";

const STEPS = [
  { title: "Choose a skill goal", body: "Pick a narrow technical path and a weekly time budget." },
  { title: "Establish baseline", body: "Show evidence of starting capability—not a profile quiz." },
  { title: "Learn with provenance", body: "Import sources, approve extracted concepts, keep citations." },
  { title: "Retrieve, apply, diagnose", body: "Practice unaided recall and realistic tasks with transparent rubrics." },
  { title: "Return with memory", body: "Mindtrace remembers mistakes and schedules the next best action." },
];

export default function ProductPage() {
  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <Logo />
      <h1 className="mt-10 font-display text-4xl font-semibold text-ink-950">How Mindtrace works</h1>
      <p className="mt-3 text-ink-600">
        Product before AI. The core value is the learning workflow that connects sources, recall, application, and
        evidence.
      </p>
      <ol className="mt-10 space-y-6">
        {STEPS.map((step, i) => (
          <li key={step.title} className="panel p-5">
            <p className="font-mono text-xs uppercase tracking-widest text-accent-strong">Step {i + 1}</p>
            <h2 className="mt-2 font-display text-2xl text-ink-950">{step.title}</h2>
            <p className="mt-2 text-ink-600">{step.body}</p>
          </li>
        ))}
      </ol>
      <Link href="/signup" className="btn-primary mt-10 inline-flex">
        Build my skill plan
      </Link>
    </div>
  );
}
