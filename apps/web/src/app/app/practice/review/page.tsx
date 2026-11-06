"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { PracticeItem, api } from "@/lib/api/client";
import { PracticeSession } from "@/features/practice/PracticeSession";

function ReviewInner() {
  const params = useSearchParams();
  const itemParam = params.get("item");
  const [itemId, setItemId] = useState<string | null>(itemParam);

  useEffect(() => {
    if (itemParam) return;
    api<PracticeItem[]>("/reviews/due").then((rows) => setItemId(rows[0]?.id || null));
  }, [itemParam]);

  if (!itemId) {
    return <div className="panel p-6 text-ink-600">No reviews due. Great time to import a source or attempt a design task.</div>;
  }
  return <PracticeSession itemId={itemId} />;
}

export default function ReviewPage() {
  return (
    <div>
      <p className="mb-4 font-mono text-xs uppercase tracking-[0.18em] text-accent-strong">Review</p>
      <Suspense fallback={<div className="panel p-8 text-ink-500">Loading…</div>}>
        <ReviewInner />
      </Suspense>
    </div>
  );
}
