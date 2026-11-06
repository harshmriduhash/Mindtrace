export function Logo({ className = "" }: { className?: string }) {
  return (
    <div className={`inline-flex items-center gap-2 ${className}`}>
      <svg width="28" height="28" viewBox="0 0 32 32" fill="none" aria-hidden="true">
        <circle cx="6" cy="24" r="2.2" fill="#0F7A5F" />
        <circle cx="14" cy="12" r="2.2" fill="#0F7A5F" />
        <circle cx="26" cy="8" r="2.2" fill="#C45C26" />
        <path
          d="M6 24 C10 18, 10 16, 14 12 C18 8, 22 9, 26 8"
          stroke="#0F7A5F"
          strokeWidth="1.6"
          strokeLinecap="round"
          fill="none"
          className="animate-trace"
          strokeDasharray="120"
        />
      </svg>
      <span className="font-display text-xl font-semibold tracking-tight text-ink-950">Mindtrace</span>
    </div>
  );
}
