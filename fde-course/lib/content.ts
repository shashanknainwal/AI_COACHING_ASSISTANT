import "server-only";
import fs from "node:fs";
import path from "node:path";
import matter from "gray-matter";
import { marked } from "marked";
import { priceUsd, tracksEnabled } from "./config";

const CONTENT_DIR = path.join(process.cwd(), "content");

/**
 * reading   prose, optional scratchpad code
 * exercise  Python graded by hidden tests
 * quiz      multiple choice
 * drill     timed, multi-level Python problem; level N+1 unlocks when level N's tests pass
 * written   text answer graded by Claude against a rubric (also used for design answers)
 * roleplay  a conversation with a Claude persona, then a rubric-graded debrief
 */
export type LessonType = "reading" | "exercise" | "quiz" | "drill" | "written" | "roleplay";

export const LESSON_TYPES: LessonType[] = ["reading", "exercise", "quiz", "drill", "written", "roleplay"];

/** Lesson types the learner completes in the editor and that are graded by Python tests. */
export const CODED_TYPES = new Set<LessonType>(["exercise", "drill"]);

export interface QuizQuestion {
  q: string;
  options: string[];
  answer: number;
  explain?: string;
}

export interface RubricItem {
  name: string;
  points: number;
  lookFor: string;
}

export interface AnswerSection {
  key: string;
  label: string;
  prompt?: string;
  /** Suggested length as [min, max] words. */
  words?: [number, number];
}

export interface Persona {
  name: string;
  role: string;
  company: string;
}

export interface DrillLevel {
  title: string;
  html: string;
}

/** Role-play only: the server injects `text` into the persona's reply after learner turn `afterTurn`. Server-only. */
export interface DesignConstraint {
  afterTurn: number;
  text: string;
}

/**
 * Grader calibration answer (scripts/grader-eval.mjs). Server-only.
 * `answer` is a string (written lessons with one section, or a role-play conversation as text),
 * an object keyed by section key (written), or a list of transcript lines (role-play).
 */
export interface GraderAnchor {
  label: string;
  expect: [number, number];
  answer: string | Record<string, string> | { from: "persona" | "learner"; text: string }[];
}

export interface LessonMeta {
  slug: string;
  moduleSlug: string;
  title: string;
  type: LessonType;
  minutes: number;
}

export interface Customer {
  company: string;
  sector: string;
  contact: string;
  role: string;
  replies: string[];
}

export interface Lesson extends LessonMeta {
  /** Exercise intro shown as the customer's case file (empty for other lesson types). */
  briefHtml: string;
  html: string;
  hints: string[];
  questions: QuizQuestion[];
  starter: string;
  setup: string;
  tests: string;
  /** drill */
  levels: DrillLevel[];
  /** Minutes. Drills: the drill clock. Role-plays: the session clock (the server closes the session when it runs out). 0 = none. */
  timeLimit: number;
  /** written and roleplay */
  sections: AnswerSection[];
  rubric: RubricItem[];
  passScore: number;
  persona: Persona | null;
  opening: string;
  maxTurns: number;
  /** roleplay: "design" for an interactive design interview, else null */
  mode: "design" | null;
  /** roleplay, written: show a diagram box (text, Mermaid or ASCII) */
  diagram: boolean;
  /** roleplay, written: "module/lesson" ids whose saved work is given to the persona or grader as <learner_prior_work> */
  contextFrom: string[];
  /** Server-only: never send these to the browser (see toClientLesson). */
  graderNotes: string;
  personaBrief: string;
  constraints: DesignConstraint[];
  anchors: GraderAnchor[];
}

/** Fields of Lesson that must never reach the browser. */
export const SERVER_ONLY_LESSON_FIELDS = ["graderNotes", "personaBrief", "constraints", "anchors"] as const;

/** A Lesson without its server-only fields: safe to pass to client components. */
export type ClientLesson = Omit<Lesson, (typeof SERVER_ONLY_LESSON_FIELDS)[number]>;

