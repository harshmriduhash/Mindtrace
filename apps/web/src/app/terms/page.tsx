import Link from "next/link";
import { Logo } from "@/components/brand/Logo";

export default function TermsPage() {
  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <Logo />
      <h1 className="mt-10 font-display text-4xl font-semibold text-ink-950">Terms of use</h1>
      <div className="mt-6 space-y-4 text-ink-700">
        <p>Mindtrace is a personal skill-development product. It provides coaching signals, not hiring decisions or exam guarantees.</p>
        <p>You are responsible for only importing content you have rights to use. Do not use Mindtrace to cheat in live interviews or assessments.</p>
        <p>Paid plans (when enabled) use India-capable billing via Razorpay. Stripe is not used for this launch geography. Cancellation stops renewal; access continues through the paid-through date where applicable.</p>
        <p>Beta software may change. Export and deletion controls are available in Settings.</p>
      </div>
      <div className="mt-8 flex gap-3">
        <Link href="/privacy" className="btn-secondary">
          Privacy
        </Link>
        <Link href="/signup" className="btn-primary">
          Build my skill plan
        </Link>
      </div>
    </div>
  );
}
