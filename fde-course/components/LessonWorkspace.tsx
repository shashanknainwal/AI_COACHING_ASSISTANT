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

const CodeEditor = dynamic(() => import("./CodeEditor"), { ssr: false });

export interface WorkspaceLesson {
  moduleSlug: string;
  slug: string;
  title: string;
  type: "reading" | "exercise" | "quiz";
  minutes: number;
  html: string;
  hints: string[];
  questions: QuizQuestion[];
  starter: string;
  setup: string;
  tests: string;
}

interface NavLink {
  href: string;
  title: string;
}

const SCRATCH = `# Scratchpad: try anything from the lesson here.
# Press Run (or Ctrl/Cmd + Enter).

print("Hello, forward deployed engineer!")
`;

export default function LessonWorkspace({
  lesson,
  moduleTitle,
  moduleNumber,
  position,
  prev,
  next,
  viewer,
}: {
  viewer: ClientViewer;
  lesson: WorkspaceLesson;
  moduleTitle: string;
  moduleNumber: number;
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

  const [code, setCode] = useState(initial);
  const [result, setResult] = useState<RunResult | null>(null);
  const [busy, setBusy] = useState<null | "run" | "submit">(null);
  const [pyStatus, setPyStatus] = useState("Python not loaded yet");
  const [hintsShown, setHintsShown] = useState(0);
  const [split, setSplit] = useState(50);
  const dragging = useRef(false);
  const edited = useRef(false);

  // Restore saved code for this lesson.
  useEffect(() => {
    edited.current = false;
    setCode(getSavedCode(id) ?? initial);
    setResult(null);
    setHintsShown(0);
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
    const off = onPythonStatus((s) => setPyStatus(s === "ready" ? "Python ready" : s));
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
      try {
        const r = await runPython({ code, setup: lesson.setup, tests: mode === "submit" ? lesson.tests : "", mode });
        setResult(r);
        if (mode === "submit" && r.passed) markComplete(id);
      } catch (e) {
        setResult({ ok: false, stdout: "", error: String(e), tests: [], passed: null });
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
      setSplit(Math.min(70, Math.max(30, pct)));
    };
    const up = () => (dragging.current = false);
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
    return () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
    };
  }, []);

  const typeLabel = { reading: "Lesson", exercise: "Exercise", quiz: "Quiz" }[lesson.type];

  return (
    <div className="flex h-screen flex-col">
      {/* Top bar */}
      <header className="flex h-12 shrink-0 items-center gap-3 border-b border-line bg-panel px-4 text-sm">
        <Link href="/learn" className="font-semibold text-accent hover:underline">
          FDE Course
        </Link>
        <span className="text-gray-600">/</span>
        <span className="hidden truncate text-gray-400 sm:inline">
          Module {moduleNumber}: {moduleTitle}
        </span>
        <span className="ml-auto text-xs text-gray-500">
          {position.index} of {position.total}
        </span>
        {!isQuiz && (
          <button
            onClick={() => setShowEditor((v) => !v)}
            className="hidden rounded border border-line px-2 py-1 text-gray-300 hover:bg-line lg:inline"
            title={showEditor ? "Hide the code editor" : "Open a Python scratchpad"}
          >
            {showEditor ? "Hide editor" : "Scratchpad"}
          </button>
        )}
        <AccountBadge viewer={viewer} compact />
        {prev && (
          <Link href={prev.href} className="rounded border border-line px-2 py-1 text-gray-300 hover:bg-line" title={prev.title}>
            ← Prev
          </Link>
        )}
        {next && (
          <Link
            href={next.href}
            className={`rounded px-2 py-1 font-medium ${done ? "bg-accent text-ink hover:opacity-90" : "border border-line text-gray-300 hover:bg-line"}`}
            title={next.title}
          >
            Next →
          </Link>
        )}
      </header>

      {/* Phones: one scrolling column (lesson, then editor). Desktop: resizable side-by-side panes. */}
      <div className="flex min-h-0 flex-1 flex-col overflow-y-auto lg:flex-row lg:overflow-hidden">
        {/* Left: lesson content */}
        <section
          className="shrink-0 border-line lg:min-h-0 lg:shrink lg:basis-[var(--split)] lg:overflow-y-auto lg:border-r"
          style={{ "--split": fullWidth ? "100%" : `${split}%` } as React.CSSProperties}
        >
          <div className="mx-auto max-w-3xl px-6 py-8">
            <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-wider">
              <span className={isExercise ? "text-accent-2" : isQuiz ? "text-amber-400" : "text-accent"}>{typeLabel}</span>
              <span className="text-gray-600">·</span>
              <span className="text-gray-500">{lesson.minutes} min</span>
              {done && <span className="ml-2 rounded bg-accent/15 px-2 py-0.5 text-accent">✓ Completed</span>}
            </div>
            <h1 className="mb-6 text-3xl font-bold text-white">{lesson.title}</h1>
            <article
              className="lesson-body prose prose-invert max-w-none prose-headings:text-white prose-a:text-accent-2 prose-code:text-emerald-300 prose-code:before:content-none prose-code:after:content-none"
              dangerouslySetInnerHTML={{ __html: lesson.html }}
            />

            {isQuiz && <Quiz questions={lesson.questions} onPass={() => markComplete(id)} />}

            {isExercise && lesson.hints.length > 0 && (
              <div className="mt-8 rounded-lg border border-line bg-panel-2 p-4">
                <div className="mb-2 flex items-center justify-between">
                  <h3 className="font-semibold text-white">Hints</h3>
                  {hintsShown < lesson.hints.length && (
                    <button onClick={() => setHintsShown((n) => n + 1)} className="text-sm text-accent-2 hover:underline">
                      Show hint {hintsShown + 1} of {lesson.hints.length}
                    </button>
                  )}
                </div>
                {hintsShown === 0 && <p className="text-sm text-gray-500">Stuck? Reveal one hint at a time.</p>}
                <ol className="list-decimal space-y-2 pl-5 text-sm text-gray-300">
                  {lesson.hints.slice(0, hintsShown).map((h, i) => (
                    <li key={i}>{h}</li>
                  ))}
                </ol>
              </div>
            )}

            {isExercise && (
              <TutorPanel lessonTitle={lesson.title} instructionsHtml={lesson.html} code={code} result={result} />
            )}

            {next && done && (
              <Link href={next.href} className="mt-10 block rounded-lg bg-accent px-5 py-3 text-center font-semibold text-ink hover:opacity-90">
                Continue: {next.title} →
              </Link>
            )}
          </div>
        </section>

        {!fullWidth && (
          <>
            <div
              className="hidden w-1 cursor-col-resize bg-line hover:bg-accent/50 lg:block"
              onPointerDown={() => (dragging.current = true)}
            />
            {/* Right: editor + console */}
            <section className="flex h-[85vh] shrink-0 flex-col border-t border-line bg-panel-2 lg:h-auto lg:min-h-0 lg:flex-1 lg:shrink lg:border-t-0">
              <div className="flex h-11 shrink-0 items-center gap-2 border-b border-line px-3 text-sm">
                <span className="font-mono text-gray-400">main.py</span>
                <span className="ml-2 hidden text-xs text-gray-500 sm:inline">{pyStatus}</span>
                <div className="ml-auto flex gap-2">
                  <button onClick={resetCode} className="rounded px-2 py-1 text-gray-400 hover:bg-line" title="Reset code">
                    Reset
                  </button>
                  <button
                    onClick={() => execute("run")}
                    disabled={busy !== null}
                    className="rounded border border-line px-3 py-1 text-gray-200 hover:bg-line disabled:opacity-50"
                    title="Ctrl/Cmd + Enter"
                  >
                    {busy === "run" ? "Running…" : "▶ Run"}
                  </button>
                  {isExercise && (
                    <button
                      onClick={() => execute("submit")}
                      disabled={busy !== null}
                      className="rounded bg-accent px-3 py-1 font-semibold text-ink hover:opacity-90 disabled:opacity-50"
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
              <Console result={result} busy={busy} />
            </section>
          </>
        )}
      </div>
    </div>
  );
}

function Console({ result, busy }: { result: RunResult | null; busy: null | "run" | "submit" }) {
  return (
    <div className="min-h-0 flex-[2] overflow-y-auto border-t border-line bg-ink p-3 font-mono text-sm">
      <div className="mb-2 text-xs uppercase tracking-wider text-gray-500">Output</div>
      {busy && <div className="text-gray-500">Running…</div>}
      {!busy && !result && <div className="text-gray-600">Run your code to see output here.</div>}
      {!busy && result && (
        <>
          {result.stdout && <pre className="whitespace-pre-wrap text-gray-200">{result.stdout}</pre>}
          {result.error && <pre className="mt-2 whitespace-pre-wrap text-red-400">{result.error}</pre>}
          {!result.stdout && !result.error && result.passed === null && <div className="text-gray-600">(no output)</div>}
          {result.tests.length > 0 && (
            <div className="mt-3 space-y-1 border-t border-line pt-3 font-sans">
              {result.passed ? (
                <div className="mb-2 rounded bg-accent/15 px-3 py-2 font-semibold text-accent">
                  ✓ All {result.tests.length} checks passed. Exercise complete!
                </div>
              ) : (
                <div className="mb-2 rounded bg-red-500/10 px-3 py-2 text-red-300">
                  {result.tests.filter((t) => t.passed).length} of {result.tests.length} checks passed. Fix the ones below and submit again.
                </div>
              )}
              {result.tests.map((t, i) => (
                <div key={i} className="flex gap-2">
                  <span className={t.passed ? "text-accent" : "text-red-400"}>{t.passed ? "✓" : "✗"}</span>
                  <div>
                    <div className={t.passed ? "text-gray-300" : "text-gray-100"}>{t.name}</div>
                    {!t.passed && t.message && <div className="whitespace-pre-wrap text-xs text-red-300">{t.message}</div>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