/** Strips grader notes, persona brief, constraints and anchors. Use for every lesson object sent to the browser. */
export function toClientLesson(lesson: Lesson): ClientLesson {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { graderNotes, personaBrief, constraints, anchors, ...rest } = lesson;
  return rest;
}

export interface ModuleMeta {
  slug: string;
  /** Position within its track, from 1. */
  number: number;
  /** Short code shown on badges: "C1", "E3", or the number for the FDE track. */
  code: string;
  /** "C1" or "Module 3". */
  label: string;
  track: string;
  title: string;
  summary: string;
  outcomes: string[];
  status: "live" | "coming-soon";
  plannedLessons: string[];
  lessons: LessonMeta[];
  minutes: number;
  customer: Customer;
}

export interface TrackMeta {
  slug: string;
  title: string;
  short: string;
  summary: string;
  audience: string;
  /** Optional two-line headline for the track's map; "\n" splits the lines. */
  headline?: string;
  modules: string[];
}

export interface Course {
  title: string;
  tagline: string;
  priceUsd: number;
  tracks: TrackMeta[];
  modules: ModuleMeta[];
}

interface CourseJson {
  title: string;
  tagline: string;
  tracks: TrackMeta[];
  modules: {
    slug: string;
    code?: string;
    title: string;
    summary: string;
    outcomes: string[];
    plannedMinutes: number;
    plannedLessons: string[];
    customer: Customer;
  }[];
}

/** The original course. It is the only track shown while tracksEnabled() is false. */
export const FDE_TRACK = "fde";

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

let courseCache: { enabled: boolean; course: Course } | null = null;

export function getCourse(): Course {
  const enabled = tracksEnabled();
  if (courseCache && courseCache.enabled === enabled && process.env.NODE_ENV === "production") return courseCache.course;
  const json = JSON.parse(fs.readFileSync(path.join(CONTENT_DIR, "course.json"), "utf8")) as CourseJson;
  const tracks = enabled ? json.tracks : json.tracks.filter((t) => t.slug === FDE_TRACK);
  const modules: ModuleMeta[] = [];
  for (const track of tracks) {
    track.modules.forEach((slug, i) => {
      const m = json.modules.find((x) => x.slug === slug);
      if (!m) throw new Error(`course.json: track ${track.slug} lists unknown module ${slug}`);
      const lessons = lessonFiles(m.slug).map((f) => parseMeta(m.slug, f).meta);
      const live = lessons.length > 0;
      modules.push({
        slug: m.slug,
        number: i + 1,
        code: m.code ?? String(i + 1),
        label: m.code ?? `Module ${i + 1}`,
        track: track.slug,
        title: m.title,
        summary: m.summary,
        outcomes: m.outcomes,
        status: live ? "live" : "coming-soon",
        plannedLessons: m.plannedLessons,
        lessons,
        minutes: live ? lessons.reduce((s, l) => s + l.minutes, 0) : m.plannedMinutes,
        customer: m.customer,
      });
    });
  }
  const course = { title: json.title, tagline: json.tagline, priceUsd: priceUsd(), tracks, modules };
  courseCache = { enabled, course };
  return course;
}

export function getTrack(slug: string): TrackMeta | undefined {
  return getCourse().tracks.find((t) => t.slug === slug);
}

export function getModule(slug: string): ModuleMeta | undefined {
  return getCourse().modules.find((m) => m.slug === slug);
}

const list = <T,>(v: unknown): T[] => (Array.isArray(v) ? (v as T[]) : []);

