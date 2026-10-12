"use client";

// Browser-side helpers shared by the lesson workspace, the AI practice panes and the drill:
// safe localStorage, attempt history (server first, localStorage fallback), loop mode and hard mode.
// Every server call degrades gracefully: { disabled: true }, 401, 404 or offline all fall back to local data.

import { useCallback, useEffect, useState } from "react";
import { MOCK_LOOP_MODULES } from "@/lib/config";
import type { Attempt, AttemptsResponse, DrillAttempt, DrillAttemptInput, GradeResult } from "@/lib/coach-types";

export function readLocal<T>(key: string, fallback: T): T {
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

export function writeLocal(key: string, value: unknown) {
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Storage blocked (private mode): the value lasts for this visit only.
  }
}

/** A boolean preference remembered in this browser (voice mode, hard mode). Off until loaded. */
export function useLocalFlag(key: string): [boolean, (v: boolean) => void] {
  const [on, setOn] = useState(false);
  useEffect(() => {
    setOn(readLocal<boolean>(key, false) === true);
  }, [key]);
  const set = useCallback(
    (v: boolean) => {
      setOn(v);
      writeLocal(key, v);
    },
    [key],
  );
  return [on, set];
}

export const useHardMode = () => useLocalFlag("fde-hard-mode-v1");

// ---------- Attempt history ----------

/** null = the server isn't recording attempts (dev mode, signed out, table missing, offline). */
export async function fetchAttempts(lessonId: string): Promise<AttemptsResponse | null> {
  try {
    const res = await fetch(`/api/attempts?lesson=${encodeURIComponent(lessonId)}`, { cache: "no-store" });
    if (!res.ok) return null;
    const data = (await res.json()) as Partial<AttemptsResponse> & { disabled?: boolean };
    if (data.disabled || !Array.isArray(data.grades) || !Array.isArray(data.drills)) return null;
    return { grades: data.grades, drills: data.drills };
  } catch {
    return null;
  }
}

/** true when the server stored it; false when attempts are disabled or the call failed. */
export async function postDrillAttempt(body: DrillAttemptInput): Promise<boolean> {
  try {
    const res = await fetch("/api/attempts", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body), keepalive: true });
    if (!res.ok) return false;
    const data = (await res.json().catch(() => ({}))) as { ok?: boolean };
    return data.ok === true;
  } catch {
    return false;
  }
}

/** A grade as the history panel shows it; built from server rows or this browser's copy. */
export interface GradeEntry {
  id: string;
  percent: number;
  passed: boolean;
  createdAt: string;
  loopMode: boolean;
  result: Attempt["result"];
}

const gradeKey = (lessonId: string) => `fde-grades-v1:${lessonId}`;
const MAX_LOCAL_GRADES = 30;

export function localGrades(lessonId: string): GradeEntry[] {
  const list = readLocal<GradeEntry[]>(gradeKey(lessonId), []);
  return Array.isArray(list) ? list : [];
}

function fromServer(a: Attempt): GradeEntry {
  return { id: `s${a.id}`, percent: a.percent, passed: a.passed, createdAt: a.created_at, loopMode: a.loop_mode, result: a.result ?? { criteria: [] } };
}

/**
 * Every graded attempt for a lesson, newest first. Uses the server's list when attempts are
 * recorded there, otherwise this browser's copy. Grades are always copied locally too, so a
 * restart or "Submit again" never loses one.
 */
export function useGradeHistory(lessonId: string) {
  const [entries, setEntries] = useState<GradeEntry[]>([]);
  const [server, setServer] = useState(false);

  useEffect(() => {
    let live = true;
    setEntries(localGrades(lessonId));
    void fetchAttempts(lessonId).then((r) => {
      if (!live || !r) return;
      setServer(true);
      setEntries(r.grades.map(fromServer));
    });
    return () => {
      live = false;
    };
  }, [lessonId]);

  const add = useCallback(
    (result: GradeResult, loopMode: boolean, serverId: number | null) => {
      const entry: GradeEntry = {
        id: serverId != null ? `s${serverId}` : `l${Date.now()}`,
        percent: result.percent,
        passed: result.passed,
        createdAt: new Date().toISOString(),
        loopMode,
        result: { criteria: result.criteria, summary: result.summary, strengths: result.strengths, fixFirst: result.fixFirst },
      };
      writeLocal(gradeKey(lessonId), [entry, ...localGrades(lessonId)].slice(0, MAX_LOCAL_GRADES));
      setEntries((list) => [entry, ...list.filter((e) => e.id !== entry.id)]);
    },
    [lessonId],
  );

  return { entries, server, add };
}

