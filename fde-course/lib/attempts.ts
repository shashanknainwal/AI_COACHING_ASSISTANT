import "server-only";
// Graded attempts (grade_attempts), drill attempts (drill_attempts) and the verified
// summaries built from them. Tables: supabase/migrations/0003_attempts.sql.
// Everything degrades to "nothing recorded" when Supabase isn't configured or a table is missing.
//
// Public helpers (for app/u/[handle]/page.tsx, the certificate and the dashboard):
//
//   getVerifiedSummary(userId: string): Promise<VerifiedSummary | null>
//     The learner's server-verified record. null in dev/unconfigured mode, without
//     SUPABASE_SECRET_KEY, or before 0003 is run. Call it only with a trusted user id
//     (from getViewer()); it reads with the secret key.
//
//   getPublicPortfolio(handle: string): Promise<PublicPortfolio | null>
//     The same summary for a public profile (profiles.handle, public_profile = true).
//     null when the handle doesn't exist, isn't public, or the tables are missing.
//
// VerifiedSummary:
//   passedRounds  AI-graded written/role-play lessons with at least one passing grade.
//                 Graded by the server, so these are verified.
//   drills        best drill attempt per lesson. Timings come from the browser and are
//                 recorded by the server (label them "timed in the browser").
//   loopScores    the first graded attempt of each mock-loop lesson taken in loop mode.
//   completions   every completed lesson. verified=true only for written/role-play lessons
//                 backed by a passing grade; verified=false means "self-reported by the browser"
//                 (code exercises are graded by tests that run in the learner's browser).
//
// Used by the API routes: recordGradeAttempt, listAttempts, recordDrillAttempt,
// passingLessonIds, loadPriorWork.

import type { Attempt, AttemptInfo, AttemptsResponse, DrillAttempt, DrillAttemptInput, GradeResult } from "@/lib/coach-types";
import { MOCK_LOOP_MODULES } from "@/lib/config";
import type { Viewer } from "@/lib/access";
import { getCourse, getLesson, type LessonType } from "@/lib/content";
import { escapeText } from "@/lib/grader";
import { createAdminClient, createClient } from "@/lib/supabase/server";

export const EMPTY_ATTEMPT: AttemptInfo = { id: null, n: 0, first: null, previous: null };

export interface VerifiedSummary {
  passedRounds: { lessonId: string; track: string | null; title: string; bestPercent: number; firstPassedAt: string; attempts: number }[];
  drills: {
    lessonId: string;
    title: string;
    levels: number;
    bestCleared: number;
    bestClearedInTime: number;
    /** Fastest attempt that cleared every level, in ms from start; null if never fully cleared. */
    fastestFullClearMs: number | null;
    attempts: number;
    lastAt: string;
  }[];
  loopScores: { lessonId: string; track: string | null; title: string; percent: number; passed: boolean; at: string }[];
  completions: { lessonId: string; title: string; type: LessonType | "unknown"; completedAt: string; verified: boolean }[];
}

export interface PublicPortfolio {
  handle: string;
  targetRole: string | null;
  summary: VerifiedSummary;
}

interface PgError {
  code?: string;
  message?: string;
}

/** True when the error means the table or function doesn't exist yet (migration not run). */
export function isMissingRelation(error: PgError | null | undefined): boolean {
  if (!error) return false;
  return error.code === "42P01" || error.code === "PGRST205" || error.code === "PGRST202" || /does not exist|could not find/i.test(error.message ?? "");
}

const isLoopModule = (moduleSlug: string) => (MOCK_LOOP_MODULES as readonly string[]).includes(moduleSlug);

function adminOrNull() {
  try {
    return createAdminClient();
  } catch {
    return null;
  }
}

/** Every lesson in course.json order (all tracks the site currently shows), by id. */
function lessonIndex(): Map<string, { title: string; type: LessonType; track: string; moduleSlug: string; levels?: number }> {
  const map = new Map<string, { title: string; type: LessonType; track: string; moduleSlug: string }>();
  for (const m of getCourse().modules) for (const l of m.lessons) map.set(`${m.slug}/${l.slug}`, { title: l.title, type: l.type, track: m.track, moduleSlug: m.slug });
  return map;
}

