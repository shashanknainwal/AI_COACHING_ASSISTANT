"use client";

import Link from "next/link";
import { useEffect } from "react";
import type { ClientViewer } from "@/lib/access";
import { enableServerSync, lessonId, resetProgress, useProgress } from "@/lib/progress";
import { Avatar, Ring } from "./Playbook";

interface MapModule {
  slug: string;
  number: number;
  code: string;
  label: string;
  title: string;
  summary: string;
  status: "live" | "coming-soon";
  minutes: number;
  locked: boolean;
  customer: { company: string; sector: string; contact: string; role: string };
  lessons: { slug: string; title: string; type: string; minutes: number }[];
}

const NUMBER_WORDS = ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve"];
const customerWord = (n: number) => NUMBER_WORDS[n] ?? String(n);

const shortTitle = (t: string) => t.replace(/^Exercise:\s*/, "");

const TYPE_MARK: Record<string, string> = { reading: "Read", exercise: "Task", quiz: "Quiz", drill: "Drill", written: "Write", roleplay: "Talk" };
const HOT_TYPES = new Set(["exercise", "drill", "written", "roleplay"]);

/** "3" -> "03"; codes like "C1" stay as they are. */
const badge = (code: string) => (/^\d+$/.test(code) ? code.padStart(2, "0") : code);

// Station positions on the route (viewBox 1000 x 230).
function stationPoints(n: number) {
  return Array.from({ length: n }, (_, i) => ({
    x: 95 + (i * 810) / Math.max(1, n - 1),
    y: i % 2 === 0 ? 150 : 72,
  }));
}

function routePath(pts: { x: number; y: number }[]) {
  return pts.reduce((d, p, i) => {
    if (i === 0) return `M ${p.x} ${p.y}`;
    const prev = pts[i - 1];
    const mid = (prev.x + p.x) / 2;
    return `${d} C ${mid} ${prev.y}, ${mid} ${p.y}, ${p.x} ${p.y}`;
  }, "");
}

