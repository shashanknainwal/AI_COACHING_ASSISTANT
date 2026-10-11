// Pure scoring for the progress dashboard and the public portfolio. Mirrors the method in each
// track's scorecard lesson: graded rounds use the loop-mode attempt (else the first attempt),
// drills score 25 points per level cleared in time and 10 per level cleared after the clock,
// combo rounds weight their lessons, a round passes at 70, and readiness is the weakest round.

import weakSignals from "@/content/weak-signals.json";
import type { FixLink, LoopCfg, LoopRoundCfg, SignalCfg } from "./SiteTypes";

export const PASS_MARK = weakSignals.passMark;
const PTS_IN = weakSignals.drillPoints.inTime;
const PTS_LATE = weakSignals.drillPoints.late;

export interface Criterion {
  name: string;
  points: number;
  score: number;
}

export interface GradeRec {
  lessonId: string;
  percent: number;
  passed: boolean;
  createdAt: string;
  loopMode: boolean;
  criteria: Criterion[];
}

export interface DrillRec {
  lessonId: string;
  startedAt: number;
  finishedAt: number | null;
  timeLimitMin: number;
  levelMs: number[];
  cleared: number;
  clearedInTime: number;
  loopMode: boolean;
}

export type Pattern = "stuck" | "edge" | "slow";

export interface RoundPart {
  title: string;
  href: string;
  score: number | null;
  source: "loop" | "first" | null;
  attempts: number;
  best: number | null;
}

export interface RoundResult {
  cfg: LoopRoundCfg;
  score: number | null;
  /** some but not all lessons of a combo round taken */
  partial: boolean;
  parts: RoundPart[];
  weakLines: (Criterion & { pct: number; lesson: string })[];
  drill?: { cleared: number; inTime: number; levels: number; marks: (number | null)[]; timeLimit: number; pattern: Pattern | null };
}

export type Verdict = "incomplete" | "ready" | "close" | "notyet" | "gap";

export const VERDICT_TEXT: Record<Verdict, { title: string; next: string }> = {
  incomplete: { title: "Not scored yet", next: "Take every required round to get a verdict. Readiness is judged by the weakest round, so one missing round means no verdict." },
  ready: { title: "Ready to schedule", next: "Every round is 70 or more. Run one more loop on fresh material a week before the real one." },
  close: { title: "Close", next: "One round is between 50 and 69. Spend two weeks on that round with the plan in the scorecard lesson." },
  notyet: { title: "Not yet", next: "Two or more rounds are between 50 and 69. Two weeks on the lower one, then a second cycle on the other." },
  gap: { title: "A gap, not a polish job", next: "A round is under 50. Go back to that round's modules first; plan on three to four weeks before the loop." },
};

export function status(score: number | null): "none" | "pass" | "close" | "gap" {
  if (score === null) return "none";
  if (score >= PASS_MARK) return "pass";
  return score >= 50 ? "close" : "gap";
}

export function drillScore(cleared: number, inTime: number): number {
  return Math.min(100, PTS_IN * inTime + PTS_LATE * Math.max(0, cleared - inTime));
}

export function drillPattern(cleared: number, inTime: number, levels: number): Pattern | null {
  if (cleared < 2) return "edge";
  if (cleared < levels) return "stuck";
  if (inTime < levels) return "slow";
  return null;
}

/** The attempt that counts for the loop: the loop-mode one, else the first. Lists are oldest first. */
function pick<T extends { loopMode: boolean }>(list: T[]): { rec: T; source: "loop" | "first" } | null {
  const loop = list.find((x) => x.loopMode);
  if (loop) return { rec: loop, source: "loop" };
  return list.length ? { rec: list[0], source: "first" } : null;
}

export function scoreRound(cfg: LoopRoundCfg, grades: Map<string, GradeRec[]>, drills: Map<string, DrillRec[]>): RoundResult {
  if (cfg.kind === "drill") {
    const lesson = cfg.lessons[0];
    const runs = drills.get(lesson.id) ?? [];
    const chosen = pick(runs);
    const levels = lesson.levels ?? 4;
    const part: RoundPart = { title: lesson.title, href: lesson.href, score: null, source: null, attempts: runs.length, best: null };
    if (!chosen) return { cfg, score: null, partial: false, parts: [part], weakLines: [] };
    const r = chosen.rec;
    const score = drillScore(r.cleared, r.clearedInTime);
    part.score = score;
    part.source = chosen.source;
    part.best = Math.max(...runs.map((x) => drillScore(x.cleared, x.clearedInTime)));
    const marks = Array.from({ length: levels }, (_, i) => (typeof r.levelMs[i] === "number" && i < r.cleared ? r.levelMs[i] : null));
    return {
      cfg,
      score,
      partial: false,
      parts: [part],
      weakLines: [],
      drill: { cleared: r.cleared, inTime: r.clearedInTime, levels, marks, timeLimit: r.timeLimitMin || lesson.timeLimit || 0, pattern: drillPattern(r.cleared, r.clearedInTime, levels) },
    };
  }

  const parts: RoundPart[] = [];
  const weakLines: RoundResult["weakLines"] = [];
  for (const lesson of cfg.lessons) {
    const list = grades.get(lesson.id) ?? [];
    const chosen = pick(list);
    parts.push({
      title: lesson.title,
      href: lesson.href,
      score: chosen ? chosen.rec.percent : null,
      source: chosen?.source ?? null,
      attempts: list.length,
      best: list.length ? Math.max(...list.map((g) => g.percent)) : null,
    });
    for (const c of chosen?.rec.criteria ?? []) {
      if (c.points > 0) weakLines.push({ ...c, pct: Math.round((c.score / c.points) * 100), lesson: lesson.title });
    }
  }
  weakLines.sort((a, b) => a.pct - b.pct);
  const taken = parts.filter((p) => p.score !== null);
  if (!taken.length) return { cfg, score: null, partial: false, parts, weakLines };
  if (taken.length < parts.length) return { cfg, score: null, partial: true, parts, weakLines };
  const weights = cfg.weights && cfg.weights.length === parts.length ? cfg.weights : parts.map(() => 1 / parts.length);
  const score = Math.round(parts.reduce((s, p, i) => s + (p.score ?? 0) * weights[i], 0));
  return { cfg, score, partial: false, parts, weakLines };
}

