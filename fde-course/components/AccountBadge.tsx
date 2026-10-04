import Link from "next/link";
import type { ClientViewer } from "@/lib/access";

export default function AccountBadge({ viewer, compact = false }: { viewer: ClientViewer; compact?: boolean }) {
  if (viewer.mode === "dev") {
    return (
      <span className="rounded bg-amber-400/15 px-2 py-1 text-xs text-amber-300" title="Logins and payments aren't configured. Every module is unlocked.">
        Dev preview
      </span>
    );
  }
  if (viewer.mode === "unconfigured") return null;

  if (!viewer.signedIn) {
    return (
      <Link href="/login" className="rounded-lg border border-line px-3 py-1 text-sm text-gray-200 hover:bg-line">
        Log in
      </Link>
    );
  }

  return (
    <form action="/auth/signout" method="post" className="flex items-center gap-2 text-sm">
      {!compact && <span className="hidden max-w-48 truncate text-gray-400 sm:inline">{viewer.email}</span>}
      <button type="submit" className="rounded-lg border border-line px-3 py-1 text-gray-300 hover:bg-line">
        Log out
      </button>
    </form>
  );
}
