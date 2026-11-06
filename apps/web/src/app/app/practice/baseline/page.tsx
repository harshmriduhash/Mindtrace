"use client";

import { PracticeSession } from "@/features/practice/PracticeSession";

export default function BaselinePage() {
  return (
    <div>
      <p className="mb-4 font-mono text-xs uppercase tracking-[0.18em] text-accent-strong">Baseline</p>
      <PracticeSession fallbackType="baseline" />
    </div>
  );
}
