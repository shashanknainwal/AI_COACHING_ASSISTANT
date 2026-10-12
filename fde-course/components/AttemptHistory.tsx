"use client";

// Past attempts for one lesson. Grades (written answers, role-plays) show in the dark console pane;
// drill runs show on the paper page under the levels, with per-level clear times for the scorecard.

import { clock, type DrillRun, type GradeEntry } from "./practice-shared";

const when = (iso: string | number) => {
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? "" : d.toLocaleString(undefined, { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });
};

export function GradeHistory({ entries, server, title = "Attempt history" }: { entries: GradeEntry[]; server: boolean; title?: string }) {
  if (entries.length === 0) return null;
  const best = Math.max(...entries.map((e) => e.percent));
  return (
    <details className="mt-6 rounded-xl border border-console-line bg-console-2/40" open={entries.length <= 3}>
      <summary className="flex cursor-pointer list-none items-center gap-3 px-4 py-2.5 text-sm [&::-webkit-details-marker]:hidden">
        <span className="font-mono text-[11px] uppercase tracking-wider text-gray-300">{title}</span>
        <span className="font-mono text-[11px] text-console-muted">
          {entries.length} attempt{entries.length === 1 ? "" : "s"} · best {best}%
        </span>
        <span className="ml-auto font-mono text-[11px] text-console-muted">{server ? "saved to your account" : "saved in this browser"}</span>
      </summary>
      <ol className="divide-y divide-console-line border-t border-console-line">
        {entries.map((e, i) => (
          <li key={e.id}>
            <details>
              <summary className="flex cursor-pointer list-none flex-wrap items-baseline gap-x-3 gap-y-1 px-4 py-2 text-sm hover:bg-console-2 [&::-webkit-details-marker]:hidden">
                <span className="font-mono text-xs text-console-muted">#{entries.length - i}</span>
                <span className={`font-mono text-sm font-semibold ${e.passed ? "text-emerald-300" : "text-amber-300"}`}>{e.percent}%</span>
                <span className="text-xs text-gray-300">{e.passed ? "Passed this rubric" : "Not yet"}</span>
                {e.loopMode && <span className="rounded bg-vermilion/20 px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wider text-orange-200">Loop score</span>}
                <span className="ml-auto font-mono text-[11px] text-console-muted">{when(e.createdAt)}</span>
              </summary>
              <div className="space-y-2 px-4 pb-3">
                {e.result.summary && <p className="text-[13px] leading-relaxed text-gray-300">{e.result.summary}</p>}
                <ul className="space-y-1">
                  {e.result.criteria.map((c) => (
                    <li key={c.name} className="flex items-baseline justify-between gap-3 text-[13px]">
                      <span className="text-gray-300">{c.name}</span>
                      <span className="shrink-0 font-mono text-xs text-console-muted">
                        {c.score} / {c.points}
                      </span>
                    </li>
                  ))}
                </ul>
                {e.result.fixFirst && (
                  <p className="text-[13px] leading-relaxed text-gray-300">
                    <span className="font-mono text-[11px] uppercase tracking-wider text-amber-300">Fix first · </span>
                    {e.result.fixFirst}
                  </p>
                )}
              </div>
            </details>
          </li>
        ))}
      </ol>
    </details>
  );
}

/** One run's per-level clear times; `limitMs` is the run's own limit (extended runs get 1.5×). */
export function LevelTimes({ run, levels }: { run: DrillRun; levels: number }) {
  const limitMs = run.timeLimitMin * 60_000 * (run.extended ? 1.5 : 1);
  return (
    <ol className="mt-3 grid gap-2 sm:grid-cols-2">
      {Array.from({ length: levels }, (_, i) => {
        const ms = run.levelMs[i];
        const inTime = ms !== undefined && (!limitMs || ms <= limitMs);
        return (
          <li key={i} className="flex items-baseline justify-between gap-3 rounded-lg border border-rule bg-white/60 px-3 py-2 text-sm">
            <span className="text-graphite-2">Level {i + 1}</span>
            <span className={`font-mono tabular-nums ${ms === undefined ? "text-graphite-3" : inTime ? "text-forest" : "text-vermilion"}`}>
              {ms === undefined ? "not cleared" : `${clock(ms)}${inTime ? "" : " (over time)"}`}
            </span>
          </li>
        );
      })}
    </ol>
  );
}

export function DrillHistory({ runs, levels, server }: { runs: DrillRun[]; levels: number; server: boolean }) {
  if (runs.length === 0) return null;
  return (
    <details className="mt-6 rounded-2xl border border-rule bg-white/50 p-5">
      <summary className="cursor-pointer font-serif text-lg font-semibold text-graphite">
        Past runs <span className="font-sans text-sm font-normal text-graphite-3">· {runs.length} · {server ? "saved to your account" : "saved in this browser"}</span>
      </summary>
      <div className="mt-3 overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-rule text-[11px] uppercase tracking-[0.12em] text-graphite-3">
              <th className="py-2 pr-3 font-semibold">Started</th>
              <th className="py-2 pr-3 font-semibold">Cleared</th>
              <th className="py-2 pr-3 font-semibold">In time</th>
              {Array.from({ length: levels }, (_, i) => (
                <th key={i} className="py-2 pr-3 font-semibold">
                  L{i + 1}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {runs.map((r) => (
              <tr key={r.startedAt} className="border-b border-rule/70 text-graphite-2">
                <td className="py-2 pr-3 whitespace-nowrap">
                  {when(r.startedAt)}
                  {r.extended && <span className="ml-1.5 rounded bg-paper-3 px-1 text-[10px] font-semibold text-graphite-2">1.5×</span>}
                  {r.loopMode && <span className="ml-1.5 rounded bg-vermilion/10 px-1 text-[10px] font-semibold text-vermilion">loop</span>}
                </td>
                <td className="py-2 pr-3 font-mono">
                  {r.cleared}/{levels}
                </td>
                <td className="py-2 pr-3 font-mono">{r.clearedInTime}</td>
                {Array.from({ length: levels }, (_, i) => (
                  <td key={i} className="py-2 pr-3 font-mono tabular-nums">
                    {r.levelMs[i] !== undefined ? clock(r.levelMs[i]) : "–"}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </details>
  );
}
