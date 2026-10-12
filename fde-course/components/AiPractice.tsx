"use client";

// Right-hand panes for Claude-graded lessons:
//   AnswerSheet    written answers (one or more sections, optional diagram), graded against the lesson's rubric
//   RoleplayChat   a conversation with a persona (optionally spoken, optionally a timed design interview), then a rubric debrief
// Drafts, transcripts and the last grade are saved like code (lib/progress), so they survive reloads
// and sync to the learner's account. Every graded attempt is also kept in the attempt history
// (server when recorded there, this browser otherwise), so "Restart" and "Submit again" never lose a score.

import { useCallback, useEffect, useRef, useState } from "react";
import type { AttemptInfo, CoachGrade, CoachReply, GradeResult, TranscriptLine } from "@/lib/coach-types";
import { getSavedCode, saveCode } from "@/lib/progress";
import { Avatar } from "./Playbook";
import { GradeHistory } from "./AttemptHistory";
import DesignBoard, { DIAGRAM_MAX } from "./DesignBoard";
import { AnswerTimer, VoiceToggle, VoiceUnsupportedNote, speak, stopSpeaking, useDictation, useSpeechSupport, useVoiceMode } from "./VoiceInput";
import { attemptLineFromHistory, clock, useGradeHistory, useTicker, type AttemptLine, type GradeEntry } from "./practice-shared";

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

/** Loop mode as the practice panes need it: whether it applies here, and when the loop began. */
export interface PracticeLoop {
  active: boolean;
  startedAt?: string;
}

/** A transcript line in the browser. "note" lines (clock nudges) are local and never sent. */
interface ChatLine {
  from: "persona" | "learner" | "note";
  text: string;
  sig?: string;
  constraint?: string;
}

interface Saved {
  answers?: Record<string, string>;
  transcript?: ChatLine[];
  grade?: GradeResult | null;
  attempt?: AttemptLine | null;
  loopScore?: boolean;
  diagram?: string;
  startedAt?: number | null;
  nudged?: number[];
}

function loadSaved(id: string): Saved {
  try {
    return JSON.parse(getSavedCode(id) ?? "{}") as Saved;
  } catch {
    return {};
  }
}

const words = (s: string) => (s.trim() ? s.trim().split(/\s+/).length : 0);

const TAMPERED_HINT = "changed outside the app";

type CoachResult<T> = { data: T; error?: undefined } | { data?: undefined; error: string; status: number };

async function callCoach<T>(body: Record<string, unknown>): Promise<CoachResult<T>> {
  try {
    const res = await fetch("/api/coach", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) return { error: (data as { error?: string }).error ?? `Request failed (${res.status}).`, status: res.status };
    return { data: data as T };
  } catch {
    return { error: "Couldn't reach the server. Check your connection and try again.", status: 0 };
  }
}

/** Only the first graded attempt per lesson during a loop counts as the loop score. */
function isLoopScore(loop: PracticeLoop, history: GradeEntry[]): boolean {
  if (!loop.active) return false;
  const since = loop.startedAt ? Date.parse(loop.startedAt) : 0;
  return !history.some((e) => e.loopMode && Date.parse(e.createdAt) >= since);
}

function attemptLine(info: AttemptInfo | undefined, history: GradeEntry[]): AttemptLine {
  if (info && info.n > 0) return { n: info.n, first: info.n > 1 ? (info.first?.percent ?? null) : null, previous: info.previous?.percent ?? null };
  return attemptLineFromHistory(history);
}

const announceGrade = (g: GradeResult) => `Scored ${g.percent} percent. ${g.passed ? "Passed this rubric." : "Not yet."} ${g.summary}`;

function PaneHeader({ title, right }: { title: string; right?: React.ReactNode }) {
  return (
    <div className="flex min-h-12 shrink-0 flex-wrap items-center gap-x-3 gap-y-1.5 border-b border-console-line px-4 py-2 text-sm">
      <div className="hidden gap-1.5 sm:flex" aria-hidden="true">
        <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" />
        <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" />
        <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]" />
      </div>
      <span className="rounded-md bg-console-2 px-2.5 py-1 font-mono text-xs text-gray-300">{title}</span>
      <div className="ml-auto flex flex-wrap items-center justify-end gap-2">{right}</div>
    </div>
  );
}

