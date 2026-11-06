"use client";

import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { PracticeSession } from "@/features/practice/PracticeSession";

function AssessmentInner() {
  const params = useSearchParams();
  return <PracticeSession itemId={params.get("item")} />;
}

export default function AssessmentPage() {
  return (
    <div>
      <p className="mb-4 font-mono text-xs uppercase tracking-[0.18em] text-accent-strong">Assessment</p>
      <Suspense fallback={<div className="panel p-8 text-ink-500">Loading…</div>}>
        <AssessmentInner />
      </Suspense>
    </div>
  );
}