export default function CourseMap({
  modules,
  viewer,
  eyebrow = "Your engagement map",
  headline,
  sectionTitle = "Engagements",
  taskLabel = "cases resolved",
}: {
  modules: MapModule[];
  viewer: ClientViewer;
  eyebrow?: string;
  /** Two lines separated by "\n". Defaults to "N customers. / One playbook." */
  headline?: string;
  sectionTitle?: string;
  /** Caption for the count of graded tasks (exercises, drills, written and live practice). */
  taskLabel?: string;
}) {
  const progress = useProgress();
  useEffect(() => {
    if (viewer.signedIn) void enableServerSync();
  }, [viewer.signedIn]);

  const isDone = (m: MapModule, slug: string) => Boolean(progress.completed[lessonId(m.slug, slug)]);
  const all = modules.flatMap((m) => m.lessons.map((l) => ({ m, l })));
  const doneCount = all.filter(({ m, l }) => isDone(m, l.slug)).length;
  const exercises = all.filter(({ l }) => HOT_TYPES.has(l.type));
  const resolved = exercises.filter(({ m, l }) => isDone(m, l.slug)).length;
  const minutesLeft = all.filter(({ m, l }) => !isDone(m, l.slug)).reduce((s, { l }) => s + l.minutes, 0);
  const pct = all.length ? doneCount / all.length : 0;
  const nextUp = all.find(({ m, l }) => !m.locked && !isDone(m, l.slug)) ?? all.find(({ m, l }) => !isDone(m, l.slug));

  const moduleProgress = (m: MapModule) => (m.lessons.length ? m.lessons.filter((l) => isDone(m, l.slug)).length / m.lessons.length : 0);
  const currentIdx = nextUp ? modules.findIndex((m) => m.slug === nextUp.m.slug) : modules.length;

  // Route progress: full segments for finished modules, partial for the current one.
  const routeFill = modules.length > 1 ? Math.min(1, (currentIdx + (nextUp ? moduleProgress(nextUp.m) : 0)) / (modules.length - 1)) : pct;
  const pts = stationPoints(modules.length);
  const d = routePath(pts);

  return (
    <>
      {/* Hero */}
      <section className="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-vermilion">{eyebrow}</p>
          <h1 className="mt-3 font-serif text-4xl font-semibold leading-[1.08] tracking-[-0.02em] text-graphite sm:text-5xl">
            {headline ? (
              headline.split("\n").map((line, i) => (
                <span key={i} className="block">
                  {line}
                </span>
              ))
            ) : (
              <>
                {customerWord(new Set(modules.map((m) => m.customer.company)).size)} customers.
                <br />
                One playbook.
              </>
            )}
          </h1>
          <dl className="mt-8 grid max-w-xl grid-cols-3 gap-3">
            {[
              [`${Math.round(pct * 100)}%`, "complete"],
              [`${resolved}/${exercises.length}`, taskLabel],
              [`${Math.round(minutesLeft / 60)}h`, "to go"],
            ].map(([n, l]) => (
              <div key={l} className="rounded-2xl border border-rule bg-white/60 px-4 py-3">
                <dt className="font-serif text-2xl font-semibold text-graphite">{n}</dt>
                <dd className="text-xs text-graphite-3">{l}</dd>
              </div>
            ))}
          </dl>
        </div>

        {nextUp ? (
          <Link
            href={`/learn/${nextUp.m.slug}/${nextUp.l.slug}`}
            className="group relative flex flex-col justify-between overflow-hidden rounded-3xl bg-graphite p-6 text-paper shadow-[0_30px_60px_-30px_rgba(29,27,22,0.8)]"
          >
            <div className="pointer-events-none absolute -right-16 -top-16 h-48 w-48 rounded-full bg-emerald-400/15 blur-2xl" />
            <div>
              <p className="font-mono text-[11px] uppercase tracking-[0.16em] text-emerald-300">{doneCount === 0 ? "Start here" : "Pick up where you left off"}</p>
              <p className="mt-3 text-xs text-paper-3">
                {nextUp.m.label} · {nextUp.m.customer.company}
              </p>
              <p className="mt-1 font-serif text-2xl leading-snug">{shortTitle(nextUp.l.title)}</p>
            </div>
            <div className="mt-6 flex items-center justify-between">
              <span className="flex items-center gap-2 text-sm text-paper-3">
                <Avatar name={nextUp.m.customer.contact} size="sm" dark />
                {nextUp.m.customer.contact} is waiting
              </span>
              <span className="rounded-full bg-emerald-400 px-4 py-2 text-sm font-semibold text-graphite transition group-hover:translate-x-1">
                {doneCount === 0 ? "Begin" : "Continue"} →
              </span>
            </div>
          </Link>
        ) : (
          <div className="flex flex-col justify-center rounded-3xl bg-forest p-6 text-white">
            <p className="font-serif text-2xl">Every engagement resolved.</p>
            <p className="mt-2 text-sm text-white/80">You&apos;ve completed the whole playbook. Congratulations.</p>
          </div>
        )}
      </section>

      {/* The route */}
      <section className="mt-12 hidden rounded-3xl border border-rule bg-white/50 px-4 pb-4 pt-2 md:block" aria-label="Course route">
        <svg viewBox="0 0 1000 230" className="w-full">
          <path d={d} fill="none" stroke="var(--color-rule)" strokeWidth="3" strokeDasharray="2 9" strokeLinecap="round" />
          <path
            d={d}
            fill="none"
            stroke="var(--color-forest)"
            strokeWidth="4"
            strokeLinecap="round"
            pathLength={1}
            strokeDasharray={`${routeFill} 1`}
            style={{ transition: "stroke-dasharray 1s ease-out" }}
          />
          {modules.map((m, i) => {
            const p = pts[i];
            const mp = moduleProgress(m);
            const complete = mp === 1;
            const current = i === currentIdx;
            const labelY = p.y > 100 ? p.y + 42 : p.y - 34;
            return (
              <a key={m.slug} href={`#module-${m.number}`} className="group">
                <title>{`${m.label}: ${m.title} (${m.customer.company})`}</title>
                {current && <circle cx={p.x} cy={p.y} r="22" fill="var(--color-forest)" opacity="0.12" />}
                <circle
                  cx={p.x}
                  cy={p.y}
                  r="15"
                  fill={complete ? "var(--color-forest)" : current ? "var(--color-graphite)" : "var(--color-paper)"}
                  stroke={complete ? "var(--color-forest)" : current ? "var(--color-graphite)" : "var(--color-graphite-3)"}
                  strokeWidth="2"
                  className="transition group-hover:opacity-80"
                />
                <text
                  x={p.x}
                  y={p.y + 4.5}
                  textAnchor="middle"
                  className="font-mono"
                  fontSize="12"
                  fontWeight="600"
                  fill={complete || current ? "#fff" : "var(--color-graphite-2)"}
                >
                  {complete ? "✓" : m.locked ? "🔒" : m.code}
                </text>
                <text x={p.x} y={labelY} textAnchor="middle" fontSize="12.5" fontWeight="600" fill="var(--color-graphite)" className="font-sans">
                  {m.customer.company}
                </text>
                <text x={p.x} y={labelY + 15} textAnchor="middle" fontSize="10.5" fill="var(--color-graphite-3)" className="font-sans">
                  {m.label}
                </text>
              </a>
            );
          })}
        </svg>
      </section>

      {/* Dossiers */}
      <section className="mt-12">
        <div className="flex items-end justify-between">
          <h2 className="font-serif text-2xl font-semibold text-graphite">{sectionTitle}</h2>
          <span className="text-sm text-graphite-3">
            {doneCount} of {all.length} lessons
          </span>
        </div>
        <ol className="mt-5 grid items-start gap-4 md:grid-cols-2">
          {modules.map((m, i) => {
            const mp = moduleProgress(m);
            const done = m.lessons.filter((l) => isDone(m, l.slug)).length;
            const current = i === currentIdx;
            return (
              <li
                key={m.slug}
                id={`module-${m.number}`}
                className={`min-w-0 scroll-mt-24 rounded-3xl border bg-white/70 transition ${current ? "border-graphite shadow-[0_24px_50px_-34px_rgba(29,27,22,0.7)]" : "border-rule"}`}
              >
                <details open={current}>
                  <summary className="flex cursor-pointer list-none gap-4 p-5 sm:p-6">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-graphite-3">
                        <span className="font-mono text-graphite">{badge(m.code)}</span>
                        <span>·</span>
                        <span className="truncate">{m.customer.company}</span>
                        {m.status === "coming-soon" && (
                          <span className="shrink-0 whitespace-nowrap rounded-full border border-rule px-2 py-0.5 text-[10px] tracking-wider text-graphite-3">Coming soon</span>
                        )}
                        {m.locked && m.status === "live" && <span className="shrink-0 whitespace-nowrap rounded-full bg-graphite px-2 py-0.5 text-[10px] tracking-wider text-paper">Full course</span>}
                        {current && !m.locked && <span className="shrink-0 whitespace-nowrap rounded-full bg-vermilion/10 px-2 py-0.5 text-[10px] text-vermilion">In progress</span>}
                      </div>
                      <h3 className="mt-2 font-serif text-xl font-semibold leading-snug text-graphite">{m.title}</h3>
                      <p className="mt-2 line-clamp-2 text-sm leading-relaxed text-graphite-2">{m.summary}</p>
                      <div className="mt-4 flex items-center gap-2 text-xs text-graphite-3">
                        <Avatar name={m.customer.contact} size="sm" />
                        <span className="truncate">
                          {m.customer.contact}, {m.customer.role}
                        </span>
                        <span className="ml-auto shrink-0 whitespace-nowrap">
                          {m.status === "live" ? `${m.lessons.length} lessons · ` : "about "}
                          {Math.round(m.minutes / 6) / 10}h
                        </span>
                      </div>
                    </div>
                    <Ring value={mp} size={52}>
                      <span className="font-mono text-[11px] font-semibold text-graphite">
                        {done}/{m.lessons.length}
                      </span>
                    </Ring>
                  </summary>
                  <ul className="border-t border-rule px-3 py-2">
                    {m.lessons.map((l) => {
                      const complete = isDone(m, l.slug);
                      return (
                        <li key={l.slug}>
                          <Link href={`/learn/${m.slug}/${l.slug}`} className="flex items-center gap-3 rounded-xl px-3 py-2 text-sm hover:bg-paper-2">
                            <span
                              className={`w-10 shrink-0 font-mono text-[10px] uppercase tracking-wider ${HOT_TYPES.has(l.type) ? "text-vermilion" : "text-graphite-3"}`}
                            >
                              {TYPE_MARK[l.type] ?? "·"}
                            </span>
                            <span className={complete ? "text-graphite-3 line-through decoration-rule" : "text-graphite"}>{shortTitle(l.title)}</span>
                            <span className="ml-auto text-xs text-graphite-3">{l.minutes}m</span>
                            <span
                              className={`flex h-4 w-4 items-center justify-center rounded-full text-[9px] ${complete ? "bg-forest text-white" : "border border-rule"}`}
                            >
                              {complete ? "✓" : ""}
                            </span>
                          </Link>
                        </li>
                      );
                    })}
                  </ul>
                </details>
              </li>
            );
          })}
        </ol>
      </section>

      {!viewer.signedIn && (
        <button
          onClick={() => confirm("Reset all progress and saved code in this browser?") && resetProgress()}
          className="mt-12 text-xs text-graphite-3 hover:text-graphite"
        >
          Reset my progress
        </button>
      )}
    </>
  );
}
