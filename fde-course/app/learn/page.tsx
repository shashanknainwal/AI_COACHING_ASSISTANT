import Link from "next/link";
import { canAccessModule, getViewer, toClientViewer } from "@/lib/access";
import { FDE_TRACK, getCourse } from "@/lib/content";
import AccountBadge from "@/components/AccountBadge";
import BuyButton from "@/components/BuyButton";
import CourseMap from "@/components/CourseMap";
import { Mark } from "@/components/Playbook";

export const metadata = { title: "Your course" };
export const dynamic = "force-dynamic";

const NOTICES: Record<string, string> = {
  unavailable: "Purchases aren't open yet. The free lessons are open to everyone right now.",
  error: "We couldn't start checkout. Please try again in a minute.",
};

export default async function LearnPage({ searchParams }: { searchParams: Promise<{ checkout?: string; track?: string }> }) {
  const { checkout, track: trackParam } = await searchParams;
  const course = getCourse();
  const viewer = await getViewer();
  const clientViewer = toClientViewer(viewer);
  const multi = course.tracks.length > 1;
  // Everyone starts on the shared core; the FDE course is the only track until launch.
  const track = course.tracks.find((t) => t.slug === trackParam) ?? course.tracks.find((t) => t.slug === (multi ? "core" : FDE_TRACK)) ?? course.tracks[0];
  const modules = course.modules.filter((m) => m.track === track.slug);

  return (
    <div className="playbook-page min-h-screen">
      <header className="sticky top-0 z-20 border-b border-rule bg-paper/85 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-6xl items-center gap-3 px-4 sm:px-6">
          <Link href="/" className="flex items-center gap-2 font-serif text-base font-semibold text-graphite">
            <Mark />
            FDE Playbook
          </Link>
          <div className="ml-auto [&_*]:!text-graphite-2 [&_a]:!border-rule [&_button]:!border-rule">
            <AccountBadge viewer={clientViewer} />
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 pb-20 pt-10 sm:px-6">
        {checkout && NOTICES[checkout] && (
          <p className="mb-6 rounded-xl border border-vermilion/30 bg-vermilion/5 p-3 text-sm text-graphite-2">{NOTICES[checkout]}</p>
        )}
        {multi && (
          <nav className="-mx-4 mb-10 flex gap-3 overflow-x-auto px-4 pb-2 sm:mx-0 sm:grid sm:grid-cols-4 sm:overflow-visible sm:px-0" aria-label="Tracks">
            {course.tracks.map((t) => {
              const mods = course.modules.filter((m) => m.track === t.slug);
              const hours = Math.round(mods.reduce((n, m) => n + m.minutes, 0) / 60);
              const active = t.slug === track.slug;
              return (
                <Link
                  key={t.slug}
                  href={`/learn?track=${t.slug}`}
                  aria-current={active ? "page" : undefined}
                  className={`min-w-[13.5rem] rounded-2xl border p-4 transition sm:min-w-0 ${
                    active ? "border-graphite bg-graphite text-paper shadow-[0_18px_40px_-26px_rgba(29,27,22,0.8)]" : "border-rule bg-white/60 text-graphite hover:border-graphite-3"
                  }`}
                >
                  <span className={`block font-mono text-[10px] uppercase tracking-[0.16em] ${active ? "text-emerald-300" : "text-vermilion"}`}>
                    {t.slug === "core" ? "Start here" : "Track"}
                  </span>
                  <span className="mt-1 block font-serif text-lg font-semibold leading-snug">{t.short}</span>
                  <span className={`mt-1 block text-xs ${active ? "text-paper-3" : "text-graphite-3"}`}>
                    {mods.length} modules · about {hours}h
                  </span>
                </Link>
              );
            })}
          </nav>
        )}
        {multi && (
          <p className="-mt-4 mb-10 max-w-3xl text-sm leading-relaxed text-graphite-2">
            <span className="font-semibold text-graphite">{track.title}.</span> {track.summary} <span className="text-graphite-3">For: {track.audience}</span>
          </p>
        )}
        <CourseMap
          viewer={clientViewer}
          eyebrow={multi ? `${track.short} map` : undefined}
          headline={track.headline}
          sectionTitle={track.slug === FDE_TRACK ? "Engagements" : "Modules"}
          taskLabel={track.slug === FDE_TRACK ? "cases resolved" : "graded tasks done"}
          modules={modules.map((m) => ({
            slug: m.slug,
            number: m.number,
            code: m.code,
            label: m.label,
            title: m.title,
            summary: m.summary,
            status: m.status,
            minutes: m.minutes,
            locked: !canAccessModule(viewer, m.slug),
            customer: { company: m.customer.company, sector: m.customer.sector, contact: m.customer.contact, role: m.customer.role },
            lessons: m.lessons.map((l) => ({ slug: l.slug, title: l.title, type: l.type, minutes: l.minutes })),
          }))}
        />
        {!viewer.hasPurchased && (
          <div className="mt-12 flex flex-wrap items-center gap-4 rounded-3xl bg-graphite p-6 text-paper">
            <p className="flex-1 text-sm text-paper-3">
              <span className="block font-serif text-xl text-paper">{multi ? "Unlock every track." : "Unlock every engagement."}</span>
              {multi
                ? "The first lessons of every track are free. Get all four tracks, every graded task and three mock loops with a one-time payment."
                : `Module 1 is free. Get all ${course.modules.length} modules, every exercise and the AI tutor with a one-time payment.`}
            </p>
            <BuyButton viewer={clientViewer} price={course.priceUsd} />
          </div>
        )}
      </main>
    </div>
  );
}
