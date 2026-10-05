"use client";

import { useState } from "react";
import type { RunResult } from "@/lib/python-runner";

export default function TutorPanel({
  lessonTitle,
  instructionsHtml,
  code,
  result,
}: {
  lessonTitle: string;
  instructionsHtml: string;
  code: string;
  result: RunResult | null;
}) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const ask = async () => {
    setLoading(true);
    setAnswer(null);
    try {
      const res = await fetch("/api/tutor", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lessonTitle,
          instructions: instructionsHtml.replace(/<[^>]+>/g, " ").slice(0, 12000),
          code: code.slice(0, 12000),
          output: result ? [result.stdout, result.error, ...result.tests.filter((t) => !t.passed).map((t) => `FAILED: ${t.name} — ${t.message}`)].filter(Boolean).join("\n").slice(0, 6000) : "",
          question: question.slice(0, 2000),
        }),
      });
      const data = await res.json();
      setAnswer(data.answer ?? data.error ?? "No answer.");
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
      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Optional: what are you stuck on?"
        rows={2}
        className="mt-3 w-full rounded-xl border border-rule bg-paper/70 p-3 text-sm text-graphite placeholder:text-graphite-3 focus:border-forest focus:outline-none"
      />
      <button onClick={ask} disabled={loading} className="mt-2 rounded-lg bg-graphite px-4 py-2 text-sm font-semibold text-paper hover:bg-black disabled:opacity-50">
        {loading ? "Thinking…" : "Ask the tutor"}
      </button>
      {answer && <div className="check-in mt-4 whitespace-pre-wrap rounded-xl border-l-4 border-forest bg-paper/80 p-4 text-[15px] leading-relaxed text-graphite-2">{answer}</div>}
    </div>
  );
}