/** "Attempt N · first attempt X% · previous Y%", from the server's numbers or the local history. */
export interface AttemptLine {
  n: number;
  first: number | null;
  previous: number | null;
}

export function attemptLineFromHistory(history: GradeEntry[]): AttemptLine {
  // history is newest first and already includes the attempt being described.
  const n = history.length;
  return { n, first: n > 1 ? history[n - 1].percent : null, previous: n > 1 ? history[1].percent : null };
}

// ---------- Drill history (local copy) ----------

export interface DrillRun {
  startedAt: number;
  finishedAt: number | null;
  timeLimitMin: number;
  extended: boolean;
  levelMs: number[];
  cleared: number;
  clearedInTime: number;
  loopMode: boolean;
}

const drillRunsKey = (lessonId: string) => `fde-drill-runs-v1:${lessonId}`;

export function localDrillRuns(lessonId: string): DrillRun[] {
  const list = readLocal<DrillRun[]>(drillRunsKey(lessonId), []);
  return Array.isArray(list) ? list : [];
}

export function saveLocalDrillRun(lessonId: string, run: DrillRun) {
  const rest = localDrillRuns(lessonId).filter((r) => r.startedAt !== run.startedAt);
  writeLocal(drillRunsKey(lessonId), [run, ...rest].slice(0, 30));
}

export function drillRunFromServer(d: DrillAttempt): DrillRun {
  return {
    startedAt: Date.parse(d.started_at),
    finishedAt: d.finished_at ? Date.parse(d.finished_at) : null,
    timeLimitMin: d.time_limit_min,
    extended: d.extended,
    levelMs: d.level_ms ?? [],
    cleared: d.cleared,
    clearedInTime: d.cleared_in_time,
    loopMode: d.loop_mode,
  };
}

// ---------- Loop mode ----------

export interface LoopState {
  track?: string;
  startedAt: string;
}

/**
 * Reads profile.loopMode from /api/profile. The loop applies to this lesson only when the lesson
 * is in its track's mock-loop module. A missing route (404) or { disabled: true } means no loop.
 */
/** Same key as components/SiteProfile.tsx PROFILE_KEY. */
const LOCAL_PROFILE_KEY = "fde-profile-v1";

export function useLoopMode(moduleSlug: string, track: string) {
  const [loop, setLoop] = useState<LoopState | null>(null);

  useEffect(() => {
    let live = true;
    (async () => {
      try {
        const res = await fetch("/api/profile", { cache: "no-store" });
        if (res.ok) {
          const data = (await res.json()) as { disabled?: boolean; profile?: { loopMode?: LoopState | null } | null };
          if (!data.disabled) {
            const lm = data.profile?.loopMode ?? null;
            if (live && lm && typeof lm.startedAt === "string") setLoop(lm);
            return;
          }
        }
      } catch {
        // No profile service: fall back to the browser copy below.
      }
      // Dev mode, signed out, or no profiles table: the dashboard keeps the profile in localStorage.
      try {
        const raw = window.localStorage.getItem(LOCAL_PROFILE_KEY);
        const lm = raw ? ((JSON.parse(raw) as { loopMode?: LoopState | null }).loopMode ?? null) : null;
        if (live && lm && typeof lm.startedAt === "string") setLoop(lm);
      } catch {
        // Storage blocked: no loop.
      }
    })();
    return () => {
      live = false;
    };
  }, []);

  const inLoopModule = (MOCK_LOOP_MODULES as readonly string[]).includes(moduleSlug);
  const active = Boolean(loop && inLoopModule && (!loop.track || loop.track === track));

  const end = useCallback(async () => {
    try {
      await fetch("/api/profile", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ loopMode: null }) });
    } catch {
      // Offline: end it in this tab anyway.
    }
    try {
      const raw = window.localStorage.getItem(LOCAL_PROFILE_KEY);
      if (raw) window.localStorage.setItem(LOCAL_PROFILE_KEY, JSON.stringify({ ...JSON.parse(raw), loopMode: null }));
    } catch {
      // Storage blocked: nothing to clear.
    }
    setLoop(null);
  }, []);

  return { loop, active, end };
}

export const clock = (ms: number) => {
  const t = Math.max(0, Math.round(ms / 1000));
  const h = Math.floor(t / 3600);
  const m = Math.floor((t % 3600) / 60);
  const sec = String(t % 60).padStart(2, "0");
  return h ? `${h}:${String(m).padStart(2, "0")}:${sec}` : `${m}:${sec}`;
};

/** Re-renders every second while `on`, returning the current time. */
export function useTicker(on: boolean): number {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    if (!on) return;
    setNow(Date.now());
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, [on]);
  return now;
}
