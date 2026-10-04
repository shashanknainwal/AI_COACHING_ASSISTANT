"use client";

import { useState } from "react";

export interface QuizQuestion {
  q: string;
  options: string[];
  answer: number;
  explain?: string;
}

const PASS_RATIO = 0.8;

export default function Quiz({ questions, onPass }: { questions: QuizQuestion[]; onPass: () => void }) {
  const [picked, setPicked] = useState<(number | null)[]>(() => questions.map(() => null));
  const [checked, setChecked] = useState(false);

  const score = picked.filter((p, i) => p === questions[i].answer).length;
  const allAnswered = picked.every((p) => p !== null);
  const passed = checked && score / questions.length >= PASS_RATIO;

  const check = () => {
    setChecked(true);
    if (score / questions.length >= PASS_RATIO) onPass();
  };

  return (
    <div className="mt-8 space-y-6">
      {questions.map((q, qi) => (
        <div key={qi} className="rounded-lg border border-line bg-panel-2 p-5">
          <p className="mb-3 font-medium text-white">
            {qi + 1}. {q.q}
          </p>
          <div className="space-y-2">
            {q.options.map((opt, oi) => {
              const chosen = picked[qi] === oi;
              const correct = oi === q.answer;
              let cls = "border-line hover:border-gray-500";
              if (checked && chosen && correct) cls = "border-accent bg-accent/10";
              else if (checked && chosen && !correct) cls = "border-red-500 bg-red-500/10";
              else if (checked && correct) cls = "border-accent/50";
              else if (chosen) cls = "border-accent-2 bg-accent-2/10";
              return (
                <button
                  key={oi}
                  disabled={checked}
                  onClick={() => setPicked((p) => p.map((v, i) => (i === qi ? oi : v)))}
                  className={`block w-full rounded border px-3 py-2 text-left text-sm text-gray-200 ${cls}`}
                >
                  {opt}
                </button>
              );
            })}
          </div>
          {checked && q.explain && <p className="mt-3 text-sm text-gray-400">{q.explain}</p>}
        </div>
      ))}

      {!checked ? (
        <button
          onClick={check}
          disabled={!allAnswered}
          className="rounded-lg bg-accent px-5 py-2 font-semibold text-ink disabled:opacity-40"
        >
          Check answers
        </button>
      ) : (
        <div className={`rounded-lg p-4 ${passed ? "bg-accent/15 text-accent" : "bg-red-500/10 text-red-300"}`}>
          You scored {score} / {questions.length}.{" "}
          {passed ? "Passed. Nice work!" : `You need ${Math.ceil(questions.length * PASS_RATIO)} to pass.`}
          {!passed && (
            <button
              onClick={() => {
                setChecked(false);
                setPicked(questions.map(() => null));
              }}
              className="ml-3 underline"
            >
              Try again
            </button>
          )}
        </div>
      )}
    </div>
  );
}
