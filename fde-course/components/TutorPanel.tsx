"use client";

import { useState } from "react";
import type { RunResult } from "@/lib/python-runner";

// The server loads the lesson's instructions itself; the browser sends only which lesson,
// the learner's code and output, and their question.

export default function TutorPanel({
  moduleSlug,
  lessonSlug,
  code,
  result,
  assistOff = false,
  loopMode = false,
  offReason,
}: {
  moduleSlug: string;
  lessonSlug: string;
  code: string;
  result: RunResult | null;
  /** A drill clock is running: the server refuses the tutor. */
  assistOff?: boolean;
  /** A mock loop is running on this lesson. */
  loopMode?: boolean;
  /** When set, the tutor is shown as switched off with this explanation. */
  offReason?: string;
}) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (offReason) {
    return (
      <div className="mt-6 rounded-2xl border border-dashed border-rule bg-paper-2/40 p-5">
        <h3 className="font-serif text-lg font-semibold text-graphite">Ask a senior FDE</h3>
        <p className="mt-1 text-sm text-graphite-2">{offReason}</p>
      </div>
    );
  }

  const ask = async () => {
    setLoading(true);
    setAnswer(null);
    try {
      const res = await fetch("/api/tutor", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          module: moduleSlug,
          lesson: lessonSlug,
          code: code.slice(0, 12000),
          output: result ? [result.stdout, result.error, ...result.tests.filter((t) => !t.passed).map((t) => `FAILED: ${t.name} — ${t.message}`)].filter(Boolean).join("\n").slice(0, 6000) : "",
          question: question.slice(0, 2000),
          assistOff,
          loopMode,
        }),
      });
      const data = (await res.json().catch(() => ({}))) as { answer?: string; error?: string };
      setAnswer(data.answer ?? data.error ?? `The tutor couldn't answer (${res.status}). Try again.`);
    } catch {
      setAnswer("Couldn't reach the tutor. Check your connection and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-6 rounded-2xl border border-rule bg-white/60 p-5">
      <div className="flex items-center gap-2">
        <span className="flex h-6 w-6 items-center justify-center rounded-full bg-graphite text-[11px] text-emerald-300" aria-hidden="true">
          ✦
        </span>
        <h3 className="font-serif text-lg font-semibold">Ask a senior FDE</h3>
      </div>
      <p className="mt-1 text-sm text-graphite-3">An AI tutor (Claude) reads your code and test results and nudges you in the right direction. It won&apos;t hand you the answer.</p>
      <label htmlFor="tutor-question" className="sr-only">
        What are you stuck on?
      </label>
      <textarea
        id="tutor-question"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Optional: what are you stuck on?"
        rows={2}
        className="mt-3 w-full rounded-xl border border-rule bg-paper/70 p-3 text-sm text-graphite placeholder:text-graphite-3 focus:border-forest focus:outline-none"
      />
      <button onClick={ask} disabled={loading} className="mt-2 rounded-lg bg-graphite px-4 py-2 text-sm font-semibold text-paper hover:bg-black disabled:opacity-50">
        {loading ? "Thinking…" : "Ask the tutor"}
      </button>
      <div aria-live="polite">
        {answer && <div className="check-in mt-4 whitespace-pre-wrap rounded-xl border-l-4 border-forest bg-paper/80 p-4 text-[15px] leading-relaxed text-graphite-2">{answer}</div>}
      </div>
    </div>
  );
}
