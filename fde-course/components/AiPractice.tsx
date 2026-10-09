"use client";

// Right-hand panes for Claude-graded lessons:
//   AnswerSheet    written answers (one or more sections), graded against the lesson's rubric
//   RoleplayChat   a conversation with a persona, then a rubric debrief
// Drafts, transcripts and the last grade are saved like code (lib/progress), so they
// survive reloads and sync to the learner's account.

import { useEffect, useRef, useState } from "react";
import type { GradeResult, TranscriptLine } from "@/lib/coach-types";
import { getSavedCode, saveCode } from "@/lib/progress";
import { Avatar } from "./Playbook";

export interface PracticeSection {
  key: string;
  label: string;
  prompt?: string;
  words?: [number, number];
}

export interface PracticePersona {
  name: string;
  role: string;
  company: string;
}

interface Saved {
  answers?: Record<string, string>;
  transcript?: TranscriptLine[];
  grade?: GradeResult | null;
}

function loadSaved(id: string): Saved {
  try {
    return JSON.parse(getSavedCode(id) ?? "{}") as Saved;
  } catch {
    return {};
  }
}

const words = (s: string) => (s.trim() ? s.trim().split(/\s+/).length : 0);

async function callCoach(body: Record<string, unknown>): Promise<{ result?: GradeResult; reply?: string; done?: boolean; error?: string }> {
  try {
    const res = await fetch("/api/coach", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) return { error: data.error ?? `Request failed (${res.status}).` };
    return data;
  } catch {
    return { error: "Couldn't reach the server. Check your connection and try again." };
  }
}

function PaneHeader({ title, right }: { title: string; right?: React.ReactNode }) {
  return (
    <div className="flex h-12 shrink-0 items-center gap-3 border-b border-console-line px-4 text-sm">
      <div className="flex gap-1.5" aria-hidden="true">
        <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" />
        <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" />
        <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]" />
      </div>
      <span className="rounded-md bg-console-2 px-2.5 py-1 font-mono text-xs text-gray-300">{title}</span>
      <div className="ml-auto flex items-center gap-2">{right}</div>
    </div>
  );
}