function Spinner({ children }: { children: React.ReactNode }) {
  return (
    <p className="mt-5 flex items-center gap-3 font-mono text-sm text-gray-300">
      <span aria-hidden="true" className="h-3 w-3 animate-spin rounded-full border-2 border-emerald-400 border-t-transparent" />
      {children}
    </p>
  );
}

function ErrorNote({ children, action }: { children: React.ReactNode; action?: React.ReactNode }) {
  return (
    <div role="alert" className="mt-4 flex flex-wrap items-center gap-3 rounded-lg bg-red-500/10 p-3 text-sm text-red-200">
      <span className="min-w-0 flex-1">{children}</span>
      {action}
    </div>
  );
}

export function AnswerSheet({
  id,
  moduleSlug,
  lessonSlug,
  sections,
  diagram = false,
  loop = { active: false },
  onPass,
}: {
  id: string;
  moduleSlug: string;
  lessonSlug: string;
  sections: PracticeSection[];
  /** Show a diagram box; its text is sent as answers.diagram. */
  diagram?: boolean;
  loop?: PracticeLoop;
  onPass: () => void;
}) {
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [board, setBoard] = useState("");
  const [grade, setGrade] = useState<GradeResult | null>(null);
  const [attempt, setAttempt] = useState<AttemptLine | null>(null);
  const [loopScore, setLoopScore] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [announce, setAnnounce] = useState("");
  const reportRef = useRef<HTMLDivElement>(null);
  const history = useGradeHistory(id);

  useEffect(() => {
    const saved = loadSaved(id);
    setAnswers(saved.answers ?? {});
    setBoard(saved.diagram ?? "");
    setGrade(saved.grade ?? null);
    setAttempt(saved.attempt ?? null);
    setLoopScore(Boolean(saved.loopScore));
  }, [id]);

  const persist = (next: Saved) => saveCode(id, JSON.stringify(next));
  const snapshot = (over: Partial<Saved> = {}): Saved => ({ answers, diagram: board, grade, attempt, loopScore, ...over });

  const edit = (key: string, value: string) => {
    const next = { ...answers, [key]: value };
    setAnswers(next);
    persist(snapshot({ answers: next }));
  };

  const editBoard = (value: string) => {
    setBoard(value);
    persist(snapshot({ diagram: value }));
  };

  const submit = async () => {
    setBusy(true);
    setError(null);
    const asLoop = isLoopScore(loop, history.entries);
    const sent = diagram && board.trim() ? { ...answers, diagram: board.slice(0, DIAGRAM_MAX) } : answers;
    const r = await callCoach<CoachGrade>({ module: moduleSlug, lesson: lessonSlug, action: "grade", answers: sent, loopMode: asLoop });
    setBusy(false);
    if (r.error !== undefined || !r.data.result) {
      setError(r.error ?? "No result came back. Try again.");
      return;
    }
    const result = r.data.result;
    const entry: GradeEntry = { id: "pending", percent: result.percent, passed: result.passed, createdAt: new Date().toISOString(), loopMode: asLoop, result };
    const line = attemptLine(r.data.attempt, [entry, ...history.entries]);
    history.add(result, asLoop, r.data.attempt?.id ?? null);
    setGrade(result);
    setAttempt(line);
    setLoopScore(asLoop);
    persist(snapshot({ grade: result, attempt: line, loopScore: asLoop }));
    setAnnounce(announceGrade(result));
    if (result.passed) onPass();
    setTimeout(() => reportRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 50);
  };

  const total = sections.reduce((n, s) => n + words(answers[s.key] ?? ""), 0);
  const empty = total === 0 && !(diagram && board.trim());

  return (
    <>
      <PaneHeader
        title="answer.md"
        right={
          <>
            <span className="font-mono text-[11px] text-console-muted">{total} words</span>
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
                    <span className={`font-mono text-[11px] ${off ? "text-amber-300" : "text-console-muted"}`}>
                      {n} / {lo}–{hi} words
                    </span>
                  )}
                </span>
                {s.prompt && <span className="mt-1 block text-xs leading-relaxed text-console-muted">{s.prompt}</span>}
                <textarea
                  value={answers[s.key] ?? ""}
                  onChange={(e) => edit(s.key, e.target.value)}
                  rows={sections.length > 1 || diagram ? 6 : 16}
                  spellCheck
                  className="mt-2 w-full resize-y rounded-lg border border-console-line bg-console-2 p-3 font-sans text-[15px] leading-relaxed text-gray-100 placeholder:text-console-muted focus:border-emerald-400/60 focus:outline-none"
                  placeholder="Write in your own words. First drafts are yours; that's the rule at the labs too."
                />
              </label>
            );
          })}
          {diagram && (
            <div className="-mx-4 flex flex-col">
              <DesignBoard id={`${id}-diagram`} value={board} onChange={editBoard} rows={10} />
            </div>
          )}
        </div>
        {error && <ErrorNote>{error}</ErrorNote>}
        {busy && <Spinner>A reviewer is reading your answer (about 20 seconds)…</Spinner>}
        <div ref={reportRef}>{grade && !busy && <GradeReport grade={grade} attempt={attempt} loopScore={loopScore} />}</div>
        <GradeHistory entries={history.entries} server={history.server} />
        <p className="sr-only" aria-live="polite">
          {announce}
        </p>
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
  timeLimit = 0,
  design = false,
  diagram = false,
  loop = { active: false },
  onPass,
}: {
  id: string;
  moduleSlug: string;
  lessonSlug: string;
  persona: PracticePersona;
  opening: string;
  maxTurns: number;
  /** Minutes on the session clock; 0 = untimed. */
  timeLimit?: number;
  /** Interactive design interview: whiteboard, constraints, clock. */
  design?: boolean;
  /** Show the whiteboard (always on in design mode). */
  diagram?: boolean;
  loop?: PracticeLoop;
  onPass: () => void;
}) {
  const first = persona.name.split(" ")[0];
  const showBoard = design || diagram;
  const limitMs = timeLimit > 0 ? timeLimit * 60_000 : 0;

  const [lines, setLines] = useState<ChatLine[]>([{ from: "persona", text: opening }]);
  const [draft, setDraft] = useState("");
  const [board, setBoard] = useState("");
  const [grade, setGrade] = useState<GradeResult | null>(null);
  const [attempt, setAttempt] = useState<AttemptLine | null>(null);
  const [loopScore, setLoopScore] = useState(false);
  const [closed, setClosed] = useState(false);
  const [busy, setBusy] = useState<null | "reply" | "grade">(null);
  const [error, setError] = useState<string | null>(null);
  const [tampered, setTampered] = useState(false);
  const [startedAt, setStartedAt] = useState<number | null>(null);
  const [nudged, setNudged] = useState<number[]>([]);
  const [answerSince, setAnswerSince] = useState<number | null>(null);
  const [boardOpen, setBoardOpen] = useState(true);
  const [announce, setAnnounce] = useState("");
  const endRef = useRef<HTMLDivElement>(null);
  const history = useGradeHistory(id);

  const support = useSpeechSupport();
  const [voicePref, setVoicePref] = useVoiceMode();
  const voiceOn = voicePref && Boolean(support?.recognition);
  const dictation = useDictation(
    useCallback((text: string) => {
      if (!text) return;
      setDraft((d) => (d.trim() ? `${d.replace(/\s+$/, "")} ${text}` : text));
      setAnswerSince((t) => t ?? Date.now());
    }, []),
  );

  useEffect(() => {
    const saved = loadSaved(id);
    setLines(saved.transcript?.length ? saved.transcript : [{ from: "persona", text: opening }]);
    setGrade(saved.grade ?? null);
    setAttempt(saved.attempt ?? null);
    setLoopScore(Boolean(saved.loopScore));
    setClosed(Boolean(saved.grade));
    setBoard(saved.diagram ?? "");
    setStartedAt(saved.startedAt ?? null);
    setNudged(saved.nudged ?? []);
  }, [id, opening]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [lines, busy, grade]);

  // Stop talking when leaving the page or switching voice off.
  useEffect(() => () => stopSpeaking(), []);

  const persist = (over: Partial<Saved>) =>
    saveCode(id, JSON.stringify({ transcript: lines, grade, attempt, loopScore, diagram: board, startedAt, nudged, ...over } satisfies Saved));
  const turns = lines.filter((l) => l.from === "learner").length;
  const wire = (ls: ChatLine[]): TranscriptLine[] =>
    ls.filter((l) => l.from !== "note").map((l) => (l.sig ? { from: l.from as TranscriptLine["from"], text: l.text, sig: l.sig } : { from: l.from as TranscriptLine["from"], text: l.text }));
  const diagramField = () => (showBoard && board.trim() ? { diagram: board.slice(0, DIAGRAM_MAX) } : {});
  const constraints = lines.filter((l) => l.constraint).map((l) => l.constraint as string);

  const clockRunning = limitMs > 0 && startedAt !== null && !grade;
  const timerRunning = voiceOn && answerSince !== null && !closed;
  const now = useTicker(clockRunning || timerRunning);
  const elapsed = startedAt !== null ? now - startedAt : 0;

  const fail = (msg: string) => {
    setError(msg);
    if (msg.includes(TAMPERED_HINT)) setTampered(true);
  };

  const ensureStarted = () => {
    if (limitMs > 0 && startedAt === null) {
      const t = Date.now();
      setStartedAt(t);
      return t;
    }
    return startedAt;
  };

  const send = async () => {
    const text = draft.trim();
    if (!text || busy) return;
    dictation.stop();
    stopSpeaking();
    const started = ensureStarted();
    const next: ChatLine[] = [...lines, { from: "learner", text }];
    setLines(next);
    setDraft("");
    setError(null);
    setAnswerSince(null);
    setBusy("reply");
    persist({ transcript: next, grade: null, startedAt: started });
    const r = await callCoach<CoachReply>({
      module: moduleSlug,
      lesson: lessonSlug,
      action: "reply",
      transcript: wire(next),
      ...diagramField(),
      ...(started !== null ? { startedAt: started } : {}),
      loopMode: loop.active,
    });
    setBusy(null);
    if (r.error !== undefined || !r.data.reply) {
      fail(r.error ?? "No reply came back. Send your message again.");
      setLines(lines);
      setDraft(text);
      persist({ transcript: lines, grade: null, startedAt: started });
      return;
    }
    const { reply, sig, done, constraint } = r.data;
    const withReply: ChatLine[] = [...next, { from: "persona", text: reply, sig, ...(constraint ? { constraint } : {}) }];
    setLines(withReply);
    persist({ transcript: withReply, grade: null, startedAt: started });
    setAnnounce(`${constraint ? "New constraint. " : ""}${persona.name}: ${reply}`);
    if (voiceOn && support?.synthesis) speak(reply, () => setAnswerSince(Date.now()));
    else setAnswerSince(Date.now());
    if (done) {
      setClosed(true);
      setAnnounce((a) => `${a} The session is over. Press End and get feedback for your score.`);
    }
  };

  const finish = useCallback(
    async (transcript: ChatLine[] = lines) => {
      dictation.stop();
      stopSpeaking();
      setBusy("grade");
      setError(null);
      setClosed(true);
      const asLoop = isLoopScore(loop, history.entries);
      const r = await callCoach<CoachGrade>({
        module: moduleSlug,
        lesson: lessonSlug,
        action: "grade",
        transcript: wire(transcript),
        ...diagramField(),
        ...(startedAt !== null ? { startedAt } : {}),
        loopMode: asLoop,
      });
      setBusy(null);
      if (r.error !== undefined || !r.data.result) {
        fail(r.error ?? "No feedback came back. Try again.");
        return;
      }
      const result = r.data.result;
      const entry: GradeEntry = { id: "pending", percent: result.percent, passed: result.passed, createdAt: new Date().toISOString(), loopMode: asLoop, result };
      const line = attemptLine(r.data.attempt, [entry, ...history.entries]);
      history.add(result, asLoop, r.data.attempt?.id ?? null);
      setGrade(result);
      setAttempt(line);
      setLoopScore(asLoop);
      persist({ transcript, grade: result, attempt: line, loopScore: asLoop });
      setAnnounce(announceGrade(result));
      if (result.passed) onPass();
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [lines, loop, history, startedAt, board, moduleSlug, lessonSlug, onPass],
  );

  // Session clock: nudges at 50% and 80%, then close and score at time-up.
  useEffect(() => {
    if (!clockRunning || busy) return;
    const pct = (elapsed / limitMs) * 100;
    const due = [50, 80, 100].filter((p) => pct >= p && !nudged.includes(p));
    if (!due.length) return;
    const left = Math.max(0, Math.ceil((limitMs - elapsed) / 60_000));
    const notes: ChatLine[] = due.map((p) => ({
      from: "note",
      text:
        p === 50
          ? `Halfway: about ${left} minutes left. ${design ? "If the whole design isn't on the board yet, sketch the end-to-end path before going deep." : "Make sure you've covered the core of the question."}`
          : p === 80
            ? `About ${left} minutes left. Start landing it: the biggest risk, what you'd measure, and what you'd do next.`
            : "Time's up. The interviewer is closing the session and scoring it.",
    }));
    const nextNudged = [...nudged, ...due];
    const nextLines = [...lines, ...notes];
    setNudged(nextNudged);
    setLines(nextLines);
    persist({ transcript: nextLines, nudged: nextNudged });
    setAnnounce(notes.map((n) => n.text).join(" "));
    if (due.includes(100)) {
      if (turns >= 1 && !grade) void finish(nextLines);
      else setClosed(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clockRunning, elapsed, busy]);

  const restart = () => {
    const unsaved = turns > 0 && !grade;
    if (unsaved && !confirm("Start a new session? This conversation and whiteboard will be cleared. Graded attempts stay in your attempt history.")) return;
    dictation.stop();
    stopSpeaking();
    const start: ChatLine[] = [{ from: "persona", text: opening }];
    setLines(start);
    setGrade(null);
    setAttempt(null);
    setLoopScore(false);
    setClosed(false);
    setDraft("");
    setBoard("");
    setError(null);
    setTampered(false);
    setStartedAt(null);
    setNudged([]);
    setAnswerSince(null);
    saveCode(id, JSON.stringify({ transcript: start, grade: null, diagram: "", startedAt: null, nudged: [] } satisfies Saved));
  };

  const editBoard = (v: string) => {
    setBoard(v);
    const started = ensureStarted();
    persist({ diagram: v, startedAt: started });
  };

  const toggleVoice = (v: boolean) => {
    setVoicePref(v);
    if (!v) {
      dictation.stop();
      stopSpeaking();
    }
  };

  return (
    <>
      <PaneHeader
        title={design ? "design interview" : "live session"}
        right={
          <>
            {limitMs > 0 && (
              <span
                className={`rounded-md px-2 py-1 font-mono text-xs tabular-nums ${
                  startedAt === null ? "text-console-muted" : elapsed >= limitMs ? "bg-red-400/15 text-red-200" : elapsed >= limitMs * 0.8 ? "bg-amber-400/15 text-amber-200" : "bg-console-2 text-gray-200"
                }`}
                title={startedAt === null ? "The clock starts with your first reply" : "Time left in this session"}
                aria-label={startedAt === null ? `${timeLimit} minute session, starts with your first reply` : `Time left ${clock(limitMs - elapsed)}`}
              >
                {startedAt === null ? `${timeLimit}:00 · starts when you reply` : elapsed >= limitMs ? "Time's up" : clock(limitMs - elapsed)}
              </span>
            )}
            <span className="font-mono text-[11px] text-console-muted">
              turn {Math.min(turns, maxTurns)} / {maxTurns}
            </span>
            <VoiceToggle support={support} on={voiceOn} onChange={toggleVoice} />
            {showBoard && (
              <button
                type="button"
                aria-pressed={boardOpen}
                onClick={() => setBoardOpen((v) => !v)}
                className="rounded-md px-2 py-1 text-xs text-console-muted hover:bg-console-2 hover:text-gray-200"
              >
                {boardOpen ? "Hide board" : "Show board"}
              </button>
            )}
            <button onClick={restart} className="rounded-md px-2 py-1 text-xs text-console-muted hover:bg-console-2 hover:text-gray-200">
              Restart
            </button>
            <button
              onClick={() => void finish()}
              disabled={busy !== null || turns < 2 || Boolean(grade)}
              title={turns < 2 ? "Answer at least two questions first" : "End the session and get scored"}
              className="rounded-md bg-emerald-500 px-3 py-1.5 text-xs font-semibold text-console hover:bg-emerald-400 disabled:opacity-50"
            >
              {busy === "grade" ? "Scoring…" : "End and get feedback"}
            </button>
          </>
        }
      />
      <VoiceUnsupportedNote support={support} />
      <div className="flex min-h-0 flex-1 flex-col">
        <div className={`min-h-0 overflow-y-auto p-4 ${showBoard && boardOpen ? "flex-[3]" : "flex-1"}`}>
          <ul className="space-y-4" aria-label={`Conversation with ${persona.name}`}>
            {lines.map((l, i) =>
              l.from === "note" ? (
                <li key={i} className="mx-auto max-w-[90%] rounded-lg border border-console-line bg-console-2/60 px-3 py-2 text-center font-mono text-[12px] leading-relaxed text-gray-300">
                  {l.text}
                </li>
              ) : l.from === "persona" ? (
                <li key={i} className="flex gap-3">
                  <Avatar name={persona.name} size="sm" dark />
                  <div className="min-w-0 max-w-[85%]">
                    <div className="flex flex-wrap items-center gap-2 text-[11px] text-console-muted">
                      <span>
                        <span className="font-semibold text-gray-300">{persona.name}</span> · {persona.role}
                      </span>
                      {l.constraint && <span className="rounded bg-amber-400/20 px-1.5 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-wider text-amber-200">New constraint</span>}
                    </div>
                    <p
                      className={`mt-1 whitespace-pre-wrap rounded-xl rounded-tl-sm px-3.5 py-2.5 text-[15px] leading-relaxed text-gray-100 ${
                        l.constraint ? "border border-amber-400/40 bg-amber-400/[0.07]" : "bg-console-2"
                      }`}
                    >
                      {l.text}
                    </p>
                  </div>
                </li>
              ) : (
                <li key={i} className="flex justify-end">
                  <p className="max-w-[85%] whitespace-pre-wrap rounded-xl rounded-tr-sm bg-emerald-500/15 px-3.5 py-2.5 text-[15px] leading-relaxed text-emerald-50">{l.text}</p>
                </li>
              ),
            )}
            {busy === "reply" && (
              <li className="flex items-center gap-2 pl-11 font-mono text-xs text-console-muted">
                <span aria-hidden="true" className="h-1.5 w-1.5 animate-pulse rounded-full bg-gray-400" />
                {persona.name} is thinking…
              </li>
            )}
          </ul>
          {error && (
            <ErrorNote
              action={
                tampered ? (
                  <button onClick={restart} className="rounded-md bg-red-400/20 px-3 py-1 text-xs font-semibold text-red-100 hover:bg-red-400/30">
                    Restart the session
                  </button>
                ) : undefined
              }
            >
              {tampered ? "This conversation was saved before an update and can't be continued. Restart it; your graded attempts stay in your history." : error}
            </ErrorNote>
          )}
          {busy === "grade" && <Spinner>Scoring your session (about 20 seconds)…</Spinner>}
          {grade && busy === null && <GradeReport grade={grade} attempt={attempt} loopScore={loopScore} />}
          <GradeHistory entries={history.entries} server={history.server} />
          <div ref={endRef} />
        </div>
        {showBoard && boardOpen && (
          <div className="flex min-h-0 flex-[2] flex-col overflow-y-auto border-t border-console-line">
            <DesignBoard id={`${id}-board`} value={board} onChange={editBoard} readOnly={Boolean(grade)} constraints={constraints} />
          </div>
        )}
      </div>
      {!closed ? (
        <div className="shrink-0 border-t border-console-line p-3">
          {voiceOn && (
            <div className="mb-2 flex flex-wrap items-center gap-2">
              <button
                type="button"
                aria-pressed={dictation.listening}
                onClick={() => (dictation.listening ? dictation.stop() : dictation.start())}
                className={`flex items-center gap-2 rounded-md px-3 py-1.5 text-xs font-semibold ${dictation.listening ? "bg-red-500/20 text-red-100" : "bg-sky-400/15 text-sky-100 hover:bg-sky-400/25"}`}
              >
                <span aria-hidden="true" className={`h-2 w-2 rounded-full ${dictation.listening ? "animate-pulse bg-red-400" : "bg-sky-300"}`} />
                {dictation.listening ? "Stop recording" : "Speak your answer"}
              </button>
              <AnswerTimer since={answerSince} now={now} />
              <span className="text-[11px] text-console-muted">Edit the text before sending if the transcript is off.</span>
            </div>
          )}
          {voiceOn && dictation.interim && <p className="mb-2 truncate font-mono text-xs italic text-console-muted">…{dictation.interim}</p>}
          {voiceOn && dictation.error && (
            <p role="alert" className="mb-2 text-xs text-amber-200">
              {dictation.error}
            </p>
          )}
          <div className="flex items-end gap-2">
            <label htmlFor={`${id}-draft`} className="sr-only">
              Your answer to {persona.name}
            </label>
            <textarea
              id={`${id}-draft`}
              value={draft}
              onChange={(e) => {
                setDraft(e.target.value);
                if (answerSince === null) setAnswerSince(Date.now());
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  void send();
                }
              }}
              rows={3}
              placeholder={`Answer ${first}… (Enter to send, Shift+Enter for a new line)`}
              className="min-w-0 flex-1 resize-none rounded-lg border border-console-line bg-console-2 p-3 text-[15px] leading-relaxed text-gray-100 placeholder:text-console-muted focus:border-emerald-400/60 focus:outline-none"
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
      ) : (
        !grade &&
        busy === null && (
          <p className="shrink-0 border-t border-console-line px-4 py-3 text-sm text-gray-300">
            The session is closed. {turns >= 2 ? "Press End and get feedback for your score, or Restart." : "Restart to try again."}
          </p>
        )
      )}
      <p className="sr-only" aria-live="polite">
        {announce}
      </p>
    </>
  );
}

export function GradeReport({ grade, attempt, loopScore = false }: { grade: GradeResult; attempt?: AttemptLine | null; loopScore?: boolean }) {
  const delay = (i: number) => ({ animationDelay: `${120 + i * 110}ms` });
  const meta = attempt
    ? [`Attempt ${attempt.n}`, attempt.first !== null ? `first attempt ${attempt.first}%` : null, attempt.previous !== null ? `previous ${attempt.previous}%` : null].filter(Boolean).join(" · ")
    : null;
  return (
    <div className="mt-6 overflow-hidden rounded-xl border border-console-line">
      <div className={`flex items-center gap-4 px-4 py-3 ${grade.passed ? "bg-emerald-400/10" : "bg-amber-400/10"}`}>
        <span className={`font-serif text-3xl font-semibold ${grade.passed ? "text-emerald-300" : "text-amber-300"}`}>{grade.percent}%</span>
        <div className="min-w-0">
          <div className={`flex flex-wrap items-center gap-x-2 font-mono text-[11px] uppercase tracking-wider ${grade.passed ? "text-emerald-300" : "text-amber-300"}`}>
            <span>{grade.passed ? "Passed this rubric" : "Not yet · revise and resubmit"}</span>
            {loopScore && <span className="rounded bg-vermilion/25 px-1.5 py-0.5 text-[10px] text-orange-100">Loop score</span>}
          </div>
          {meta && <div className="mt-0.5 font-mono text-[11px] text-gray-300">{meta}</div>}
          <p className="mt-0.5 text-sm text-gray-300">{grade.summary}</p>
          {grade.graderRuns === 2 && <p className="mt-1 text-[11px] text-console-muted">Close to the pass mark, so it was graded twice and averaged.</p>}
        </div>
      </div>
      <ul className="divide-y divide-console-line">
        {grade.criteria.map((c, i) => (
          <li key={c.name} className="check-in px-4 py-3" style={delay(i)}>
            <div className="flex items-baseline justify-between gap-3">
              <span className="text-sm font-medium text-gray-100">{c.name}</span>
              <span className="font-mono text-xs text-gray-300">
                {c.score} / {c.points}
              </span>
            </div>
            <div className="mt-1.5 h-1.5 rounded-full bg-console-2">
              <div
                className={`bar-fill h-1.5 rounded-full ${c.score / c.points >= 0.7 ? "bg-emerald-400" : c.score / c.points >= 0.4 ? "bg-amber-400" : "bg-red-400/80"}`}
                style={{ width: `${(c.score / c.points) * 100}%`, ...delay(i) }}
              />
            </div>
            <p className="mt-2 text-[13px] leading-relaxed text-gray-300">{c.feedback}</p>
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
