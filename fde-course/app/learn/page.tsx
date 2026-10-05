import Link from "next/link";
import { canAccessModule, getViewer, toClientViewer } from "@/lib/access";
import { getCourse } from "@/lib/content";
import AccountBadge from "@/components/AccountBadge";
import BuyButton from "@/components/BuyButton";
import CourseMap from "@/components/CourseMap";
import { Mark } from "@/components/Playbook";

export const metadata = { title: "Your course" };
export const dynamic = "force-dynamic";

const NOTICES: Record<string, string> = {
  unavailable: "Purchases aren't open yet. Module 1 is free to take right now.",
  error: "We couldn't start checkout. Please try again in a minute.",
};

export default async function LearnPage({ searchParams }: { searchParams: Promise<{ checkout?: string }> }) {
  const { checkout } = await searchParams;
  const course = getCourse();
  const viewer = await getViewer();
  const clientViewer = toClientViewer(viewer);

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
        <CourseMap
          viewer={clientViewer}
          modules={course.modules.map((m) => ({
            slug: m.slug,
            number: m.number,
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
              <span className="block font-serif text-xl text-paper">Unlock every engagement.</span>
              Module 1 is free. Get all {course.modules.length} modules, every exercise and the AI tutor with a one-time payment.
            </p>
            <BuyButton viewer={clientViewer} price={course.priceUsd} />
          </div>
        )}
      </main>
    </div>
  );
}
