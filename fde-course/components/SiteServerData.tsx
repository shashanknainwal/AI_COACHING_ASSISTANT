import "server-only";
// Server-side data builders for the site pages: the loop scorecards (content/weak-signals.json),
// graded-lesson and drill lists for the dashboard, modules for the onboarding plan, flashcards
// for /review and peer-mock scripts for /community. Everything here reads only public lesson
// fields; grader notes, persona briefs, constraints and anchors are never touched.

import weakSignals from "@/content/weak-signals.json";
import prices from "@/content/prices.json";
import { canAccessLesson, type Viewer } from "@/lib/access";
import { getCourse, getLesson, getModule, type LessonType } from "@/lib/content";
import type { DrillCfg, FixLink, GradedLessonCfg, LoopCfg, LoopRoundCfg, PlanModule, RoleTrack, SignalCfg } from "./SiteTypes";

const GRADED_TYPES = new Set<LessonType>(["written", "roleplay"]);
const HOT_TYPES = new Set<LessonType>(["exercise", "drill", "written", "roleplay"]);

export const lessonHref = (id: string) => `/learn/${id}`;

export function moduleHref(slug: string): string {
  const m = getModule(slug);
  return m ? `/learn?track=${m.track}#module-${m.number}` : "/learn";
}

function lessonTitle(id: string): string | null {
  const [m, l] = id.split("/");
  const mod = getModule(m);
  return mod?.lessons.find((x) => x.slug === l)?.title ?? null;
}

const shortTitle = (t: string) => t.replace(/^(Exercise|Drill|Write It|Written|Role-play|Live Practice):\s*/, "");

interface RawFix {
  lesson?: string;
  module?: string;
  note?: string;
}

function resolveFix(f: RawFix): FixLink | null {
  if (f.lesson) {
    const t = lessonTitle(f.lesson);
    if (!t) return null;
    const mod = getModule(f.lesson.split("/")[0])!;
    return { label: `${mod.code} · ${shortTitle(t)}`, href: lessonHref(f.lesson), note: f.note };
  }
  if (f.module) {
    const mod = getModule(f.module);
    if (!mod) return null;
    return { label: `${mod.code} · ${mod.title}`, href: moduleHref(f.module), note: f.note };
  }
  return null;
}

/** Loop scorecards for the tracks the site currently shows. */
export function getLoopConfigs(): LoopCfg[] {
  const out: LoopCfg[] = [];
  for (const t of weakSignals.tracks) {
    const mod = getModule(t.loopModule);
    if (!mod) continue; // track not visible (e.g. before TRACKS_LIVE)
    const rounds: LoopRoundCfg[] = [];
    for (const r of t.rounds as { key: string; label: string; kind: string; optional?: boolean; lessons: string[]; weights?: number[] }[]) {
      if (r.kind !== "drill" && r.kind !== "graded" && r.kind !== "combo") continue;
      const lessons = r.lessons.flatMap((id) => {
        const [m, l] = id.split("/");
        const lesson = getLesson(m, l);
        if (!lesson) return [];
        return [{ id, title: shortTitle(lesson.title), href: lessonHref(id), levels: lesson.levels.length || undefined, timeLimit: lesson.timeLimit || undefined }];
      });
      if (lessons.length !== r.lessons.length) continue;
      rounds.push({ key: r.key, label: r.label, kind: r.kind, optional: Boolean(r.optional), lessons, weights: r.weights });
    }
    const signals: SignalCfg[] = (t.signals as (Omit<SignalCfg, "fix"> & { fix: RawFix[] })[]).map((s) => ({
      ...s,
      fix: s.fix.map(resolveFix).filter((x): x is FixLink => x !== null),
    }));
    const [sm, sl] = t.scorecardLesson.split("/");
    const scorecard = getLesson(sm, sl);
    out.push({
      track: t.track as RoleTrack,
      title: t.title,
      loopModule: t.loopModule,
      firstLessonHref: mod.lessons[0] ? lessonHref(`${mod.slug}/${mod.lessons[0].slug}`) : moduleHref(mod.slug),
      scorecard: { title: scorecard?.title ?? "Scorecard lesson", href: lessonHref(t.scorecardLesson) },
      rounds,
      signals,
    });
  }
  return out;
}

export function getGradedLessons(): GradedLessonCfg[] {
  return getCourse().modules.flatMap((m) =>
    m.lessons
      .filter((l) => GRADED_TYPES.has(l.type))
      .map((l) => ({ id: `${m.slug}/${l.slug}`, title: shortTitle(l.title), href: lessonHref(`${m.slug}/${l.slug}`), track: m.track, moduleLabel: m.code })),
  );
}

export function getDrills(): DrillCfg[] {
  return getCourse().modules.flatMap((m) =>
    m.lessons
      .filter((l) => l.type === "drill")
      .flatMap((l) => {
        const lesson = getLesson(m.slug, l.slug);
        if (!lesson) return [];
        return [{ id: `${m.slug}/${l.slug}`, title: shortTitle(l.title), href: lessonHref(`${m.slug}/${l.slug}`), levels: lesson.levels.length, timeLimit: lesson.timeLimit }];
      }),
  );
}

export function getPlanModules(): PlanModule[] {
  return getCourse()
    .modules.filter((m) => m.status === "live")
    .map((m) => ({
      slug: m.slug,
      track: m.track,
      code: m.code,
      title: m.title,
      minutes: m.minutes,
      gradedMinutes: m.lessons.filter((l) => HOT_TYPES.has(l.type)).reduce((s, l) => s + l.minutes, 0),
      href: moduleHref(m.slug),
    }));
}

// ---------------------------------------------------------------- flashcards

