import { notFound } from "next/navigation";
import LessonWorkspace from "@/components/LessonWorkspace";
import { getCourse, getLesson, getLessonSequence } from "@/lib/content";

export function generateStaticParams() {
  return getLessonSequence().map((l) => ({ module: l.moduleSlug, lesson: l.slug }));
}

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
  const seq = getLessonSequence();
  const i = seq.findIndex((l) => l.moduleSlug === module && l.slug === lessonSlug);
  const link = (j: number) => (seq[j] ? { href: `/learn/${seq[j].moduleSlug}/${seq[j].slug}`, title: seq[j].title } : null);

  // TODO(paywall): once Stripe is wired, redirect unpaid users to /#pricing for any module after the first.

  return (
    <LessonWorkspace
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