export function AnswerSheet({
  id,
  moduleSlug,
  lessonSlug,
  sections,
  onPass,
}: {
  id: string;
  moduleSlug: string;
  lessonSlug: string;
  sections: PracticeSection[];
  onPass: () => void;
}) {
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [grade, setGrade] = useState<GradeResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const reportRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const saved = loadSaved(id);
    setAnswers(saved.answers ?? {});
    setGrade(saved.grade ?? null);
  }, [id]);

  const persist = (next: Saved) => saveCode(id, JSON.stringify(next));

  const edit = (key: string, value: string) => {
    const next = { ...answers, [key]: value };
    setAnswers(next);
    persist({ answers: next, grade });
  };

  const submit = async () => {
    setBusy(true);
    setError(null);
    const r = await callCoach({ module: moduleSlug, lesson: lessonSlug, action: "grade", answers });
    setBusy(false);
    if (r.error || !r.result) {
      setError(r.error ?? "No result came back. Try again.");
      return;
    }
    setGrade(r.result);
    persist({ answers, grade: r.result });
    if (r.result.passed) onPass();
    setTimeout(() => reportRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 50);
  };

  const total = sections.reduce((n, s) => n + words(answers[s.key] ?? ""), 0);
  const empty = total === 0;

  return (
    <>
      <PaneHeader
        title="answer.md"
        right={
          <>
            <span className="font-mono text-[11px] text-gray-500">{total} words</span>
            <button
              onClick={submit}
              disabled={busy || empty}
              className="rounded-md bg-emerald-500 px-3 py-1.5 text-xs font-semibold text-console hover:bg-emerald-400 disabled:opacity-50"
            >
              {busy ? "Reviewing…" : grade ? "Submit again" : "Submit for review"}
            </button>
          </>
        }
      />
      <div className="min-h-0 flex-1 overflow-y-auto p-4">
        <div className="space-y-5">
          {sections.map((s) => {
            const n = words(answers[s.key] ?? "");
            const [lo, hi] = s.words ?? [0, 0];
            const off = s.words && n > 0 && (n < lo || n > hi);
            return (
              <label key={s.key} className="block">
                <span className="flex items-baseline justify-between gap-3">
                  <span className="font-mono text-xs uppercase tracking-wider text-gray-300">{s.label}</span>
                  {s.words && (
                    <span className={`font-mono text-[11px] ${off ? "text-amber-300" : "text-gray-500"}`}>
                      {n} / {lo}–{hi} words
                    </span>
                  )}
                </span>
                {s.prompt && <span className="mt-1 block text-xs leading-relaxed text-gray-500">{s.prompt}</span>}
                <textarea
                  value={answers[s.key] ?? ""}
                  onChange={(e) => edit(s.key, e.target.value)}
                  rows={sections.length > 1 ? 6 : 16}
                  spellCheck
                  className="mt-2 w-full resize-y rounded-lg border border-console-line bg-console-2 p-3 font-sans text-[15px] leading-relaxed text-gray-100 placeholder:text-gray-600 focus:border-emerald-400/60 focus:outline-none"
                  placeholder="Write in your own words. First drafts are yours; that's the rule at the labs too."
                />
              </label>
            );
          })}
        </div>
        {error && <p className="mt-4 rounded-lg bg-red-500/10 p-3 text-sm text-red-300">{error}</p>}
        {busy && (
          <p className="mt-5 flex items-center gap-3 font-mono text-sm text-gray-400">
            <span className="h-3 w-3 animate-spin rounded-full border-2 border-emerald-400 border-t-transparent" />
            A reviewer is reading your answer (about 20 seconds)…
          </p>
        )}
        <div ref={reportRef}>{grade && !busy && <GradeReport grade={grade} />}</div>
      </div>
    </>
  );
}

