"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { runPython, onPythonStatus, warmUpPython, type RunResult } from "@/lib/python-runner";
import { enableServerSync, lessonId, markComplete, saveCode, getSavedCode, useProgress } from "@/lib/progress";
import type { ClientViewer } from "@/lib/access";
import AccountBadge from "./AccountBadge";
import Quiz, { type QuizQuestion } from "./Quiz";
import TutorPanel from "./TutorPanel";
import { Avatar, Mark } from "./Playbook";

const CodeEditor = dynamic(() => import("./CodeEditor"), { ssr: false });

export interface WorkspaceLesson {
  moduleSlug: string;
  slug: string;
  title: string;
  type: "reading" | "exercise" | "quiz";
  minutes: number;
  briefHtml: string;
  html: string;
  hints: string[];
  questions: QuizQuestion[];
  starter: string;
  setup: string;
  tests: string;
}

export interface WorkspaceCustomer {
  company: string;
  sector: string;
  contact: string;
  role: string;
  replies: string[];
}

interface NavLink {
  href: string;
  title: string;
}

interface Sibling {
  slug: string;
  title: string;
  type: string;
}

const SCRATCH = `# Scratchpad: try anything from the lesson here.
# Press Run (or Ctrl/Cmd + Enter).

print("Hello, forward deployed engineer!")
`;

const TYPE_LABEL = { reading: "Field reading", exercise: "Engagement task", quiz: "Checkpoint" } as const;

