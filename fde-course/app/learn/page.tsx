import Link from "next/link";
import { getCourse } from "@/lib/content";
import CourseMap from "@/components/CourseMap";

export const metadata = { title: "Your course — FDE Course" };

export default function LearnPage() {
  const course = getCourse();
  return (
    <div className="min-h-screen">
      <header className="flex h-14 items-center border-b border-line bg-panel px-6">
        <Link href="/" className="font-semibold text-accent">
          FDE Course
        </Link>
      </header>
      <main className="mx-auto max-w-4xl px-6 py-10">
        <h1 className="text-3xl font-bold text-white">{course.title}</h1>
        <p className="mt-2 text-gray-400">{course.tagline}</p>
        <CourseMap
          modules={course.modules.map((m) => ({
            slug: m.slug,
            number: m.number,
            title: m.title,
            summary: m.summary,
            status: m.status,
            minutes: m.minutes,
            plannedLessons: m.plannedLessons,
            lessons: m.lessons.map((l) => ({ slug: l.slug, title: l.title, type: l.type, minutes: l.minutes })),
          }))}
        />
      </main>
    </div>
  );
}
