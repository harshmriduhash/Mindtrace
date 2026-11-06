import Link from "next/link";
import { Logo } from "@/components/brand/Logo";

export default function PrivacyPage() {
  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <Logo />
      <h1 className="mt-10 font-display text-4xl font-semibold text-ink-950">Privacy</h1>
      <p className="mt-3 text-ink-600">
        Mindtrace is built for personal skill development. Your learning memory belongs to you.
      </p>
      <div className="prose-like mt-8 space-y-4 text-ink-700">
        <p>We collect only what the learning workflow needs: account details, sources you import, practice responses, and progress evidence.</p>
        <p>We do not sell learner data. We do not use your private responses to train third-party models without explicit consent.</p>
        <p>When AI features are enabled, relevant excerpts may be sent to a model provider to generate feedback. You can use Mindtrace with AI disabled via deterministic fallbacks.</p>
        <p>You can export or request deletion of your data from Settings at any time.</p>
      </div>
      <Link href="/" className="btn-secondary mt-10 inline-flex">
        Back home
      </Link>
    </div>
  );
}