export function getLesson(moduleSlug: string, lessonSlug: string): Lesson | null {
  // Modules outside the visible tracks don't exist as far as learners are concerned.
  if (!getModule(moduleSlug)) return null;
  const file = `${lessonSlug}.md`;
  if (!lessonFiles(moduleSlug).includes(file)) return null;
  const { meta, data, body } = parseMeta(moduleSlug, file);
  const exDir = path.join(CONTENT_DIR, "modules", moduleSlug, lessonSlug);
  let html = decorate(marked.parse(body, { async: false }) as string);

  // An exercise's opening paragraphs (before its first heading) are the customer's brief.
  const cut = meta.type === "exercise" ? html.indexOf("<h2") : -1;
  const briefHtml = cut > 0 ? html.slice(0, cut) : "";
  if (cut > 0) html = html.slice(cut);

  // A drill's "## Level N: ..." sections are revealed one at a time.
  const levels: DrillLevel[] = [];
  if (meta.type === "drill") {
    const parts = html.split(/(?=<h2[^>]*>\s*Level\s+\d)/);
    html = parts[0];
    const titles = list<string>(data.levels);
    parts.slice(1).forEach((part, i) => levels.push({ title: titles[i] ?? `Level ${i + 1}`, html: part }));
  }

  const sections = list<AnswerSection>(data.sections);
  return {
    ...meta,
    briefHtml,
    html,
    hints: list<string>(data.hints),
    questions: list<QuizQuestion>(data.questions),
    starter: readIfExists(path.join(exDir, "starter.py")),
    setup: readIfExists(path.join(exDir, "setup.py")),
    tests: readIfExists(path.join(exDir, "tests.py")),
    levels,
    timeLimit: Number(data.timeLimit ?? 0),
    sections: sections.length ? sections : meta.type === "written" ? [{ key: "answer", label: "Your answer" }] : [],
    rubric: list<RubricItem>(data.rubric),
    passScore: Number(data.passScore ?? 70),
    persona: (data.persona as Persona) ?? null,
    opening: String(data.opening ?? ""),
    maxTurns: Number(data.maxTurns ?? 8),
    mode: data.mode === "design" ? "design" : null,
    diagram: data.diagram === true,
    contextFrom: list<unknown>(data.contextFrom).filter((x): x is string => typeof x === "string"),
    graderNotes: String(data.graderNotes ?? ""),
    personaBrief: String(data.personaBrief ?? ""),
    constraints: list<Record<string, unknown>>(data.constraints)
      .map((c) => ({ afterTurn: Number(c?.afterTurn), text: String(c?.text ?? "").trim() }))
      .filter((c) => Number.isInteger(c.afterTurn) && c.afterTurn > 0 && c.text),
    anchors: list<GraderAnchor>(data.anchors),
  };
}

/** Tag the recurring callouts so they can be styled: objectives, key takeaways and the instructor's "From my loop" notes. */
function decorate(html: string): string {
  return html.replace(/<blockquote>\s*<p><strong>(By the end of this lesson[^<]*|Key takeaways[^<]*|From my loop[^<]*)<\/strong>/g, (match, label: string) => {
    const kind = label.startsWith("Key") ? "takeaways" : label.startsWith("From my loop") ? "loop" : "objectives";
    return match.replace("<blockquote>", `<blockquote class="callout-${kind}">`);
  });
}

/** Ordered lessons of one track, for prev/next navigation. */
export function getLessonSequence(trackSlug: string): LessonMeta[] {
  return getCourse()
    .modules.filter((m) => m.track === trackSlug)
    .flatMap((m) => m.lessons);
}

/**
 * Lessons anyone can open without buying (besides FREE_MODULES): the first lesson of every
 * track, plus a taster of each graded format: the first C3 drill, the C5 mock values
 * interview, and the FDE customer-discovery field drill (found by type, not slug number).
 */
export function freeLessonIds(): Set<string> {
  const ids = new Set<string>();
  const course = getCourse();
  for (const t of course.tracks) {
    const first = course.modules.find((m) => m.track === t.slug && m.lessons.length > 0);
    if (first) ids.add(`${first.slug}/${first.lessons[0].slug}`);
  }
  const add = (moduleSlug: string, pick: (l: LessonMeta) => boolean) => {
    const lesson = course.modules.find((m) => m.slug === moduleSlug)?.lessons.find(pick);
    if (lesson) ids.add(`${moduleSlug}/${lesson.slug}`);
  };
  add("c3-progressive-coding", (l) => l.type === "drill");
  add("c5-values-and-behavioral", (l) => l.type === "roleplay" && l.slug.endsWith("mock-values-interview"));
  add("02-customer-discovery", (l) => l.type === "roleplay");
  return ids;
}
