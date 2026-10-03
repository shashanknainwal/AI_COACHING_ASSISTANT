import Link from "next/link";
import { notFound } from "next/navigation";
import LessonWorkspace from "@/components/LessonWorkspace";
import BuyButton from "@/components/BuyButton";
import { canAccessModule, getViewer, toClientViewer } from "@/lib/access";
import { getCourse, getLesson, getLessonSequence } from "@/lib/content";

// Rendered per request so paid lesson content is only sent to learners who bought the course.
export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: { params: Promise<{ module: string; lesson: string }> }) {
  const { module, lesson } = await params;
  const l = getLesson(module, lesson);
  return { title: l ? `${l.title} — FDE Course` : "FDE Course" };
}

export default async function LessonPage({ params }: { params: Promise<{ module: string; lesson: string }> }) {
  const { module, lesson: lessonSlug } = await params;
  const lesson = getLesson(module, lessonSlug);
  if (!lesson) notFound();

  const course = getCourse();
  const mod = course.modules.find((m) => m.slug === module)!;
  const viewer = await getViewer();
  const clientViewer = toClientViewer(viewer);

  if (!canAccessModule(viewer, module)) {
    return (
      <main className="mx-auto flex min-h-screen max-w-lg flex-col justify-center px-6 text-center">
        <div className="text-4xl">🔒</div>
        <p className="mt-4 text-sm uppercase tracking-widest text-gray-500">
          Module {mod.number}: {mod.title}
        </p>
        <h1 className="mt-2 text-2xl font-bold text-white">{lesson.title}</h1>
        <p className="mt-4 text-gray-400">
          This lesson is part of the full course. Get lifetime access to all {course.modules.length} modules, every exercise and the AI tutor for a
          one-time ${course.priceUsd}.
        </p>
        <div className="mt-8 flex flex-col items-center gap-3">
          <BuyButton viewer={clientViewer} price={course.priceUsd} />
          <Link href="/learn" className="text-sm text-gray-400 hover:text-white">
            Back to the course
          </Link>
        </div>
      </main>
    );
  }

  const seq = getLessonSequence();
  const i = seq.findIndex((l) => l.moduleSlug === module && l.slug === lessonSlug);
  const link = (j: number) => (seq[j] ? { href: `/learn/${seq[j].moduleSlug}/${seq[j].slug}`, title: seq[j].title } : null);

  return (
    <LessonWorkspace
      viewer={clientViewer}
      lesson={{
        moduleSlug: lesson.moduleSlug,
        slug: lesson.slug,
        title: lesson.title,
        type: lesson.type,
        minutes: lesson.minutes,
        html: lesson.html,
        hints: lesson.hints,
        questions: lesson.questions,
        starter: lesson.starter,
        setup: lesson.setup,
        tests: lesson.tests,
      }}
      moduleTitle={mod.title}
      moduleNumber={mod.number}
      position={{ index: i + 1, total: seq.length }}
      prev={link(i - 1)}
      next={link(i + 1)}
    />
  );
}
