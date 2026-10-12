"use client";

// The progress dashboard: loop scorecards per track, rubric-line averages, attempt counts,
// drill level times and "next best module". Attempts come from GET /api/attempts; when the server
// isn't recording them (dev mode, signed out, table missing), from this browser's copies.

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import type { Attempt, DrillAttempt } from "@/lib/coach-types";
import { localDrillRuns, localGrades } from "./practice-shared";
import { countdownText, daysUntil, useProfile } from "./SiteProfile";
import { ROLE_LABEL, type DrillCfg, type GradedLessonCfg, type LoopCfg, type RoleTrack } from "./SiteTypes";
import { PASS_MARK, VERDICT_TEXT, mmss, scoreLoop, status, themeAverages, type DrillRec, type GradeRec, type RoundResult } from "./DashboardScore";
import DashboardLoopStart from "./DashboardLoopStart";
import DashboardOutcome from "./DashboardOutcome";
import DashboardSettings from "./DashboardSettings";

type Source = "loading" | "server" | "local";

function group<T extends { lessonId: string }>(list: T[], key: (x: T) => number): Map<string, T[]> {
  const m = new Map<string, T[]>();
  for (const x of list) m.set(x.lessonId, [...(m.get(x.lessonId) ?? []), x]);
  for (const v of m.values()) v.sort((a, b) => key(a) - key(b));
  return m;
}

function fromServerGrade(a: Attempt): GradeRec {
  return {
    lessonId: a.lesson_id,
    percent: a.percent,
    passed: a.passed,
    createdAt: a.created_at,
    loopMode: a.loop_mode,
    criteria: (a.result?.criteria ?? []).map((c) => ({ name: c.name, points: Number(c.points) || 0, score: Number(c.score) || 0 })),
  };
}

function fromServerDrill(d: DrillAttempt): DrillRec {
  return {
    lessonId: d.lesson_id,
    startedAt: Date.parse(d.started_at),
    finishedAt: d.finished_at ? Date.parse(d.finished_at) : null,
    timeLimitMin: d.time_limit_min,
    levelMs: d.level_ms ?? [],
    cleared: d.cleared,
    clearedInTime: d.cleared_in_time,
    loopMode: d.loop_mode,
  };
}

function useAttempts(graded: GradedLessonCfg[], drills: DrillCfg[]) {
  const [state, setState] = useState<{ source: Source; grades: GradeRec[]; drills: DrillRec[] }>({ source: "loading", grades: [], drills: [] });
  useEffect(() => {
    let live = true;
    (async () => {
      try {
        const res = await fetch("/api/attempts", { cache: "no-store" });
        if (res.ok) {
          const data = (await res.json()) as { disabled?: boolean; grades?: Attempt[]; drills?: DrillAttempt[] };
          if (!data.disabled && Array.isArray(data.grades) && Array.isArray(data.drills)) {
            if (live) setState({ source: "server", grades: data.grades.map(fromServerGrade), drills: data.drills.map(fromServerDrill) });
            return;
          }
        }
      } catch {
        // Fall back to this browser's copies.
      }
      const g: GradeRec[] = graded.flatMap((l) =>
        localGrades(l.id).map((e) => ({
          lessonId: l.id,
          percent: e.percent,
          passed: e.passed,
          createdAt: e.createdAt,
          loopMode: e.loopMode,
          criteria: (e.result?.criteria ?? []).map((c) => ({ name: c.name, points: Number(c.points) || 0, score: Number(c.score) || 0 })),
        })),
      );
      const d: DrillRec[] = drills.flatMap((l) => localDrillRuns(l.id).map((r) => ({ lessonId: l.id, ...r })));
      if (live) setState({ source: "local", grades: g, drills: d });
    })();
    return () => {
      live = false;
    };
  }, [graded, drills]);
  return state;
}

const STATUS_STYLE = {
  none: ["Not taken", "border border-rule text-graphite-3"],
  pass: ["Pass", "bg-forest text-white"],
  close: ["Close", "bg-amber-100 text-amber-900"],
  gap: ["Gap", "bg-vermilion text-white"],
} as const;