// ---------------------------------------------------------------- grade attempts

/**
 * Records a grade (never overwrites) and returns the attempt bookkeeping.
 * Only the first loop-mode attempt per mock-loop lesson is stored with loop_mode = true.
 */
export async function recordGradeAttempt(
  viewer: Viewer,
  lesson: { moduleSlug: string; slug: string },
  result: GradeResult,
  transcript: unknown,
  loopModeRequested: boolean,
): Promise<AttemptInfo> {
  if (viewer.mode !== "live" || !viewer.user) return EMPTY_ATTEMPT;
  const admin = adminOrNull();
  if (!admin) {
    console.error("recordGradeAttempt: SUPABASE_SECRET_KEY is not set; attempt not recorded");
    return EMPTY_ATTEMPT;
  }
  const lessonId = `${lesson.moduleSlug}/${lesson.slug}`;
  const prior = await admin
    .from("grade_attempts")
    .select("percent, passed, loop_mode")
    .eq("user_id", viewer.user.id)
    .eq("lesson_id", lessonId)
    .order("created_at", { ascending: true })
    .limit(1000);
  if (prior.error) {
    if (!isMissingRelation(prior.error)) console.error("recordGradeAttempt: lookup failed", prior.error.message);
    return EMPTY_ATTEMPT;
  }
  const rows = (prior.data ?? []) as { percent: number; passed: boolean; loop_mode: boolean }[];
  const loopMode = loopModeRequested && isLoopModule(lesson.moduleSlug) && !rows.some((r) => r.loop_mode);
  const track = getCourse().modules.find((m) => m.slug === lesson.moduleSlug)?.track ?? null;

  const inserted = await admin
    .from("grade_attempts")
    .insert({
      user_id: viewer.user.id,
      lesson_id: lessonId,
      track,
      percent: result.percent,
      passed: result.passed,
      result,
      transcript: transcript ?? null,
      loop_mode: loopMode,
    })
    .select("id")
    .single();
  if (inserted.error) {
    console.error("recordGradeAttempt: insert failed", inserted.error.message);
    return EMPTY_ATTEMPT;
  }
  return {
    id: Number(inserted.data.id),
    n: rows.length + 1,
    first: rows.length ? { percent: rows[0].percent, passed: rows[0].passed } : null,
    previous: rows.length ? { percent: rows[rows.length - 1].percent } : null,
  };
}

/**
 * This learner's attempts, newest first (RLS: own rows only). With a lesson id, the full
 * grade results; without, criteria only. null when attempts aren't available (→ { disabled: true }).
 */
export async function listAttempts(viewer: Viewer, lessonId?: string): Promise<AttemptsResponse | null> {
  if (viewer.mode !== "live" || !viewer.user) return null;
  const supabase = await createClient();
  let grades = supabase
    .from("grade_attempts")
    .select(lessonId ? "id, lesson_id, track, percent, passed, result, created_at, loop_mode" : "id, lesson_id, track, percent, passed, criteria:result->criteria, created_at, loop_mode")
    .eq("user_id", viewer.user.id)
    .order("created_at", { ascending: false })
    .limit(lessonId ? 200 : 2000);
  let drills = supabase
    .from("drill_attempts")
    .select("id, lesson_id, started_at, finished_at, time_limit_min, extended, level_ms, cleared, cleared_in_time, loop_mode")
    .eq("user_id", viewer.user.id)
    .order("started_at", { ascending: false })
    .limit(lessonId ? 200 : 2000);
  if (lessonId) {
    grades = grades.eq("lesson_id", lessonId);
    drills = drills.eq("lesson_id", lessonId);
  }
  const [g, d] = await Promise.all([grades, drills]);
  if (g.error || d.error) {
    const err = g.error ?? d.error;
    if (!isMissingRelation(err)) console.error("listAttempts failed", err?.message);
    return null;
  }
  const gradeRows = (g.data ?? []) as unknown as (Omit<Attempt, "result"> & { result?: Attempt["result"]; criteria?: Attempt["result"]["criteria"] })[];
  return {
    grades: gradeRows.map(({ criteria, result, ...row }) => ({
      ...row,
      result: result ?? { criteria: (criteria ?? []).map((c) => ({ name: c.name, points: c.points, score: c.score })) },
    })),
    drills: (d.data ?? []) as DrillAttempt[],
  };
}

