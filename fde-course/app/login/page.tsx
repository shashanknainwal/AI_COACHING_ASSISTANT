import Link from "next/link";
import { redirect } from "next/navigation";
import { getViewer } from "@/lib/access";
import { safeNext } from "@/lib/safe-next";
import LoginForm from "./LoginForm";
import { Mark } from "@/components/Playbook";

export const metadata = { title: "Log in" };

export default async function LoginPage({ searchParams }: { searchParams: Promise<{ next?: string; error?: string }> }) {
  const { next, error } = await searchParams;
  const dest = safeNext(next);
  const viewer = await getViewer();
  if (viewer.user) redirect(dest);

  return (
    <main className="playbook-page flex min-h-screen items-center justify-center px-6 py-16">
      <div className="w-full max-w-sm">
        <Link href="/" className="flex items-center justify-center gap-2 font-serif text-lg font-semibold text-graphite">
          <Mark />
          FDE Playbook
        </Link>
        <div className="mt-8 rounded-3xl border border-rule bg-white/80 p-7 shadow-[0_30px_60px_-40px_rgba(29,27,22,0.6)]">
          <h1 className="font-serif text-3xl font-semibold text-graphite">Log in or sign up</h1>
          <p className="mt-2 text-sm text-graphite-3">We&apos;ll email you a link. No password needed.</p>
          {error && (
            <p className="mt-4 rounded-xl border border-vermilion/30 bg-vermilion/5 p-3 text-sm text-graphite-2">
              That login link didn&apos;t work or has expired. Request a new one.
            </p>
          )}
          {viewer.mode === "live" ? (
            <LoginForm next={dest} />
          ) : (
            <div className="mt-6 rounded-xl border border-rule bg-paper/70 p-4 text-sm text-graphite-2">
              {viewer.mode === "dev"
                ? "Logins aren't configured yet, so this is a preview with every module unlocked."
                : "Accounts are coming soon. Module 1 is free to try right now."}
              <Link href="/learn" className="mt-3 block font-semibold text-forest">
                Go to the course →
              </Link>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
