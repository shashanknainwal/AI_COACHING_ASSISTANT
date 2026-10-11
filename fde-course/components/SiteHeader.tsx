import Link from "next/link";
import type { ClientViewer } from "@/lib/access";
import { SITE_NAME } from "@/lib/config";
import AccountBadge from "./AccountBadge";
import { Mark } from "./Playbook";

/** Sub-navigation for the learner pages: map, progress, plan, review, community. */
export const SITE_NAV: [string, string][] = [
  ["/learn", "Map"],
  ["/learn/progress", "Progress"],
  ["/start", "My plan"],
  ["/review", "Review"],
  ["/community", "Peer mocks"],
];

export function SiteNav({ current, className = "" }: { current?: string; className?: string }) {
  return (
    <nav aria-label="Course pages" className={`flex gap-1 overflow-x-auto text-sm ${className}`}>
      {SITE_NAV.map(([href, label]) => (
        <Link
          key={href}
          href={href}
          aria-current={current === href ? "page" : undefined}
          className={`shrink-0 whitespace-nowrap rounded-full px-3 py-1 ${current === href ? "bg-graphite text-paper" : "text-graphite-2 hover:bg-paper-2 hover:text-graphite"}`}
        >
          {label}
        </Link>
      ))}
    </nav>
  );
}

export default function SiteHeader({ viewer, current }: { viewer?: ClientViewer; current?: string }) {
  return (
    <header className="sticky top-0 z-20 border-b border-rule bg-paper/90 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-6xl items-center gap-3 px-4 sm:px-6">
        <Link href="/" className="flex shrink-0 items-center gap-2 font-serif text-base font-semibold text-graphite">
          <Mark />
          <span className="hidden sm:inline">{SITE_NAME}</span>
        </Link>
        <SiteNav current={current} className="hidden min-w-0 md:flex" />
        {viewer && (
          <div className="ml-auto shrink-0 [&_*]:!text-graphite-2 [&_a]:!border-rule [&_button]:!border-rule">
            <AccountBadge viewer={viewer} />
          </div>
        )}
      </div>
      <div className="border-t border-rule/70 px-4 py-1.5 md:hidden">
        <SiteNav current={current} />
      </div>
    </header>
  );
}
