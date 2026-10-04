import Link from "next/link";
import { canAccessModule, getViewer, toClientViewer } from "@/lib/access";
import { getCourse } from "@/lib/content";
import AccountBadge from "@/components/AccountBadge";
import BuyButton from "@/components/BuyButton";
import CourseMap from "@/components/CourseMap";

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
    <div className="min-h-screen">
      <header className="flex h-14 items-center gap-3 border-b border-line bg-panel px-6">
        <Link href="/" className="font-semibold text-accent">
          FDE Playbook
        </Link>
        <div className="ml-auto">
          <AccountBadge viewer={clientViewer} />
        </div>
      </header>
      <main className="mx-auto max-w-4xl px-6 py-10">
        {checkout && NOTICES[checkout] && <p className="mb-6 rounded-lg bg-amber-400/10 p-3 text-sm text-amber-200">{NOTICES[checkout]}</p>}
        <h1 className="text-3xl font-bold text-white">{course.title}</h1>
        <p className="mt-2 text-gray-400">{course.tagline}</p>
        {!viewer.hasPurchased && (
          <div className="mt-6 flex flex-wrap items-center gap-4 rounded-xl border border-accent/30 bg-accent/5 p-5">
            <p className="flex-1 text-sm text-gray-300">
              Module 1 is free. Unlock all {course.modules.length} modules, every exercise and the AI tutor with a one-time payment.
            </p>
            <BuyButton viewer={clientViewer} price={course.priceUsd} />
          </div>
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
            plannedLessons: m.plannedLessons,
            lessons: m.lessons.map((l) => ({ slug: l.slug, title: l.title, type: l.type, minutes: l.minutes })),
          }))}
        />
      </main>
    </div>
  );
}