export function RoleplayChat({
  id,
  moduleSlug,
  lessonSlug,
  persona,
  opening,
  maxTurns,
  onPass,
}: {
  id: string;
  moduleSlug: string;
  lessonSlug: string;
  persona: PracticePersona;
  opening: string;
  maxTurns: number;
  onPass: () => void;
}) {
  const start: TranscriptLine[] = [{ from: "persona", text: opening }];
  const [lines, setLines] = useState<TranscriptLine[]>(start);
  const [draft, setDraft] = useState("");
  const [grade, setGrade] = useState<GradeResult | null>(null);
  const [closed, setClosed] = useState(false);
  const [busy, setBusy] = useState<null | "reply" | "grade">(null);
  const [error, setError] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const saved = loadSaved(id);
    setLines(saved.transcript?.length ? saved.transcript : [{ from: "persona", text: opening }]);
    setGrade(saved.grade ?? null);
    setClosed(Boolean(saved.grade));
  }, [id, opening]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [lines, busy, grade]);

  const persist = (transcript: TranscriptLine[], g: GradeResult | null) => saveCode(id, JSON.stringify({ transcript, grade: g }));
  const turns = lines.filter((l) => l.from === "learner").length;

  const send = async () => {
    const text = draft.trim();
    if (!text || busy) return;
    const next: TranscriptLine[] = [...lines, { from: "learner", text }];
    setLines(next);
    setDraft("");
    setError(null);
    setBusy("reply");
    persist(next, null);
    const r = await callCoach({ module: moduleSlug, lesson: lessonSlug, action: "reply", transcript: next });
    setBusy(null);
    if (r.error || !r.reply) {
      setError(r.error ?? "No reply came back. Send your message again.");
      setLines(lines);
      setDraft(text);
      persist(lines, null);
      return;
    }
    const withReply: TranscriptLine[] = [...next, { from: "persona", text: r.reply }];
    setLines(withReply);
    persist(withReply, null);
    if (r.done) setClosed(true);
  };

  const finish = async () => {
    setBusy("grade");
    setError(null);
    setClosed(true);
    const r = await callCoach({ module: moduleSlug, lesson: lessonSlug, action: "grade", transcript: lines });
    setBusy(null);
    if (r.error || !r.result) {
      setError(r.error ?? "No feedback came back. Try again.");
      return;
    }
    setGrade(r.result);
    persist(lines, r.result);
    if (r.result.passed) onPass();
  };

  const restart = () => {
    if (turns > 0 && !confirm("Start a new session? This conversation will be cleared.")) return;
    setLines(start);
    setGrade(null);
    setClosed(false);
    setDraft("");
    setError(null);
    persist(start, null);
  };

  return (
    <>
      <PaneHeader
        title="live session"
        right={
          <>
            <span className="font-mono text-[11px] text-gray-500">
              turn {Math.min(turns, maxTurns)} / {maxTurns}
            </span>
            <button onClick={restart} className="rounded-md px-2 py-1 text-xs text-gray-500 hover:bg-console-2 hover:text-gray-300">
              Restart
            </button>
            <button
              onClick={finish}
              disabled={busy !== null || turns < 2 || Boolean(grade)}
              title={turns < 2 ? "Answer at least two questions first" : "End the session and get scored"}
              className="rounded-md bg-emerald-500 px-3 py-1.5 text-xs font-semibold text-console hover:bg-emerald-400 disabled:opacity-50"
            >
              {busy === "grade" ? "Scoring…" : "End and get feedback"}
            </button>
          </>
        }
      />
      <div className="min-h-0 flex-1 overflow-y-auto p-4">
        <ul className="space-y-4">
          {lines.map((l, i) =>
            l.from === "persona" ? (
              <li key={i} className="flex gap-3">
                <Avatar name={persona.name} size="sm" dark />
                <div className="min-w-0 max-w-[85%]">
                  <div className="text-[11px] text-gray-500">
                    <span className="font-semibold text-gray-300">{persona.name}</span> · {persona.role}
                  </div>
                  <p className="mt-1 whitespace-pre-wrap rounded-xl rounded-tl-sm bg-console-2 px-3.5 py-2.5 text-[15px] leading-relaxed text-gray-100">{l.text}</p>
                </div>
              </li>
            ) : (
              <li key={i} className="flex justify-end">
                <p className="max-w-[85%] whitespace-pre-wrap rounded-xl rounded-tr-sm bg-emerald-500/15 px-3.5 py-2.5 text-[15px] leading-relaxed text-emerald-50">{l.text}</p>
              </li>
            ),
          )}
          {busy === "reply" && (
            <li className="flex items-center gap-2 pl-11 font-mono text-xs text-gray-500">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-gray-400" />
              {persona.name} is thinking…
            </li>
          )}
        </ul>
        {error && <p className="mt-4 rounded-lg bg-red-500/10 p-3 text-sm text-red-300">{error}</p>}
        {busy === "grade" && (
          <p className="mt-5 flex items-center gap-3 font-mono text-sm text-gray-400">
            <span className="h-3 w-3 animate-spin rounded-full border-2 border-emerald-400 border-t-transparent" />
            Scoring your session (about 20 seconds)…
          </p>
        )}
        {grade && busy === null && <GradeReport grade={grade} />}
        <div ref={endRef} />
      </div>
      {!closed && (
        <div className="shrink-0 border-t border-console-line p-3">
          <div className="flex items-end gap-2">
            <textarea
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  void send();
                }
              }}
              rows={3}
              placeholder={`Answer ${persona.name.split(" ")[0]}… (Enter to send, Shift+Enter for a new line)`}
              className="min-w-0 flex-1 resize-none rounded-lg border border-console-line bg-console-2 p-3 text-[15px] leading-relaxed text-gray-100 placeholder:text-gray-600 focus:border-emerald-400/60 focus:outline-none"
            />
            <button
              onClick={() => void send()}
              disabled={busy !== null || !draft.trim()}
              className="rounded-lg bg-emerald-500 px-4 py-3 text-sm font-semibold text-console hover:bg-emerald-400 disabled:opacity-50"
            >
              Send
            </button>
          </div>
        </div>
      )}
    </>
  );
}

