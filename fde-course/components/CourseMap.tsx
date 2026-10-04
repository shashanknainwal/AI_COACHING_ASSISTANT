"use client";

import Link from "next/link";
import { useEffect } from "react";
import type { ClientViewer } from "@/lib/access";
import { enableServerSync, lessonId, resetProgress, useProgress } from "@/lib/progress";

interface MapModule {
  slug: string;
  number: number;
  title: string;
  summary: string;
  status: "live" | "coming-soon";
  minutes: number;
  locked: boolean;
  plannedLessons: string[];
  lessons: { slug: string; title: string; type: string; minutes: number }[];
}

const icon: Record<string, string> = { reading: "📖", exercise: "💻", quiz: "✅" };

export default function CourseMap({ modules, viewer }: { modules: MapModule[]; viewer: ClientViewer }) {
  const progress = useProgress();
  useEffect(() => {
    if (viewer.signedIn) void enableServerSync();
  }, [viewer.signedIn]);
  const all = modules.flatMap((m) => m.lessons.map((l) => lessonId(m.slug, l.slug)));
  const doneCount = all.filter((id) => progress.completed[id]).length;
  const pct = all.length ? Math.round((doneCount / all.length) * 100) : 0;
  const nextUp = modules
    .flatMap((m) => m.lessons.map((l) => ({ m, l })))
    .find(({ m, l }) => !progress.completed[lessonId(m.slug, l.slug)]);

  return (
    <>
      <div className="mt-8 rounded-xl border border-line bg-panel p-5">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-300">
            {doneCount} of {all.length} available lessons complete
          </span>
          <span className="font-semibold text-accent">{pct}%</span>
        </div>
        <div className="mt-2 h-2 overflow-hidden rounded bg-line">
          <div className="h-full bg-accent transition-all" style={{ width: `${pct}%` }} />
        </div>
        {nextUp && (
          <Link
            href={`/learn/${nextUp.m.slug}/${nextUp.l.slug}`}
            className="mt-4 inline-block rounded-lg bg-accent px-4 py-2 font-semibold text-ink hover:opacity-90"
          >
            {doneCount === 0 ? "Start the course" : "Continue"}: {nextUp.l.title} →
          </Link>
        )}
      </div>

      <ol className="mt-8 space-y-4">
        {modules.map((m) => {
          const done = m.lessons.filter((l) => progress.completed[lessonId(m.slug, l.slug)]).length;
          return (
            <li key={m.slug} className="rounded-xl border border-line bg-panel">
              <div className="p-5">
                <div className="flex items-baseline gap-3">
                  <span className="text-sm font-mono text-gray-500">{String(m.number).padStart(2, "0")}</span>
                  <h2 className="text-lg font-semibold text-white">{m.title}</h2>
                  {m.locked && m.status === "live" && <span title="Part of the full course">🔒</span>}
                  <span className="ml-auto shrink-0 text-xs text-gray-500">
                    {m.status === "live" ? `${done}/${m.lessons.length} · ${m.minutes} min` : `Coming soon · ~${m.minutes} min`}
                  </span>
                </div>
                <p className="mt-1 pl-9 text-sm text-gray-400">{m.summary}</p>
              </div>
              {m.status === "live" ? (
                <ul className="border-t border-line">
                  {m.lessons.map((l) => {
                    const complete = Boolean(progress.completed[lessonId(m.slug, l.slug)]);
                    return (
                      <li key={l.slug}>
                        <Link
                          href={`/learn/${m.slug}/${l.slug}`}
                          className="flex items-center gap-3 px-5 py-2.5 pl-14 text-sm hover:bg-line/50"
                        >
                          <span>{icon[l.type] ?? "•"}</span>
                          <span className={complete ? "text-gray-400" : "text-gray-200"}>{l.title}</span>
                          <span className="ml-auto text-xs text-gray-500">{l.minutes} min</span>
                          <span className={`w-4 text-accent ${complete ? "" : "invisible"}`}>✓</span>
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              ) : (
                <ul className="border-t border-line px-5 py-3 pl-14 text-sm text-gray-500">
                  {m.plannedLessons.map((t) => (
                    <li key={t} className="py-0.5">
                      {t}
                    </li>
                  ))}
                </ul>
              )}
            </li>
          );
        })}
      </ol>

      {!viewer.signedIn && (
        <button
          onClick={() => confirm("Reset all progress and saved code in this browser?") && resetProgress()}
          className="mt-10 text-xs text-gray-600 hover:text-gray-400"
        >
          Reset my progress
        </button>
      )}
    </>
  );
}