/** Lesson ids (from `lessonIds`) with at least one passing grade, or null if grade_attempts doesn't exist. */
export async function passingLessonIds(userId: string, lessonIds: string[]): Promise<Set<string> | null> {
  if (!lessonIds.length) return new Set();
  const supabase = await createClient();
  const { data, error } = await supabase
    .from("grade_attempts")
    .select("lesson_id")
    .eq("user_id", userId)
    .eq("passed", true)
    .in("lesson_id", lessonIds);
  if (error) {
    if (!isMissingRelation(error)) console.error("passingLessonIds failed", error.message);
    return null;
  }
  return new Set((data ?? []).map((r: { lesson_id: string }) => r.lesson_id));
}

// ---------------------------------------------------------------- drill attempts

const MAX_LEVELS = 20;

/** Validates and inserts a drill attempt with the secret key. Returns "disabled", "ok" or an error message. */
export async function recordDrillAttempt(viewer: Viewer, input: DrillAttemptInput, levelCount: number): Promise<"ok" | "disabled" | { error: string }> {
  if (viewer.mode !== "live" || !viewer.user) return "disabled";
  const started = Date.parse(String(input.startedAt));
  const finished = input.finishedAt ? Date.parse(String(input.finishedAt)) : null;
  const now = Date.now();
  if (!Number.isFinite(started) || started > now + 60_000 || started < now - 7 * 24 * 3600_000) return { error: "Invalid startedAt" };
  if (finished !== null && (!Number.isFinite(finished) || finished < started || finished > now + 60_000)) return { error: "Invalid finishedAt" };
  const int = (v: unknown, max: number) => (Number.isInteger(v) && (v as number) >= 0 && (v as number) <= max ? (v as number) : null);
  const timeLimitMin = int(input.timeLimitMin, 24 * 60);
  const levels = Math.min(levelCount || MAX_LEVELS, MAX_LEVELS);
  const cleared = int(input.cleared, levels);
  const clearedInTime = int(input.clearedInTime, levels);
  const levelMs = Array.isArray(input.levelMs) ? input.levelMs : [];
  if (timeLimitMin === null || cleared === null || clearedInTime === null || clearedInTime > cleared) return { error: "Invalid drill result" };
  if (levelMs.length > levels || !levelMs.every((ms) => int(ms, 7 * 24 * 3600_000) !== null)) return { error: "Invalid levelMs" };

  const admin = adminOrNull();
  if (!admin) return "disabled";
  const lessonId = String(input.lesson);
  const moduleSlug = lessonId.split("/")[0];
  let loopMode = false;
  if (input.loopMode === true && isLoopModule(moduleSlug)) {
    const prior = await admin.from("drill_attempts").select("id").eq("user_id", viewer.user.id).eq("lesson_id", lessonId).eq("loop_mode", true).limit(1);
    if (prior.error) return isMissingRelation(prior.error) ? "disabled" : { error: "Could not save the attempt" };
    loopMode = !(prior.data ?? []).length;
  }
  const { error } = await admin.from("drill_attempts").insert({
    user_id: viewer.user.id,
    lesson_id: lessonId,
    started_at: new Date(started).toISOString(),
    finished_at: finished === null ? null : new Date(finished).toISOString(),
    time_limit_min: timeLimitMin,
    extended: input.extended === true,
    level_ms: levelMs,
    cleared,
    cleared_in_time: clearedInTime,
    loop_mode: loopMode,
  });
  if (error) {
    if (isMissingRelation(error)) return "disabled";
    console.error("recordDrillAttempt: insert failed", error.message);
    return { error: "Could not save the attempt" };
  }
  return "ok";
}

// ---------------------------------------------------------------- contextFrom

