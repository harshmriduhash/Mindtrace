import Link from "next/link";
import { Logo } from "@/components/brand/Logo";

export default function SecurityPage() {
  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <Logo />
      <h1 className="mt-10 font-display text-4xl font-semibold text-ink-950">Security</h1>
      <p className="mt-3 text-ink-600">Security by default — because learning history is sensitive personal evidence.</p>
      <ul className="mt-8 space-y-3 text-ink-700">
        <li className="panel p-4">HttpOnly session cookies; passwords hashed with Argon2id</li>
        <li className="panel p-4">Every resource query is scoped to the owning user</li>
        <li className="panel p-4">SSRF protections on URL import; private IPs and localhost blocked</li>
        <li className="panel p-4">PDF size/page limits; encrypted PDFs rejected</li>
        <li className="panel p-4">Rate limits on signup, login, and verification</li>
        <li className="panel p-4">Imported source text treated as untrusted data, never as instructions</li>
      </ul>
      <Link href="/" className="btn-secondary mt-10 inline-flex">
        Back home
      </Link>
    </div>
  );
}
