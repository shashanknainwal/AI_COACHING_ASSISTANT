"use client";

import { useState } from "react";

export interface QuizQuestion {
  q: string;
  options: string[];
  answer: number;
  explain?: string;
}

const PASS_RATIO = 0.8;
const LETTERS = "ABCDEFGH";

export default function Quiz({ questions, onPass }: { questions: QuizQuestion[]; onPass: () => void }) {
  const [picked, setPicked] = useState<(number | null)[]>(() => questions.map(() => null));
  const [checked, setChecked] = useState(false);

  const score = picked.filter((p, i) => p === questions[i].answer).length;
  const answered = picked.filter((p) => p !== null).length;
  const allAnswered = answered === questions.length;
  const needed = Math.ceil(questions.length * PASS_RATIO);
  const passed = checked && score >= needed;

  const check = () => {
    setChecked(true);
    if (score >= needed) onPass();
  };

  return (
    <div className="mt-10 space-y-5">
      {questions.map((q, qi) => (
        <div key={qi} className="rounded-2xl border border-rule bg-white/70 p-5 sm:p-6">
          <div className="flex gap-3">
            <span className="font-mono text-sm text-graphite-3">{String(qi + 1).padStart(2, "0")}</span>
            <p className="font-serif text-lg font-semibold leading-snug text-graphite">{q.q}</p>
          </div>
          <div className="mt-4 space-y-2">
            {q.options.map((opt, oi) => {
              const chosen = picked[qi] === oi;
              const correct = oi === q.answer;
              let cls = "border-rule bg-paper/60 hover:border-graphite-3";
              let badge = "border-rule text-graphite-3";
              if (checked && correct) {
                cls = "border-forest bg-forest/[0.07]";
                badge = "border-forest bg-forest text-white";
              } else if (checked && chosen && !correct) {
                cls = "border-vermilion bg-vermilion/[0.06]";
                badge = "border-vermilion bg-vermilion text-white";
              } else if (chosen) {
                cls = "border-graphite bg-white";
                badge = "border-graphite bg-graphite text-white";
              }
              return (
                <button
                  key={oi}
                  disabled={checked}
                  onClick={() => setPicked((p) => p.map((v, i) => (i === qi ? oi : v)))}
                  className={`flex w-full items-start gap-3 rounded-xl border px-3.5 py-2.5 text-left text-[15px] text-graphite-2 transition ${cls}`}
                >
                  <span className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-md border font-mono text-[11px] font-semibold ${badge}`}>
                    {LETTERS[oi]}
                  </span>
                  <span>{opt}</span>
                </button>
              );
            })}
          </div>
          {checked && q.explain && (
            <p className="mt-4 border-l-2 border-forest pl-3 text-sm leading-relaxed text-graphite-2">
              <span className="font-semibold">{picked[qi] === q.answer ? "Correct. " : "Not quite. "}</span>
              {q.explain}
            </p>
          )}
        </div>
      ))}

      <div className="sticky bottom-4 z-10">
        {!checked ? (
          <div className="flex items-center justify-between gap-4 rounded-2xl bg-graphite px-5 py-3.5 text-paper shadow-[0_18px_40px_-20px_rgba(29,27,22,0.8)]">
            <span className="text-sm text-paper-3">
              {answered} of {questions.length} answered · {needed} to pass
            </span>
            <button onClick={check} disabled={!allAnswered} className="rounded-lg bg-emerald-400 px-4 py-2 text-sm font-semibold text-graphite disabled:opacity-40">
              Check answers
            </button>
          </div>
        ) : (
          <div
            className={`flex flex-wrap items-center justify-between gap-3 rounded-2xl px-5 py-4 shadow-[0_18px_40px_-20px_rgba(29,27,22,0.6)] ${
              passed ? "bg-forest text-white" : "bg-white text-graphite ring-1 ring-vermilion/40"
            }`}
          >
            <span className="font-serif text-lg">
              {score} / {questions.length}. {passed ? "Checkpoint passed." : `You need ${needed} to pass.`}
            </span>
            {!passed && (
              <button
                onClick={() => {
                  setChecked(false);
                  setPicked(questions.map(() => null));
                }}
                className="rounded-lg bg-graphite px-4 py-2 text-sm font-semibold text-white"
              >
                Try again
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
