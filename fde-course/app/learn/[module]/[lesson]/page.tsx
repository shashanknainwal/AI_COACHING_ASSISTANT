import Link from "next/link";
import { notFound } from "next/navigation";
import LessonWorkspace from "@/components/LessonWorkspace";
import BuyButton from "@/components/BuyButton";
import { canAccessLesson, getViewer, toClientViewer } from "@/lib/access";
import { getCourse, getLesson, getLessonSequence, getModule, toClientLesson } from "@/lib/content";

// Rendered per request so paid lesson content is only sent to learners who bought the course.
export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: { params: Promise<{ module: string; lesson: string }> }) {
  const { module, lesson } = await params;
  const l = getLesson(module, lesson);
  return { title: l ? l.title : "Lesson" };
}

export default async function LessonPage({ params }: { params: Promise<{ module: string; lesson: string }> }) {
  const { module, lesson: lessonSlug } = await params;
  const lesson = getLesson(module, lessonSlug);
  if (!lesson) notFound();

  const course = getCourse();
  const mod = getModule(module)!;
  const viewer = await getViewer();
  const clientViewer = toClientViewer(viewer);

  if (!canAccessLesson(viewer, module, lessonSlug)) {
    return (
      <main className="playbook-page flex min-h-screen items-center justify-center px-6">
        <div className="w-full max-w-lg rounded-3xl border border-rule bg-white/75 p-8 text-center shadow-[0_30px_60px_-40px_rgba(29,27,22,0.6)] sm:p-10">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-graphite text-lg text-paper">🔒</div>
          <p className="mt-5 text-[11px] font-semibold uppercase tracking-[0.16em] text-graphite-3">
            {mod.label} · {mod.customer.company}
          </p>
          <h1 className="mt-2 font-serif text-3xl font-semibold leading-tight text-graphite">{lesson.title}</h1>
          <p className="mt-4 text-graphite-2">
            This lesson is part of the full course. Get lifetime access to{" "}
            {course.tracks.length > 1 ? "all four tracks, every graded task and the mock loops" : `all ${course.modules.length} modules, every exercise and the AI tutor`} for
            a one-time ${course.priceUsd}.
          </p>
          <div className="mt-8 flex flex-col items-center gap-3">
            <BuyButton viewer={clientViewer} price={course.priceUsd} />
            <Link href={`/learn?track=${mod.track}`} className="text-sm text-graphite-3 hover:text-graphite">
              Back to your map
            </Link>
          </div>
        </div>
      </main>
    );
  }

  const seq = getLessonSequence(mod.track);
  const i = seq.findIndex((l) => l.moduleSlug === module && l.slug === lessonSlug);
  const link = (j: number) => (seq[j] ? { href: `/learn/${seq[j].moduleSlug}/${seq[j].slug}`, title: seq[j].title } : null);

  return (
    <LessonWorkspace
      key={`${module}/${lessonSlug}`}
      viewer={clientViewer}
      // toClientLesson drops graderNotes, personaBrief, constraints and anchors: they must never reach the browser.
      lesson={toClientLesson(lesson)}
      track={mod.track}
      moduleLabel={mod.label}
      moduleTitle={mod.title}
      customer={mod.customer}
      siblings={mod.lessons.map((l) => ({ slug: l.slug, title: l.title, type: l.type }))}
      position={{ index: i + 1, total: seq.length }}
      prev={link(i - 1)}
      next={link(i + 1)}
    />
  );
}