function StatusPill({ score, partial }: { score: number | null; partial?: boolean }) {
  const s = status(score);
  const [label, cls] = partial ? ["In progress", "border border-rule text-graphite-2"] : STATUS_STYLE[s];
  return <span className={`inline-block shrink-0 whitespace-nowrap rounded-full px-2 py-0.5 text-[11px] font-semibold ${cls}`}>{label}</span>;
}

function Bar({ pct, label }: { pct: number; label: string }) {
  const tone = pct >= PASS_MARK ? "bg-forest" : pct >= 50 ? "bg-amber-500" : "bg-vermilion";
  return (
    <div className="h-2.5 w-full overflow-hidden rounded-full bg-paper-3" role="img" aria-label={`${label}: ${pct}%`}>
      <div className={`h-full rounded-full ${tone}`} style={{ width: `${Math.max(2, Math.min(100, pct))}%` }} />
    </div>
  );
}

function RoundRow({ r }: { r: RoundResult }) {
  return (
    <li className="py-4">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
        <span className="min-w-0 flex-1 font-semibold text-graphite">{r.cfg.label}</span>
        <span className="font-mono text-lg font-semibold tabular-nums text-graphite">{r.score ?? "–"}</span>
        <StatusPill score={r.score} partial={r.partial} />
      </div>
      <ul className="mt-1.5 space-y-1 text-xs text-graphite-3">
        {r.parts.map((p) => (
          <li key={p.href} className="flex flex-wrap gap-x-2">
            <Link href={p.href} className="text-graphite-2 underline decoration-rule underline-offset-2 hover:text-graphite">
              {p.title}
            </Link>
            {p.score !== null ? (
              <span>
                {r.cfg.kind === "drill" ? `${p.score} pts` : `${p.score}%`} · {p.source === "loop" ? "loop score" : "first attempt"}
                {p.attempts > 1 && ` · best ${r.cfg.kind === "drill" ? `${p.best} pts` : `${p.best}%`} over ${p.attempts} attempts`}
              </span>
            ) : (
              <span>not taken yet</span>
            )}
          </li>
        ))}
      </ul>
      {r.drill && (
        <p className="mt-1.5 text-xs text-graphite-3">
          {r.drill.inTime} of {r.drill.levels} levels in time{r.drill.cleared > r.drill.inTime ? `, ${r.drill.cleared - r.drill.inTime} after` : ""}
          {r.drill.timeLimit ? ` · ${r.drill.timeLimit}-minute clock` : ""} · minute marks{" "}
          {r.drill.marks.map((m, i) => (
            <span key={i} className="font-mono">
              L{i + 1} {m === null ? "–" : mmss(m)}
              {i < r.drill!.marks.length - 1 ? "  " : ""}
            </span>
          ))}
        </p>
      )}
      {r.score !== null && r.weakLines[0] && r.score < PASS_MARK && (
        <p className="mt-1.5 text-xs text-graphite-2">
          Lowest rubric line: <span className="font-semibold">{r.weakLines[0].name}</span> ({r.weakLines[0].score}/{r.weakLines[0].points})
        </p>
      )}
    </li>
  );
}