export function GradeReport({ grade }: { grade: GradeResult }) {
  const delay = (i: number) => ({ animationDelay: `${120 + i * 110}ms` });
  return (
    <div className="mt-6 overflow-hidden rounded-xl border border-console-line">
      <div className={`flex items-center gap-4 px-4 py-3 ${grade.passed ? "bg-emerald-400/10" : "bg-amber-400/10"}`}>
        <span className={`font-serif text-3xl font-semibold ${grade.passed ? "text-emerald-300" : "text-amber-300"}`}>{grade.percent}%</span>
        <div className="min-w-0">
          <div className={`font-mono text-[11px] uppercase tracking-wider ${grade.passed ? "text-emerald-300" : "text-amber-300"}`}>
            {grade.passed ? "Passed · interview-ready" : "Not yet · revise and resubmit"}
          </div>
          <p className="mt-0.5 text-sm text-gray-300">{grade.summary}</p>
        </div>
      </div>
      <ul className="divide-y divide-console-line">
        {grade.criteria.map((c, i) => (
          <li key={c.name} className="check-in px-4 py-3" style={delay(i)}>
            <div className="flex items-baseline justify-between gap-3">
              <span className="text-sm font-medium text-gray-100">{c.name}</span>
              <span className="font-mono text-xs text-gray-400">
                {c.score} / {c.points}
              </span>
            </div>
            <div className="mt-1.5 h-1.5 rounded-full bg-console-2">
              <div
                className={`bar-fill h-1.5 rounded-full ${c.score / c.points >= 0.7 ? "bg-emerald-400" : c.score / c.points >= 0.4 ? "bg-amber-400" : "bg-red-400/80"}`}
                style={{ width: `${(c.score / c.points) * 100}%`, ...delay(i) }}
              />
            </div>
            <p className="mt-2 text-[13px] leading-relaxed text-gray-400">{c.feedback}</p>
          </li>
        ))}
      </ul>
      <div className="grid gap-px bg-console-line sm:grid-cols-2">
        <div className="bg-console p-4">
          <div className="font-mono text-[11px] uppercase tracking-wider text-emerald-300">Strongest point</div>
          <p className="mt-1 text-sm leading-relaxed text-gray-300">{grade.strengths}</p>
        </div>
        <div className="bg-console p-4">
          <div className="font-mono text-[11px] uppercase tracking-wider text-amber-300">Fix this first</div>
          <p className="mt-1 text-sm leading-relaxed text-gray-300">{grade.fixFirst}</p>
        </div>
      </div>
    </div>
  );
}

/** The rubric, shown on the lesson page so learners know how they'll be judged. */
export function RubricCard({ rubric, passScore }: { rubric: { name: string; points: number; lookFor: string }[]; passScore: number }) {
  const max = rubric.reduce((s, r) => s + r.points, 0);
  return (
    <div className="mt-10 rounded-2xl border border-rule bg-white/60 p-5">
      <div className="flex items-baseline justify-between gap-4">
        <h3 className="font-serif text-lg font-semibold">How you&apos;ll be graded</h3>
        <span className="text-xs text-graphite-3">
          Pass: {passScore}% of {max} points
        </span>
      </div>
      <ul className="mt-3 space-y-3">
        {rubric.map((r) => (
          <li key={r.name} className="flex gap-3 text-[15px] leading-relaxed text-graphite-2">
            <span className="mt-0.5 w-10 shrink-0 font-mono text-xs font-semibold text-vermilion">{r.points} pt</span>
            <span>
              <span className="font-semibold text-graphite">{r.name}.</span> {r.lookFor}
            </span>
          </li>
        ))}
      </ul>
      <p className="mt-4 text-xs text-graphite-3">Graded by Claude against this rubric. Treat the score as practice feedback, not a prediction of any real interview.</p>
    </div>
  );
}
