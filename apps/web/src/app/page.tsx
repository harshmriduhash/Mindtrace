import Link from "next/link";
import { Logo } from "@/components/brand/Logo";

export default function HomePage() {
  return (
    <div className="relative overflow-hidden">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 opacity-40"
        style={{
          backgroundImage:
            "linear-gradient(rgba(14,18,16,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(14,18,16,0.04) 1px, transparent 1px)",
          backgroundSize: "48px 48px",
          maskImage: "radial-gradient(ellipse at center, black 30%, transparent 75%)",
        }}
      />

      <header className="relative mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <Logo />
        <div className="flex items-center gap-3">
          <Link href="/login" className="btn-secondary">
            Log in
          </Link>
          <Link href="/signup" className="btn-primary">
            Build my skill plan
          </Link>
        </div>
      </header>

      <section className="relative mx-auto flex min-h-[78vh] max-w-6xl flex-col justify-center px-6 pb-20 pt-10">
        <p className="mb-4 font-mono text-xs uppercase tracking-[0.22em] text-accent-strong animate-rise">
          Personal skill development
        </p>
        <h1 className="max-w-3xl font-display text-5xl font-semibold leading-[1.05] tracking-tight text-ink-950 md:text-6xl animate-rise [animation-delay:80ms]">
          Mindtrace
        </h1>
        <p className="mt-5 max-w-2xl text-xl leading-relaxed text-ink-700 animate-rise [animation-delay:140ms]">
          Turn what you study into what you can do.
        </p>
        <p className="mt-3 max-w-xl text-base leading-relaxed text-ink-500 animate-rise [animation-delay:200ms]">
          Build durable technical skills through active recall, realistic practice, and feedback that remembers where
          you need to improve.
        </p>
        <div className="mt-8 flex flex-wrap gap-3 animate-rise [animation-delay:260ms]">
          <Link href="/signup" className="btn-primary">
            Build my skill plan
          </Link>
          <Link href="/product" className="btn-secondary">
            How it works
          </Link>
        </div>
      </section>

      <footer className="relative mx-auto flex max-w-6xl flex-wrap gap-4 border-t border-ink-100/80 px-6 py-8 text-sm text-ink-500">
        <Link href="/methodology" className="hover:text-ink-800">
          Methodology
        </Link>
        <Link href="/privacy" className="hover:text-ink-800">
          Privacy
        </Link>
        <Link href="/security" className="hover:text-ink-800">
          Security
        </Link>
        <Link href="/product" className="hover:text-ink-800">
          Product
        </Link>
      </footer>
    </div>
  );
}