interface SavedWork {
  answers?: Record<string, string>;
  transcript?: { from?: string; text?: string }[];
  diagram?: string;
}

const PRIOR_WORK_CHARS = 6_000;

function formatSaved(lessonId: string, saved: SavedWork | string): string {
  if (typeof saved === "string") return saved;
  const [m, l] = lessonId.split("/");
  const lesson = getLesson(m, l);
  const parts: string[] = [];
  if (saved.answers && typeof saved.answers === "object") {
    const labels = new Map((lesson?.sections ?? []).map((s) => [s.key, s.label]));
    for (const [key, text] of Object.entries(saved.answers)) if (String(text ?? "").trim()) parts.push(`${labels.get(key) ?? key}:\n${String(text).trim()}`);
  }
  if (Array.isArray(saved.transcript)) {
    const who = lesson?.persona?.name ?? "Interviewer";
    parts.push(saved.transcript.map((t) => `${t?.from === "persona" ? who : "Learner"}: ${String(t?.text ?? "")}`).join("\n"));
  }
  if (typeof saved.diagram === "string" && saved.diagram.trim()) parts.push(`Diagram:\n${saved.diagram.trim()}`);
  return parts.join("\n\n");
}

/**
 * The learner's saved work for a lesson's contextFrom lessons, as escaped <learner_prior_work>
 * blocks. Prefers the newest graded attempt's transcript, else lesson_progress.code. "" when none.
 */
export async function loadPriorWork(viewer: Viewer, lessonIds: string[]): Promise<string> {
  if (viewer.mode !== "live" || !viewer.user || !lessonIds.length) return "";
  const ids = lessonIds.slice(0, 5);
  const supabase = await createClient();
  const [progress, graded] = await Promise.all([
    supabase.from("lesson_progress").select("lesson_id, code").eq("user_id", viewer.user.id).in("lesson_id", ids),
    supabase.from("grade_attempts").select("lesson_id, transcript, created_at").eq("user_id", viewer.user.id).in("lesson_id", ids).order("created_at", { ascending: false }).limit(50),
  ]);
  const blocks: string[] = [];
  for (const id of ids) {
    let text = "";
    const g = graded.error ? undefined : (graded.data ?? []).find((r: { lesson_id: string; transcript: unknown }) => r.lesson_id === id && r.transcript);
    if (g) text = formatSaved(id, g.transcript as SavedWork);
    if (!text.trim()) {
      const p = progress.error ? undefined : (progress.data ?? []).find((r: { lesson_id: string; code: string | null }) => r.lesson_id === id);
      if (p?.code) {
        let saved: SavedWork | string = p.code;
        try {
          const parsed = JSON.parse(p.code);
          if (parsed && typeof parsed === "object") saved = parsed as SavedWork;
        } catch {
          // Plain code from an exercise.
        }
        text = formatSaved(id, saved);
      }
    }
    if (!text.trim()) continue;
    const [m, l] = id.split("/");
    const title = getLesson(m, l)?.title ?? id;
    blocks.push(`<learner_prior_work lesson="${escapeText(id)}" title="${escapeText(title).replace(/"/g, "&quot;")}">\n${escapeText(text.slice(0, PRIOR_WORK_CHARS))}\n</learner_prior_work>`);
  }
  return blocks.join("\n\n");
}

// ---------------------------------------------------------------- verified summaries

