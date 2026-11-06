"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Logo } from "@/components/brand/Logo";
import { api } from "@/lib/api/client";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/app/today", label: "Today" },
  { href: "/app/skills", label: "My Skills" },
  { href: "/app/passport", label: "Passport" },
  { href: "/app/learn", label: "Learn" },
  { href: "/app/practice", label: "Practice" },
  { href: "/app/practice/voice", label: "Voice" },
  { href: "/app/projects", label: "Projects" },
  { href: "/app/calendar", label: "Calendar" },
  { href: "/app/memory", label: "Memory" },
  { href: "/app/progress", label: "Progress" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  async function logout() {
    await api("/auth/logout", { method: "POST" });
    router.push("/login");
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-6xl gap-6 px-4 py-6 md:px-6">
      <aside className="hidden w-56 shrink-0 md:block">
        <div className="sticky top-6 space-y-8">
          <Logo />
          <nav className="space-y-1" aria-label="Primary">
            {NAV.map((item) => {
              const active = pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "block rounded-xl px-3 py-2 text-sm transition",
                    active ? "bg-accent-soft font-medium text-accent-strong" : "text-ink-700 hover:bg-white/70",
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
          <div className="space-y-2 border-t border-ink-100 pt-4">
            <Link href="/app/usage" className="block rounded-xl px-3 py-2 text-sm text-ink-700 hover:bg-white/70">
              Usage
            </Link>
            <Link href="/app/settings" className="block rounded-xl px-3 py-2 text-sm text-ink-700 hover:bg-white/70">
              Settings
            </Link>
            <Link href="/app/admin" className="block rounded-xl px-3 py-2 text-sm text-ink-700 hover:bg-white/70">
              Admin
            </Link>
            <button onClick={logout} className="block w-full rounded-xl px-3 py-2 text-left text-sm text-ink-500 hover:bg-white/70">
              Log out
            </button>
          </div>
        </div>
      </aside>
      <main className="min-w-0 flex-1 animate-rise">{children}</main>
    </div>
  );
}