export default function LessonWorkspace({
  lesson,
  moduleTitle,
  moduleNumber,
  customer,
  siblings,
  position,
  prev,
  next,
  viewer,
}: {
  viewer: ClientViewer;
  lesson: WorkspaceLesson;
  moduleTitle: string;
  moduleNumber: number;
  customer: WorkspaceCustomer;
  siblings: Sibling[];
  position: { index: number; total: number };
  prev: NavLink | null;
  next: NavLink | null;
}) {
  const id = lessonId(lesson.moduleSlug, lesson.slug);
  const isExercise = lesson.type === "exercise";
  const isQuiz = lesson.type === "quiz";
  // Reading lessons without example code open full-width; the scratchpad is one click away.
  const [showEditor, setShowEditor] = useState(!isQuiz && (lesson.type !== "reading" || Boolean(lesson.starter)));
  const fullWidth = isQuiz || !showEditor;
  const initial = lesson.starter || SCRATCH;
  const progress = useProgress();
  const done = Boolean(progress.completed[id]);
  const indexInModule = Math.max(0, siblings.findIndex((s) => s.slug === lesson.slug));
  const reply = customer.replies[indexInModule % customer.replies.length];

  const [code, setCode] = useState(initial);
  const [result, setResult] = useState<RunResult | null>(null);
  const [runId, setRunId] = useState(0);
  const [busy, setBusy] = useState<null | "run" | "submit">(null);
  const [pyStatus, setPyStatus] = useState("loading");
  const [tab, setTab] = useState<"output" | "checks">("output");
  const [hintsShown, setHintsShown] = useState(0);
  const [split, setSplit] = useState(48);
  const dragging = useRef(false);
  const edited = useRef(false);

  // Restore saved code for this lesson.
  useEffect(() => {
    edited.current = false;
    setCode(getSavedCode(id) ?? initial);
    setResult(null);
    setHintsShown(0);
    setTab("output");
  }, [id, initial]);

  // Signed in: merge with the account's progress, then restore code saved on another device.
  useEffect(() => {
    if (!viewer.signedIn) return;
    enableServerSync().then(() => {
      if (!edited.current) setCode(getSavedCode(id) ?? initial);
    });
  }, [viewer.signedIn, id, initial]);

  useEffect(() => {
    if (!showEditor) return;
    const off = onPythonStatus((s) => setPyStatus(s));
    warmUpPython();
    return off;
  }, [showEditor]);

  // Reading lessons count as complete once opened.
  useEffect(() => {
    if (lesson.type === "reading") markComplete(id);
  }, [id, lesson.type]);

  const onChange = useCallback(
    (v: string) => {
      edited.current = true;
      setCode(v);
      saveCode(id, v);
    },
    [id],
  );

  const execute = useCallback(
    async (mode: "run" | "submit") => {
      setBusy(mode);
      if (mode === "submit") setTab("checks");
      try {
        const r = await runPython({ code, setup: lesson.setup, tests: mode === "submit" ? lesson.tests : "", mode });
        setResult(r);
        setRunId((n) => n + 1);
        if (mode === "submit" && r.passed) markComplete(id);
        if (mode === "run") setTab("output");
      } catch (e) {
        setResult({ ok: false, stdout: "", error: String(e), tests: [], passed: null });
        setTab("output");
      } finally {
        setBusy(null);
      }
    },
    [code, lesson.setup, lesson.tests, id],
  );

  const resetCode = () => {
    if (!confirm("Reset the editor to the starting code? Your changes will be lost.")) return;
    setCode(initial);
    saveCode(id, initial);
    setResult(null);
  };

  useEffect(() => {
    const move = (e: PointerEvent) => {
      if (!dragging.current) return;
      const pct = (e.clientX / window.innerWidth) * 100;
      setSplit(Math.min(68, Math.max(32, pct)));
    };
    const up = () => (dragging.current = false);
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
    return () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
    };
  }, []);

  const ready = pyStatus === "ready";
  const checks = result?.tests ?? [];

  return (
    <div className="flex h-screen flex-col bg-paper text-graphite">
      {/* Top bar */}
      <header className="flex h-14 shrink-0 items-center gap-3 border-b border-rule bg-paper-2/80 px-4 text-sm backdrop-blur">
        <Link href="/learn" className="flex items-center gap-2 font-serif text-base font-semibold text-graphite" title="Your engagement map">
          <Mark />
          <span className="hidden sm:inline">FDE Playbook</span>
        </Link>
        <span className="hidden h-5 w-px bg-rule sm:block" />
        <div className="hidden min-w-0 md:block">
          <div className="truncate text-[11px] font-medium uppercase tracking-[0.14em] text-graphite-3">
            Module {moduleNumber} · {customer.company}
          </div>
          <div className="truncate text-[13px] text-graphite-2">{moduleTitle}</div>
        </div>

        {/* Lessons in this module */}
        <nav className="mx-auto hidden items-center gap-1.5 lg:flex" aria-label="Lessons in this module">
          {siblings.map((s, i) => {
            const sid = lessonId(lesson.moduleSlug, s.slug);
            const current = s.slug === lesson.slug;
            const complete = Boolean(progress.completed[sid]);
            return (
              <Link
                key={s.slug}
                href={`/learn/${lesson.moduleSlug}/${s.slug}`}
                title={`${i + 1}. ${s.title}`}
                className={`block rounded-full transition ${
                  current ? "h-2.5 w-8 bg-graphite" : complete ? "h-2.5 w-2.5 bg-forest hover:scale-125" : "h-2.5 w-2.5 bg-paper-3 hover:bg-graphite-3"
                } ${s.type === "exercise" && !current ? "ring-1 ring-offset-1 ring-offset-paper-2 " + (complete ? "ring-forest/40" : "ring-graphite-3/40") : ""}`}
              />
            );
          })}
        </nav>

        <div className="ml-auto flex items-center gap-2 lg:ml-0">
          <span className="hidden text-xs tabular-nums text-graphite-3 xl:inline">
            {position.index} / {position.total}
          </span>
          {!isQuiz && (
            <button
              onClick={() => setShowEditor((v) => !v)}
              className="hidden rounded-lg border border-rule px-2.5 py-1 text-graphite-2 hover:bg-paper-3 lg:inline"
              title={showEditor ? "Hide the code editor" : "Open a Python scratchpad"}
            >
              {showEditor ? "Focus read" : "Scratchpad"}
            </button>
          )}
          <span className="[&_*]:!text-graphite-2 [&_button]:!border-rule [&_a]:!border-rule">
            <AccountBadge viewer={viewer} compact />
          </span>
          {prev && (
            <Link href={prev.href} className="rounded-lg border border-rule px-2.5 py-1 text-graphite-2 hover:bg-paper-3" title={prev.title}>
              ←
            </Link>
          )}
          {next && (
            <Link
              href={next.href}
              className={`rounded-lg px-3 py-1 font-medium ${done ? "bg-forest text-white hover:bg-forest-2" : "border border-rule text-graphite-2 hover:bg-paper-3"}`}
              title={next.title}
            >
              Next →
            </Link>
          )}
        </div>
      </header>

      {/* Phones: one scrolling column (lesson, then editor). Desktop: resizable side-by-side panes. */}
      <div className="flex min-h-0 flex-1 flex-col overflow-y-auto lg:flex-row lg:overflow-hidden">
        {/* Left: the playbook page */}
        <section
          className="playbook-page shrink-0 lg:min-h-0 lg:shrink lg:basis-[var(--split)] lg:overflow-y-auto"
          style={{ "--split": fullWidth ? "100%" : `${split}%` } as React.CSSProperties}
        >
          <div className="mx-auto max-w-[44rem] px-6 pb-16 pt-10 sm:px-10">
            <div className="flex flex-wrap items-center gap-3 text-[11px] font-semibold uppercase tracking-[0.16em]">
              <span className={isExercise ? "text-vermilion" : isQuiz ? "text-graphite" : "text-forest"}>{TYPE_LABEL[lesson.type]}</span>
              <span className="h-px w-6 bg-rule" />
              <span className="text-graphite-3">{lesson.minutes} min</span>
              {done && (
                <span className="ml-auto rotate-[-3deg] rounded border-2 border-forest px-2 py-0.5 text-forest">
                  {isExercise ? "Resolved" : "Done"}
                </span>
              )}
            </div>
            <h1 className="mt-4 font-serif text-[2.35rem] font-semibold leading-[1.12] tracking-[-0.015em] text-graphite sm:text-[2.7rem]">
              {lesson.title.replace(/^Exercise:\s*/, "")}
            </h1>

            {isExercise && lesson.briefHtml && <CaseFile customer={customer} briefHtml={lesson.briefHtml} resolved={done} />}

            <article className="playbook-prose mt-8" dangerouslySetInnerHTML={{ __html: lesson.html }} />

            {isQuiz && <Quiz questions={lesson.questions} onPass={() => markComplete(id)} />}

            {isExercise && lesson.hints.length > 0 && (
              <div className="mt-10 rounded-2xl border border-rule bg-white/60 p-5">
                <div className="flex items-center justify-between gap-4">
                  <h3 className="font-serif text-lg font-semibold">Field notes</h3>
                  {hintsShown < lesson.hints.length && (
                    <button onClick={() => setHintsShown((n) => n + 1)} className="text-sm font-medium text-forest hover:underline">
                      Reveal note {hintsShown + 1} of {lesson.hints.length}
                    </button>
                  )}
                </div>
                {hintsShown === 0 && <p className="mt-1 text-sm text-graphite-3">Stuck? Reveal one hint at a time, the way a senior FDE would nudge you.</p>}
                <ol className="mt-3 space-y-3">
                  {lesson.hints.slice(0, hintsShown).map((h, i) => (
                    <li key={i} className="check-in flex gap-3 text-[15px] leading-relaxed text-graphite-2">
                      <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-vermilion/10 font-mono text-xs font-semibold text-vermilion">
                        {i + 1}
                      </span>
                      <span>{h}</span>
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {isExercise && <TutorPanel lessonTitle={lesson.title} instructionsHtml={lesson.briefHtml + lesson.html} code={code} result={result} />}

            {next && done && (
              <Link
                href={next.href}
                className="group mt-12 flex items-center justify-between rounded-2xl bg-graphite px-6 py-5 text-paper shadow-[0_18px_40px_-24px_rgba(29,27,22,0.7)] hover:bg-black"
              >
                <span>
                  <span className="block text-[11px] font-semibold uppercase tracking-[0.16em] text-paper-3">Up next</span>
                  <span className="mt-1 block font-serif text-lg">{next.title}</span>
                </span>
                <span className="text-2xl transition group-hover:translate-x-1">→</span>
              </Link>
            )}
          </div>
        </section>

        {!fullWidth && (
          <>
            <div
              className="group hidden w-2 cursor-col-resize items-center justify-center bg-paper-3 lg:flex"
              onPointerDown={() => (dragging.current = true)}
              title="Drag to resize"
            >
              <span className="h-10 w-0.5 rounded bg-graphite-3/40 group-hover:bg-forest" />
            </div>

            {/* Right: the console */}
            <section className="flex h-[88vh] shrink-0 flex-col bg-console text-gray-200 lg:h-auto lg:min-h-0 lg:flex-1 lg:shrink">
              <div className="flex h-12 shrink-0 items-center gap-3 border-b border-console-line px-3 text-sm">
                <div className="flex gap-1.5" aria-hidden="true">
                  <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" />
                  <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" />
                  <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]" />
                </div>
                <span className="rounded-md bg-console-2 px-2.5 py-1 font-mono text-xs text-gray-300">main.py</span>
                <span className="hidden items-center gap-1.5 font-mono text-[11px] uppercase tracking-wider text-gray-500 sm:flex">
                  <span className={`h-1.5 w-1.5 rounded-full ${ready ? "bg-emerald-400" : "animate-pulse bg-amber-400"}`} />
                  {ready ? "Runtime ready" : pyStatus === "loading" ? "Booting Python" : pyStatus}
                </span>
                <div className="ml-auto flex items-center gap-1.5">
                  <button onClick={resetCode} className="rounded-md px-2 py-1 text-xs text-gray-500 hover:bg-console-2 hover:text-gray-300" title="Reset code">
                    Reset
                  </button>
                  <button
                    onClick={() => execute("run")}
                    disabled={busy !== null}
                    className="rounded-md border border-console-line px-3 py-1.5 text-xs font-medium text-gray-200 hover:bg-console-2 disabled:opacity-50"
                    title="Ctrl/Cmd + Enter"
                  >
                    {busy === "run" ? "Running…" : "▶ Run"}
                  </button>
                  {isExercise && (
                    <button
                      onClick={() => execute("submit")}
                      disabled={busy !== null}
                      className="rounded-md bg-emerald-500 px-3 py-1.5 text-xs font-semibold text-console hover:bg-emerald-400 disabled:opacity-50"
                      title="Ctrl/Cmd + Shift + Enter"
                    >
                      {busy === "submit" ? "Checking…" : "Submit"}
                    </button>
                  )}
                </div>
              </div>
              <div className="min-h-0 flex-[3]">
                <CodeEditor value={code} onChange={onChange} onRun={() => execute("run")} onSubmit={isExercise ? () => execute("submit") : undefined} />
              </div>

              <div className="flex min-h-0 flex-[2] flex-col border-t border-console-line">
                <div className="flex shrink-0 items-center gap-1 border-b border-console-line px-2 text-xs">
                  {(["output", ...(isExercise ? ["checks"] : [])] as ("output" | "checks")[]).map((t) => (
                    <button
                      key={t}
                      onClick={() => setTab(t)}
                      className={`relative px-3 py-2 font-mono uppercase tracking-wider ${tab === t ? "text-gray-100" : "text-gray-500 hover:text-gray-300"}`}
                    >
                      {t === "output" ? "Output" : "Checks"}
                      {t === "checks" && checks.length > 0 && (
                        <span className={`ml-2 rounded px-1.5 py-0.5 ${result?.passed ? "bg-emerald-500/15 text-emerald-300" : "bg-red-500/15 text-red-300"}`}>
                          {checks.filter((c) => c.passed).length}/{checks.length}
                        </span>
                      )}
                      {tab === t && <span className="absolute inset-x-2 -bottom-px h-0.5 rounded bg-emerald-400" />}
                    </button>
                  ))}
                </div>
                <div className="min-h-0 flex-1 overflow-y-auto p-4">
                  {tab === "output" ? (
                    <Output result={result} busy={busy} />
                  ) : (
                    <ChecksPanel key={runId} result={result} busy={busy === "submit"} customer={customer} reply={reply} next={next} />
                  )}
                </div>
              </div>
            </section>
          </>
        )}
      </div>
    </div>
  );
}

function CaseFile({ customer, briefHtml, resolved }: { customer: WorkspaceCustomer; briefHtml: string; resolved: boolean }) {
  return (
    <div className="relative mt-8 overflow-hidden rounded-2xl border border-rule bg-white/70 shadow-[0_1px_0_rgba(0,0,0,0.03),0_20px_40px_-30px_rgba(29,27,22,0.5)]">
      <div className="flex items-center gap-3 border-b border-rule bg-paper-2/70 px-5 py-2.5 font-mono text-[11px] uppercase tracking-[0.14em] text-graphite-3">
        <span className="whitespace-nowrap font-semibold text-vermilion">Case file</span>
        <span>·</span>
        <span className="truncate">{customer.company}</span>
        <span
          className={`ml-auto flex items-center gap-1.5 rounded-full px-2 py-0.5 ${resolved ? "bg-forest/10 text-forest" : "bg-vermilion/10 text-vermilion"}`}
        >
          <span className={`h-1.5 w-1.5 rounded-full ${resolved ? "bg-forest" : "animate-pulse bg-vermilion"}`} />
          {resolved ? "Resolved" : "Open"}
        </span>
      </div>
      <div className="px-5 pb-5 pt-4">
        <div className="flex items-center gap-3">
          <Avatar name={customer.contact} />
          <div className="leading-tight">
            <div className="font-semibold text-graphite">{customer.contact}</div>
            <div className="text-xs text-graphite-3">
              {customer.role}, {customer.company} · {customer.sector}
            </div>
          </div>
        </div>
        <div className="casefile-body mt-4 text-[15px] leading-relaxed text-graphite-2" dangerouslySetInnerHTML={{ __html: briefHtml }} />
      </div>
    </div>
  );
}

function Output({ result, busy }: { result: RunResult | null; busy: null | "run" | "submit" }) {
  if (busy) return <div className="font-mono text-sm text-gray-500">Running…</div>;
  if (!result) return <div className="font-mono text-sm text-gray-600">Run your code to see output here. Ctrl/Cmd + Enter runs it.</div>;
  return (
    <div className="font-mono text-sm">
      {result.stdout && <pre className="whitespace-pre-wrap text-gray-200">{result.stdout}</pre>}
      {result.error && <pre className="mt-2 whitespace-pre-wrap rounded-lg bg-red-500/10 p-3 text-red-300">{result.error}</pre>}
      {!result.stdout && !result.error && <div className="text-gray-600">(no output)</div>}
    </div>
  );
}

function ChecksPanel({
  result,
  busy,
  customer,
  reply,
  next,
}: {
  result: RunResult | null;
  busy: boolean;
  customer: WorkspaceCustomer;
  reply: string;
  next: NavLink | null;
}) {
  if (busy) {
    return (
      <div className="flex items-center gap-3 font-mono text-sm text-gray-400">
        <span className="h-3 w-3 animate-spin rounded-full border-2 border-emerald-400 border-t-transparent" />
        Running the checks…
      </div>
    );
  }
  if (!result || result.tests.length === 0) {
    if (result?.error) {
      return <pre className="whitespace-pre-wrap rounded-lg bg-red-500/10 p-3 font-mono text-sm text-red-300">{result.error}</pre>;
    }
    return <div className="font-mono text-sm text-gray-600">Press Submit to run the checks for this task.</div>;
  }
  const tests = result.tests;
  const passedCount = tests.filter((t) => t.passed).length;
  const delay = (i: number) => ({ animationDelay: `${120 + i * 110}ms` });

  return (
    <div>
      {result.passed && (
        <div className="check-in mb-5 overflow-hidden rounded-xl border border-emerald-400/25 bg-gradient-to-br from-emerald-400/10 to-transparent" style={delay(tests.length)}>
          <div className="flex items-center gap-2 border-b border-emerald-400/15 px-4 py-2 font-mono text-[11px] uppercase tracking-wider text-emerald-300">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" /> Case resolved · new message
          </div>
          <div className="flex gap-3 p-4">
            <Avatar name={customer.contact} dark />
            <div>
              <div className="text-xs text-gray-400">
                <span className="font-semibold text-gray-200">{customer.contact}</span> · {customer.role}, {customer.company}
              </div>
              <p className="mt-1.5 font-serif text-[15px] leading-relaxed text-gray-100">&ldquo;{reply}&rdquo;</p>
            </div>
          </div>
          {next && (
            <Link href={next.href} className="block border-t border-emerald-400/15 px-4 py-2.5 text-sm font-medium text-emerald-300 hover:bg-emerald-400/5">
              Next: {next.title} →
            </Link>
          )}
        </div>
      )}
      <div className="flex items-baseline justify-between">
        <span className="font-mono text-xs uppercase tracking-wider text-gray-500">Checks</span>
        <span className={`font-mono text-sm ${result.passed ? "text-emerald-300" : "text-gray-300"}`}>
          {passedCount} / {tests.length} passing
        </span>
      </div>
      <div className="mt-2 flex gap-1">
        {tests.map((t, i) => (
          <span key={i} className={`bar-fill h-1.5 flex-1 rounded-full ${t.passed ? "bg-emerald-400" : "bg-red-400/80"}`} style={delay(i)} />
        ))}
      </div>

      <ul className="mt-4 space-y-2">
        {tests.map((t, i) => (
          <li key={i} className="check-in" style={delay(i)}>
            <div className="flex items-start gap-3">
              <span
                className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[11px] font-bold ${
                  t.passed ? "bg-emerald-400/15 text-emerald-300" : "bg-red-400/15 text-red-300"
                }`}
              >
                {t.passed ? "✓" : "✗"}
              </span>
              <div className="min-w-0 flex-1">
                <div className={`text-sm ${t.passed ? "text-gray-400" : "text-gray-100"}`}>{t.name}</div>
                {!t.passed && t.message && (
                  <pre className="mt-1.5 whitespace-pre-wrap rounded-md border border-red-400/20 bg-red-400/5 px-3 py-2 font-mono text-xs leading-relaxed text-red-200">
                    {t.message}
                  </pre>
                )}
              </div>
            </div>
          </li>
        ))}
      </ul>

      {!result.passed && (
        <p className="check-in mt-5 text-sm text-gray-400" style={delay(tests.length)}>
          {tests.length - passedCount} check{tests.length - passedCount === 1 ? "" : "s"} still failing. Fix the first red one, then submit again.
        </p>
      )}
    </div>
  );
}