export interface ReviewCard {
  id: string;
  kind: "quiz" | "number";
  deck: string;
  front: string;
  back: string;
  explain?: string;
  href?: string;
}

/** Stable short id for a card (FNV-1a over its source). */
function cardId(s: string): string {
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return (h >>> 0).toString(36);
}

const usd = (n: number) => `$${n < 1 ? n.toFixed(2) : Number.isInteger(n) ? n : n.toFixed(2)}`;

export function getNumberCards(): ReviewCard[] {
  const cards: ReviewCard[] = [];
  const add = (key: string, front: string, back: string, explain?: string) => cards.push({ id: `n-${key}`, kind: "number", deck: "Numbers", front, back, explain });
  for (const m of prices.models) {
    add(`${m.id}-io`, `${m.name}: price per million input / output tokens?`, `${usd(m.input)} / ${usd(m.output)}`, "note" in m && m.note ? `Prices ${m.note}.` : undefined);
    if ("cacheRead" in m && typeof m.cacheRead === "number") {
      add(`${m.id}-cache`, `${m.name}: price of a cache read per million tokens?`, usd(m.cacheRead), `That is ${Math.round((m.cacheRead / m.input) * 1000) / 10}% of the ${usd(m.input)} input price.`);
    }
    if ("effortDefault" in m && m.effortDefault) add(`${m.id}-effort`, `${m.name}: default effort level?`, m.effortDefault, "Thinking is billed as output, so set effort explicitly in cost estimates.");
  }
  add("batch", "Message Batches discount?", `${Math.round(prices.batchDiscount * 100)}% off input and output`, "Batches isn't available on Bedrock, Vertex or Foundry.");
  add("cache-write-5m", "Prompt-cache write cost, 5-minute TTL?", `${prices.cacheWrite.fiveMinute}× the input price`);
  add("cache-write-1h", "Prompt-cache write cost, 1-hour TTL?", `${prices.cacheWrite.oneHour}× the input price`);
  add("cache-min", "Minimum cacheable prompt length on the current models?", `${prices.cacheMinimumTokens} tokens`);
  add("cache-ttl", "Default prompt-cache lifetime, and the longer option?", `${prices.cacheTtl.default}; ${prices.cacheTtl.option} as an option`);
  const sonnet = prices.models.find((m) => m.id === "claude-sonnet-5-5");
  if (sonnet) {
    const cost = (10_000 * sonnet.input + 500 * sonnet.output) / 1_000_000;
    add("sonnet-math", "Sonnet 5.5: 10,000 input + 500 output tokens costs?", `$${cost.toFixed(3)} per request`, `10,000 × ${usd(sonnet.input)}/1M + 500 × ${usd(sonnet.output)}/1M. Thinking tokens bill as output, so the real output may be larger.`);
  }
  return cards;
}

/** Quiz questions the viewer can open, as cards: question → correct option + explanation. */
export function getQuizCards(viewer: Viewer): ReviewCard[] {
  const cards: ReviewCard[] = [];
  for (const m of getCourse().modules) {
    for (const l of m.lessons) {
      if (l.type !== "quiz" || !canAccessLesson(viewer, m.slug, l.slug)) continue;
      const lesson = getLesson(m.slug, l.slug);
      if (!lesson) continue;
      lesson.questions.forEach((q, i) => {
        const answer = q.options[q.answer];
        if (!answer) return;
        cards.push({
          id: `q-${cardId(`${m.slug}/${l.slug}#${i}#${q.q}`)}`,
          kind: "quiz",
          deck: m.code,
          front: q.q,
          back: answer,
          explain: q.explain,
          href: lessonHref(`${m.slug}/${l.slug}`),
        });
      });
    }
  }
  return cards;
}

// ---------------------------------------------------------------- peer mocks

export interface PeerScript {
  id: string;
  track: string;
  moduleCode: string;
  title: string;
  minutes: number;
  timeLimit: number;
  maxTurns: number;
  design: boolean;
  persona: { name: string; role: string; company: string } | null;
  opening: string;
  /** The lesson's own text, as the learner sees it (plain text, no grader material). */
  setup: string;
  rubric: { name: string; points: number; lookFor: string }[];
  passScore: number;
  free: boolean;
}

function htmlToText(html: string): string {
  return html
    .replace(/<\/(p|li|h[1-6]|blockquote|tr)>/g, "\n")
    .replace(/<br\s*\/?>/g, "\n")
    .replace(/<[^>]+>/g, "")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

/** Role-play lessons the viewer can open, as interviewer scripts built from public fields only. */
export function getPeerScripts(viewer: Viewer, freeIds: Set<string>): PeerScript[] {
  const out: PeerScript[] = [];
  for (const m of getCourse().modules) {
    for (const l of m.lessons) {
      if (l.type !== "roleplay") continue;
      const id = `${m.slug}/${l.slug}`;
      if (!canAccessLesson(viewer, m.slug, l.slug)) continue;
      const lesson = getLesson(m.slug, l.slug);
      if (!lesson) continue;
      out.push({
        id,
        track: m.track,
        moduleCode: m.code,
        title: shortTitle(lesson.title),
        minutes: lesson.minutes,
        timeLimit: lesson.timeLimit,
        maxTurns: lesson.maxTurns,
        design: lesson.mode === "design",
        persona: lesson.persona ? { name: lesson.persona.name, role: lesson.persona.role, company: lesson.persona.company } : null,
        opening: lesson.opening,
        setup: htmlToText(lesson.html).slice(0, 6000),
        rubric: lesson.rubric.map((r) => ({ name: r.name, points: r.points, lookFor: r.lookFor })),
        passScore: lesson.passScore,
        free: freeIds.has(id),
      });
    }
  }
  return out;
}
