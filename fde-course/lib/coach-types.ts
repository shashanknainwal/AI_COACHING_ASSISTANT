// Shapes shared by /api/coach, /api/attempts and the browser components that call them.

export interface TranscriptLine {
  from: "persona" | "learner";
  text: string;
  /** Persona lines carry the server's HMAC signature (lib/signing.ts). The lesson's opening line needs none. */
  sig?: string;
}

export interface GradeResult {
  criteria: { name: string; points: number; score: number; feedback: string }[];
  total: number;
  max: number;
  percent: number;
  passed: boolean;
  summary: string;
  strengths: string;
  fixFirst: string;
  /** Set when the first grade landed within ±5 of the pass mark and a second grade was averaged in. */
  graderRuns?: number;
}

/** POST /api/coach { action: "reply" } response. */
export interface CoachReply {
  reply: string;
  sig: string;
  done: boolean;
  /** Set when the server injected a design-mode constraint this turn; the reply starts with it. */
  constraint?: string;
}

/** Attempt bookkeeping returned with every grade. All empty in dev mode or before the 0003 migration. */
export interface AttemptInfo {
  id: number | null;
  /** This attempt's number for this learner and lesson (1 = first). 0 when attempts aren't recorded. */
  n: number;
  first: { percent: number; passed: boolean } | null;
  previous: { percent: number } | null;
}

/** POST /api/coach { action: "grade" } response. */
export interface CoachGrade {
  result: GradeResult;
  attempt: AttemptInfo;
}

/** A row of grade_attempts as returned by GET /api/attempts. */
export interface Attempt {
  id: number;
  lesson_id: string;
  track: string | null;
  percent: number;
  passed: boolean;
  /** The list view (no ?lesson=) carries criteria only; the per-lesson view carries the full GradeResult. */
  result: {
    criteria: { name: string; points: number; score: number; feedback?: string }[];
    summary?: string;
    strengths?: string;
    fixFirst?: string;
  };
  created_at: string;
  loop_mode: boolean;
}

/** A row of drill_attempts as returned by GET /api/attempts. */
export interface DrillAttempt {
  id: number;
  lesson_id: string;
  started_at: string;
  finished_at: string | null;
  time_limit_min: number;
  extended: boolean;
  level_ms: number[];
  cleared: number;
  cleared_in_time: number;
  loop_mode: boolean;
}

/** GET /api/attempts response (or { disabled: true }). */
export interface AttemptsResponse {
  grades: Attempt[];
  drills: DrillAttempt[];
}

/** POST /api/attempts body for a drill. */
export interface DrillAttemptInput {
  kind: "drill";
  lesson: string;
  startedAt: string;
  finishedAt?: string | null;
  timeLimitMin: number;
  extended?: boolean;
  levelMs?: number[];
  cleared: number;
  clearedInTime: number;
  loopMode?: boolean;
}
