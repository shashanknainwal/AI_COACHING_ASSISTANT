import Link from "next/link";
import { redirect } from "next/navigation";
import { getViewer } from "@/lib/access";
import { safeNext } from "@/lib/safe-next";
import LoginForm from "./LoginForm";

export const metadata = { title: "Log in — FDE Course" };

export default async function LoginPage({ searchParams }: { searchParams: Promise<{ next?: string; error?: string }> }) {
  const { next, error } = await searchParams;
  const dest = safeNext(next);
  const viewer = await getViewer();
  if (viewer.user) redirect(dest);

  return (
    <main className="mx-auto flex min-h-screen max-w-sm flex-col justify-center px-6">
      <Link href="/" className="mb-10 font-semibold text-accent">
        FDE Course
      </Link>
      <h1 className="text-2xl font-bold text-white">Log in or sign up</h1>
      <p className="mt-2 text-sm text-gray-400">We&apos;ll email you a link. No password needed.</p>
      {error && <p className="mt-4 rounded bg-red-500/10 p-3 text-sm text-red-300">That login link didn&apos;t work or has expired. Request a new one.</p>}
      {viewer.mode === "live" ? (
        <LoginForm next={dest} />
      ) : (
        <div className="mt-6 rounded-lg border border-line bg-panel p-4 text-sm text-gray-300">
          {viewer.mode === "dev"
            ? "Logins aren't configured yet, so this is a local preview with every module unlocked. Add your Supabase keys to .env.local to turn on accounts."
            : "Accounts are coming soon. Module 1 is free to try right now."}
          <Link href="/learn" className="mt-3 block font-semibold text-accent">
            Go to the course →
          </Link>
        </div>
      )}
    </main>
  );
}
