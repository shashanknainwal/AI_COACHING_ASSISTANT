import "server-only";
import fs from "node:fs";
import path from "node:path";
import matter from "gray-matter";
import { marked } from "marked";

const CONTENT_DIR = path.join(process.cwd(), "content");

export type LessonType = "reading" | "exercise" | "quiz";

export interface QuizQuestion {
  q: string;
  options: string[];
  answer: number;
  explain?: string;
}

export interface LessonMeta {
  slug: string;
  moduleSlug: string;
  title: string;
  type: LessonType;
  minutes: number;
}

export interface Lesson extends LessonMeta {
  html: string;
  hints: string[];
  questions: QuizQuestion[];
  starter: string;
  setup: string;
  tests: string;
}

export interface ModuleMeta {
  slug: string;
  number: number;
  title: string;
  summary: string;
  outcomes: string[];
  status: "live" | "coming-soon";
  plannedLessons: string[];
  lessons: LessonMeta[];
  minutes: number;
}

export interface Course {
  title: string;
  tagline: string;
  priceUsd: number;
  modules: ModuleMeta[];
}

interface CourseJson {
  title: string;
  tagline: string;
  priceUsd: number;
  modules: {
    slug: string;
    title: string;
    summary: string;
    outcomes: string[];
    plannedMinutes: number;
    plannedLessons: string[];
  }[];
}

function readIfExists(p: string): string {
  return fs.existsSync(p) ? fs.readFileSync(p, "utf8") : "";
}

function lessonFiles(moduleSlug: string): string[] {
  const dir = path.join(CONTENT_DIR, "modules", moduleSlug);
  if (!fs.existsSync(dir)) return [];
  return fs
    .readdirSync(dir)
    .filter((f) => f.endsWith(".md"))
    .sort();
}

function parseMeta(moduleSlug: string, file: string): { meta: LessonMeta; data: Record<string, unknown>; body: string } {
  const raw = fs.readFileSync(path.join(CONTENT_DIR, "modules", moduleSlug, file), "utf8");
  const { data, content } = matter(raw);
  const slug = file.replace(/\.md$/, "");
  return {
    meta: {
      slug,
      moduleSlug,
      title: String(data.title ?? slug),
      type: (data.type as LessonType) ?? "reading",
      minutes: Number(data.minutes ?? 10),
    },
    data,
    body: content,
  };
}

let courseCache: Course | null = null;

export function getCourse(): Course {
  if (courseCache && process.env.NODE_ENV === "production") return courseCache;
  const json = JSON.parse(fs.readFileSync(path.join(CONTENT_DIR, "course.json"), "utf8")) as CourseJson;
  const modules: ModuleMeta[] = json.modules.map((m, i) => {
    const lessons = lessonFiles(m.slug).map((f) => parseMeta(m.slug, f).meta);
    const live = lessons.length > 0;
    return {
      slug: m.slug,
      number: i + 1,
      title: m.title,
      summary: m.summary,
      outcomes: m.outcomes,
      status: live ? "live" : "coming-soon",
      plannedLessons: m.plannedLessons,
      lessons,
      minutes: live ? lessons.reduce((s, l) => s + l.minutes, 0) : m.plannedMinutes,
    };
  });
  courseCache = { title: json.title, tagline: json.tagline, priceUsd: json.priceUsd, modules };
  return courseCache;
}

export function getLesson(moduleSlug: string, lessonSlug: string): Lesson | null {
  const file = `${lessonSlug}.md`;
  if (!lessonFiles(moduleSlug).includes(file)) return null;
  const { meta, data, body } = parseMeta(moduleSlug, file);
  const exDir = path.join(CONTENT_DIR, "modules", moduleSlug, lessonSlug);
  return {
    ...meta,
    html: marked.parse(body, { async: false }) as string,
    hints: Array.isArray(data.hints) ? (data.hints as string[]) : [],
    questions: Array.isArray(data.questions) ? (data.questions as QuizQuestion[]) : [],
    starter: readIfExists(path.join(exDir, "starter.py")),
    setup: readIfExists(path.join(exDir, "setup.py")),
    tests: readIfExists(path.join(exDir, "tests.py")),
  };
}

/** Flat ordered list of every live lesson, for prev/next navigation. */
export function getLessonSequence(): LessonMeta[] {
  return getCourse().modules.flatMap((m) => m.lessons);
}
