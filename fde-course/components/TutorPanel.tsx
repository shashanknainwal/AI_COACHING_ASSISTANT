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
    <div className="mt-6 rounded-lg border border-line bg-panel-2 p-4">
      <h3 className="mb-1 font-semibold text-white">AI tutor</h3>
      <p className="mb-3 text-sm text-gray-500">Gets a nudge in the right direction based on your code and test output. It won&apos;t hand you the answer.</p>
      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Optional: what are you stuck on?"
        rows={2}
        className="mb-2 w-full rounded border border-line bg-ink p-2 text-sm text-gray-200 placeholder:text-gray-600"
      />
      <button onClick={ask} disabled={loading} className="rounded border border-accent-2 px-3 py-1 text-sm text-accent-2 hover:bg-accent-2/10 disabled:opacity-50">
        {loading ? "Thinking…" : "Ask the tutor"}
      </button>
      {answer && <div className="mt-3 whitespace-pre-wrap rounded bg-ink p-3 text-sm text-gray-200">{answer}</div>}
    </div>
  );
}