export default function DashboardView({
  loops,
  graded,
  drills,
  signedIn,
  initialTrack,
}: {
  loops: LoopCfg[];
  graded: GradedLessonCfg[];
  drills: DrillCfg[];
  signedIn: boolean;
  initialTrack?: string;
}) {
  const attempts = useAttempts(graded, drills);
  const { profile } = useProfile();
  const [track, setTrack] = useState<string | null>(initialTrack && loops.some((l) => l.track === initialTrack) ? initialTrack : null);
  useEffect(() => {
    if (track === null && profile?.targetRole && loops.some((l) => l.track === profile.targetRole)) setTrack(profile.targetRole);
  }, [profile, loops, track]);
  const active = loops.find((l) => l.track === track) ?? loops[0];

  const gradesBy = useMemo(() => group(attempts.grades, (g) => Date.parse(g.createdAt)), [attempts.grades]);
  const drillsBy = useMemo(() => group(attempts.drills, (d) => d.startedAt), [attempts.drills]);
  const result = useMemo(() => (active ? scoreLoop(active, gradesBy, drillsBy) : null), [active, gradesBy, drillsBy]);
  const themes = useMemo(() => themeAverages(gradesBy), [gradesBy]);
  const titles = useMemo(() => new Map(graded.map((g) => [g.id, g])), [graded]);

  const lessonRows = useMemo(
    () =>
      [...gradesBy.entries()]
        .map(([id, list]) => ({
          id,
          meta: titles.get(id),
          attempts: list.length,
          first: list[0].percent,
          best: Math.max(...list.map((g) => g.percent)),
          latest: list[list.length - 1].percent,
          at: list[list.length - 1].createdAt,
        }))
        .sort((a, b) => b.at.localeCompare(a.at)),
    [gradesBy, titles],
  );
  const drillRows = drills
    .map((d) => {
      const runs = drillsBy.get(d.id) ?? [];
      const best = runs.reduce<DrillRec | null>((a, b) => (!a || b.cleared > a.cleared || (b.cleared === a.cleared && b.clearedInTime > a.clearedInTime) ? b : a), null);
      return { d, runs, best };
    })
    .filter((x) => x.runs.length);

  const days = daysUntil(profile?.interviewDate);
  const countdown = countdownText(days);

  return (
    <div className="space-y-10">
      <section className="flex flex-col gap-4 sm:flex-row sm:items-end">
        <div className="min-w-0 flex-1">
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-vermilion">Progress</p>
          <h1 className="mt-2 font-serif text-4xl font-semibold leading-tight tracking-[-0.02em] text-graphite">Your loop scorecard</h1>
          <p className="mt-2 max-w-2xl text-sm leading-relaxed text-graphite-2">
            Built automatically with the method from each track&apos;s scorecard lesson: the loop score (or first attempt) counts, drills score 25 points
            per level in time and 10 after, a round passes at {PASS_MARK}, and readiness is your weakest round.
          </p>
          <p className="mt-2 text-xs text-graphite-3" aria-live="polite">
            {attempts.source === "loading"
              ? "Loading your attempts…"
              : attempts.source === "server"
                ? "Attempts from your account."
                : "Attempts saved in this browser. Sign in to keep them on your account."}
          </p>
        </div>
        <div className="flex shrink-0 flex-col items-start gap-2 sm:items-end">
          {countdown ? (
            <p className="rounded-full bg-graphite px-4 py-1.5 text-sm font-semibold text-paper">{countdown}</p>
          ) : (
            <Link href="/start" className="rounded-full bg-graphite px-4 py-1.5 text-sm font-semibold text-paper hover:bg-black">
              Build my plan →
            </Link>
          )}
          {countdown && (
            <Link href="/start" className="text-xs font-semibold text-forest hover:underline">
              See my week-by-week plan
            </Link>
          )}
        </div>
      </section>

      {active && result ? (
        <section aria-labelledby="loop-title" className="rounded-3xl border border-rule bg-white/70 p-5 sm:p-6">
          {loops.length > 1 && (
            <div role="tablist" aria-label="Track" className="-mx-1 mb-5 flex gap-1 overflow-x-auto px-1 pb-1">
              {loops.map((l) => (
                <button
                  key={l.track}
                  role="tab"
                  type="button"
                  aria-selected={l.track === active.track}
                  onClick={() => setTrack(l.track)}
                  className={`shrink-0 whitespace-nowrap rounded-full px-3 py-1.5 text-sm ${l.track === active.track ? "bg-graphite text-paper" : "border border-rule text-graphite-2 hover:bg-paper-2"}`}
                >
                  {ROLE_LABEL[l.track]}
                </button>
              ))}
            </div>
          )}
          <div className="grid gap-6 lg:grid-cols-[1.35fr_1fr]">
            <div className="min-w-0">
              <h2 id="loop-title" className="font-serif text-2xl font-semibold text-graphite">
                {active.title}
              </h2>
              <ol className="mt-2 divide-y divide-rule">
                {result.rounds.map((r) => (
                  <RoundRow key={r.cfg.key} r={r} />
                ))}
              </ol>
              <p className="mt-2 text-xs text-graphite-3">
                Method and fix plan:{" "}
                <Link href={active.scorecard.href} className="font-semibold text-forest hover:underline">
                  {active.scorecard.title}
                </Link>
              </p>
            </div>
            <div className="min-w-0 space-y-5">
              <div className={`rounded-2xl p-5 ${result.verdict === "ready" ? "bg-forest text-white" : "bg-graphite text-paper"}`} aria-live="polite">
                <p className="font-mono text-[10px] uppercase tracking-[0.16em] opacity-80">Readiness · weakest round</p>
                <p className="mt-2 font-serif text-2xl leading-snug">{VERDICT_TEXT[result.verdict].title}</p>
                {result.weakest && (
                  <p className="mt-1 text-sm opacity-90">
                    Weakest so far: {result.weakest.cfg.label.replace(/^Round \S+ · /, "")} at {result.weakest.score}
                  </p>
                )}
                <p className="mt-3 text-sm opacity-90">{VERDICT_TEXT[result.verdict].next}</p>
                <p className="mt-3 text-xs opacity-75">
                  {result.scoredRequired} of {result.required} required rounds scored
                </p>
              </div>
              <DashboardLoopStart track={active.track as RoleTrack} firstLessonHref={active.firstLessonHref} />
              <div>
                <h3 className="font-serif text-lg font-semibold text-graphite">Next best modules</h3>
                {result.recommendations.length ? (
                  <ul className="mt-2 space-y-3 text-sm">
                    {result.recommendations.map((rec) => (
                      <li key={rec.signal.signal} className="rounded-2xl border border-rule bg-white p-3">
                        <p className="text-xs text-graphite-3">{rec.round}</p>
                        <p className="font-semibold text-graphite">{rec.signal.signal}</p>
                        <p className="text-xs text-graphite-3">Likely cause: {rec.signal.cause}</p>
                        <ul className="mt-1.5 space-y-0.5">
                          {rec.fix.map((f) => (
                            <li key={f.href + f.label}>
                              <Link href={f.href} className="font-semibold text-forest hover:underline">
                                {f.label}
                              </Link>
                              {f.note && <span className="text-graphite-3"> · {f.note}</span>}
                            </li>
                          ))}
                        </ul>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="mt-2 text-sm text-graphite-2">
                    {result.rounds.some((r) => r.score !== null)
                      ? "Every scored round is at or above the pass mark. Nothing to fix yet."
                      : "Take a round and your weak spots will map to the modules that fix them here."}
                  </p>
                )}
              </div>
            </div>
          </div>
        </section>
      ) : (
        <p className="rounded-2xl border border-rule bg-white/70 p-5 text-sm text-graphite-2">The mock loops open when the three role tracks launch.</p>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <section aria-labelledby="themes-title" className="min-w-0 rounded-3xl border border-rule bg-white/70 p-5 sm:p-6">
          <h2 id="themes-title" className="font-serif text-2xl font-semibold text-graphite">
            Rubric lines across all graded lessons
          </h2>
          <p className="mt-1 text-xs text-graphite-3">Your latest attempt on each written and live lesson, grouped by what the rubric line measures.</p>
          {themes.length ? (
            <ul className="mt-4 space-y-3">
              {themes.map((t) => (
                <li key={t.theme}>
                  <div className="flex items-baseline justify-between gap-3 text-sm">
                    <span className="text-graphite">{t.theme}</span>
                    <span className="shrink-0 font-mono tabular-nums text-graphite-2">
                      {t.pct}% <span className="text-xs text-graphite-3">({t.lines} lines)</span>
                    </span>
                  </div>
                  <div className="mt-1">
                    <Bar pct={t.pct} label={t.theme} />
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-4 text-sm text-graphite-2">No graded answers yet. Submit a written answer or finish a live session to see your rubric lines here.</p>
          )}
        </section>

        <section aria-labelledby="drills-title" className="min-w-0 rounded-3xl border border-rule bg-white/70 p-5 sm:p-6">
          <h2 id="drills-title" className="font-serif text-2xl font-semibold text-graphite">
            Drill level times
          </h2>
          <p className="mt-1 text-xs text-graphite-3">Your best run on each drill. Times are measured in your browser.</p>
          {drillRows.length ? (
            <ul className="mt-4 divide-y divide-rule text-sm">
              {drillRows.map(({ d, runs, best }) => (
                <li key={d.id} className="py-3">
                  <div className="flex flex-wrap items-baseline gap-x-2">
                    <Link href={d.href} className="min-w-0 flex-1 font-semibold text-graphite hover:underline">
                      {d.title}
                    </Link>
                    <span className="text-xs text-graphite-3">
                      {runs.length} attempt{runs.length === 1 ? "" : "s"} · {d.timeLimit} min clock
                    </span>
                  </div>
                  {best && (
                    <p className="mt-1 font-mono text-xs text-graphite-2">
                      {Array.from({ length: d.levels }, (_, i) => (
                        <span key={i} className="mr-3 inline-block">
                          L{i + 1} {i < best.cleared && typeof best.levelMs[i] === "number" ? mmss(best.levelMs[i]) : i < best.cleared ? "✓" : "–"}
                        </span>
                      ))}
                      <span className="inline-block text-graphite-3">
                        {best.clearedInTime}/{d.levels} in time
                      </span>
                    </p>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-4 text-sm text-graphite-2">No drill runs yet. Drills are timed, multi-level problems; your minute marks appear here.</p>
          )}
        </section>
      </div>

      <section aria-labelledby="attempts-title" className="rounded-3xl border border-rule bg-white/70 p-5 sm:p-6">
        <h2 id="attempts-title" className="font-serif text-2xl font-semibold text-graphite">
          Attempts by lesson
        </h2>
        {lessonRows.length ? (
          <div className="mt-4 overflow-x-auto">
            <table className="w-full min-w-[32rem] text-left text-sm">
              <thead className="text-xs uppercase tracking-wider text-graphite-3">
                <tr>
                  <th scope="col" className="py-2 pr-3 font-semibold">Lesson</th>
                  <th scope="col" className="px-2 py-2 text-right font-semibold">Attempts</th>
                  <th scope="col" className="px-2 py-2 text-right font-semibold">First</th>
                  <th scope="col" className="px-2 py-2 text-right font-semibold">Best</th>
                  <th scope="col" className="py-2 pl-2 text-right font-semibold">Latest</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-rule">
                {lessonRows.map((r) => (
                  <tr key={r.id}>
                    <td className="py-2 pr-3">
                      {r.meta ? (
                        <Link href={r.meta.href} className="text-graphite hover:underline">
                          <span className="mr-2 font-mono text-xs text-vermilion">{r.meta.moduleLabel}</span>
                          {r.meta.title}
                        </Link>
                      ) : (
                        <span className="text-graphite-3">{r.id}</span>
                      )}
                    </td>
                    <td className="px-2 py-2 text-right tabular-nums">{r.attempts}</td>
                    <td className="px-2 py-2 text-right tabular-nums">{r.first}%</td>
                    <td className="px-2 py-2 text-right tabular-nums">{r.best}%</td>
                    <td className="py-2 pl-2 text-right tabular-nums">{r.latest}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="mt-3 text-sm text-graphite-2">Nothing graded yet.</p>
        )}
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
        <section id="settings" aria-labelledby="settings-title" className="min-w-0 scroll-mt-24 rounded-3xl border border-rule bg-white/70 p-5 sm:p-6">
          <h2 id="settings-title" className="mb-1 font-serif text-2xl font-semibold text-graphite">
            Portfolio and reminders
          </h2>
          <p className="mb-4 text-xs text-graphite-3">A public page with your verified results and a certificate you can link from a résumé.</p>
          <DashboardSettings signedIn={signedIn} />
        </section>
        <section id="outcome" aria-label="Interview outcome" className="min-w-0 scroll-mt-24 rounded-3xl border border-rule bg-white/70 p-5 sm:p-6">
          <DashboardOutcome defaultTrack={active?.track} />
        </section>
      </div>
    </div>
  );
}