export interface LoopResult {
  rounds: RoundResult[];
  verdict: Verdict;
  weakest: RoundResult | null;
  scoredRequired: number;
  required: number;
  recommendations: { round: string; signal: SignalCfg; fix: FixLink[] }[];
}

export function scoreLoop(cfg: LoopCfg, grades: Map<string, GradeRec[]>, drills: Map<string, DrillRec[]>): LoopResult {
  const rounds = cfg.rounds.map((r) => scoreRound(r, grades, drills));
  const required = rounds.filter((r) => !r.cfg.optional);
  const counted = rounds.filter((r) => r.score !== null && (!r.cfg.optional || r.score !== null));
  const scoredRequired = required.filter((r) => r.score !== null).length;
  const weakest = counted.length ? counted.reduce((a, b) => ((b.score ?? 101) < (a.score ?? 101) ? b : a)) : null;

  let verdict: Verdict = "incomplete";
  if (scoredRequired === required.length && required.length) {
    const scores = counted.map((r) => r.score as number);
    if (scores.some((s) => s < 50)) verdict = "gap";
    else {
      const close = scores.filter((s) => s < PASS_MARK).length;
      verdict = close === 0 ? "ready" : close === 1 ? "close" : "notyet";
    }
  }

  // Next best modules: weak signals for every round under the pass mark, weakest round first.
  const recommendations: LoopResult["recommendations"] = [];
  const seen = new Set<string>();
  const weakRounds = counted.filter((r) => (r.score as number) < PASS_MARK).sort((a, b) => (a.score as number) - (b.score as number));
  for (const r of weakRounds) {
    const lines = r.weakLines.filter((l) => l.pct < PASS_MARK).map((l) => l.name.toLowerCase());
    const candidates = cfg.signals.filter((s) => s.rounds.includes(r.cfg.key));
    let matched = candidates.filter((s) => {
      if (s.drill) return s.drill === r.drill?.pattern;
      if (s.criteria) return lines.some((name) => s.criteria!.some((c) => name.includes(c)));
      return false;
    });
    if (!matched.length) matched = candidates.filter((s) => !s.drill && !s.criteria);
    if (!matched.length) matched = candidates.filter((s) => !s.drill).slice(0, 2);
    for (const s of matched) {
      if (seen.has(s.signal)) continue;
      seen.add(s.signal);
      recommendations.push({ round: r.cfg.label, signal: s, fix: s.fix });
    }
  }
  return { rounds, verdict, weakest, scoredRequired, required: required.length, recommendations: recommendations.slice(0, 6) };
}

// ---------------------------------------------------------------- rubric themes

const THEMES: [string, RegExp][] = [
  ["Evals and measurement", /eval|measur|baseline|success criteria|quality bar|faithful/],
  ["Cost, latency and numbers", /cost|latency|number|arithmetic|peaks|quantified|value/],
  ["Scoping and discovery", /scop|discovery|framing|asked for|listens|hidden|requirement|disputed/],
  ["Failure, security and risk", /failure|security|risk|safety|compliance|residency|injection|limits|identity/],
  ["Architecture and design", /architect|pipeline|design|topology|diagram|context|decision|model choice|approach|data plan|platform|use case|demo/],
  ["Ownership and stories", /owner|personal|specific|stor|example|role|self-aware|honest|learning|redo|result|situation|action|judg/],
  ["Communication and close", /concise|close|next step|ask|recommendation|leads with|communicat|people|clear|motivation|goals|overview|adapt|trust|prioriti/],
];

export function themeOf(name: string): string {
  const n = name.toLowerCase();
  return THEMES.find(([, re]) => re.test(n))?.[0] ?? "Other";
}

export const THEME_ORDER = [...THEMES.map(([t]) => t), "Other"];

/** Average score per theme across the latest attempt of every graded lesson. */
export function themeAverages(grades: Map<string, GradeRec[]>): { theme: string; pct: number; lines: number }[] {
  const acc = new Map<string, { got: number; max: number; lines: number }>();
  for (const list of grades.values()) {
    const latest = list[list.length - 1];
    for (const c of latest?.criteria ?? []) {
      if (!(c.points > 0)) continue;
      const t = themeOf(c.name);
      const a = acc.get(t) ?? { got: 0, max: 0, lines: 0 };
      a.got += Math.max(0, Math.min(c.score, c.points));
      a.max += c.points;
      a.lines++;
      acc.set(t, a);
    }
  }
  return THEME_ORDER.filter((t) => acc.has(t)).map((t) => {
    const a = acc.get(t)!;
    return { theme: t, pct: Math.round((a.got / a.max) * 100), lines: a.lines };
  });
}

export const mmss = (ms: number) => {
  const t = Math.max(0, Math.round(ms / 1000));
  return `${Math.floor(t / 60)}:${String(t % 60).padStart(2, "0")}`;
};