export async function getVerifiedSummary(userId: string): Promise<VerifiedSummary | null> {
  const admin = adminOrNull();
  if (!admin || !userId) return null;
  const [g, d, p] = await Promise.all([
    admin.from("grade_attempts").select("lesson_id, track, percent, passed, loop_mode, created_at").eq("user_id", userId).order("created_at", { ascending: true }).limit(5000),
    admin.from("drill_attempts").select("lesson_id, started_at, level_ms, cleared, cleared_in_time").eq("user_id", userId).order("started_at", { ascending: true }).limit(5000),
    admin.from("lesson_progress").select("lesson_id, completed_at").eq("user_id", userId).not("completed_at", "is", null).limit(5000),
  ]);
  if (g.error || d.error) {
    const err = g.error ?? d.error;
    if (!isMissingRelation(err)) console.error("getVerifiedSummary failed", err?.message);
    return null;
  }
  const index = lessonIndex();
  const titleOf = (id: string) => index.get(id)?.title ?? id;

  const grades = (g.data ?? []) as { lesson_id: string; track: string | null; percent: number; passed: boolean; loop_mode: boolean; created_at: string }[];
  const rounds = new Map<string, VerifiedSummary["passedRounds"][number]>();
  const attemptsPer = new Map<string, number>();
  for (const row of grades) attemptsPer.set(row.lesson_id, (attemptsPer.get(row.lesson_id) ?? 0) + 1);
  for (const row of grades) {
    if (!row.passed) continue;
    const cur = rounds.get(row.lesson_id);
    if (!cur) {
      rounds.set(row.lesson_id, { lessonId: row.lesson_id, track: row.track, title: titleOf(row.lesson_id), bestPercent: row.percent, firstPassedAt: row.created_at, attempts: attemptsPer.get(row.lesson_id) ?? 1 });
    } else cur.bestPercent = Math.max(cur.bestPercent, row.percent);
  }
  const loopScores = grades
    .filter((r) => r.loop_mode)
    .map((r) => ({ lessonId: r.lesson_id, track: r.track, title: titleOf(r.lesson_id), percent: r.percent, passed: r.passed, at: r.created_at }));

  const drillsByLesson = new Map<string, VerifiedSummary["drills"][number]>();
  for (const row of (d.data ?? []) as { lesson_id: string; started_at: string; level_ms: number[] | null; cleared: number; cleared_in_time: number }[]) {
    const [m, l] = row.lesson_id.split("/");
    const levels = getLesson(m, l)?.levels.length ?? row.cleared;
    const cur =
      drillsByLesson.get(row.lesson_id) ??
      { lessonId: row.lesson_id, title: titleOf(row.lesson_id), levels, bestCleared: 0, bestClearedInTime: 0, fastestFullClearMs: null, attempts: 0, lastAt: row.started_at };
    cur.attempts++;
    cur.lastAt = row.started_at;
    cur.bestCleared = Math.max(cur.bestCleared, row.cleared);
    cur.bestClearedInTime = Math.max(cur.bestClearedInTime, row.cleared_in_time);
    const ms = row.level_ms ?? [];
    if (levels > 0 && row.cleared >= levels && ms.length >= levels) {
      const total = ms[levels - 1];
      cur.fastestFullClearMs = cur.fastestFullClearMs === null ? total : Math.min(cur.fastestFullClearMs, total);
    }
    drillsByLesson.set(row.lesson_id, cur);
  }

  const completions = p.error
    ? []
    : ((p.data ?? []) as { lesson_id: string; completed_at: string }[]).map((r) => {
        const meta = index.get(r.lesson_id);
        const graded = meta?.type === "written" || meta?.type === "roleplay";
        return {
          lessonId: r.lesson_id,
          title: titleOf(r.lesson_id),
          type: meta?.type ?? ("unknown" as const),
          completedAt: r.completed_at,
          verified: graded && rounds.has(r.lesson_id),
        };
      });

  return { passedRounds: [...rounds.values()], drills: [...drillsByLesson.values()], loopScores, completions };
}

export async function getPublicPortfolio(handle: string): Promise<PublicPortfolio | null> {
  const h = String(handle ?? "").toLowerCase();
  if (!/^[a-z0-9-]{3,30}$/.test(h)) return null;
  const admin = adminOrNull();
  if (!admin) return null;
  const { data, error } = await admin.from("profiles").select("user_id, handle, target_role").eq("handle", h).eq("public_profile", true).maybeSingle();
  if (error) {
    if (!isMissingRelation(error)) console.error("getPublicPortfolio failed", error.message);
    return null;
  }
  if (!data) return null;
  const summary = await getVerifiedSummary(String(data.user_id));
  if (!summary) return null;
  return { handle: String(data.handle), targetRole: (data.target_role as string | null) ?? null, summary };
}
