// Shapes the site pages (dashboard, onboarding, review, community, portfolio) pass from the
// server to their client components. Types only: safe to import anywhere.

export type RoleTrack = "engineer" | "architect" | "fde";
export const ROLE_TRACKS: RoleTrack[] = ["engineer", "architect", "fde"];
export const ROLE_LABEL: Record<RoleTrack, string> = {
  engineer: "Applied AI Engineer",
  architect: "Applied AI Architect",
  fde: "Forward Deployed Engineer",
};

export interface FixLink {
  label: string;
  href: string;
  note?: string;
}

export interface LoopLessonCfg {
  id: string;
  title: string;
  href: string;
  /** drills */
  levels?: number;
  timeLimit?: number;
}

export interface LoopRoundCfg {
  key: string;
  label: string;
  kind: "drill" | "graded" | "combo";
  optional: boolean;
  lessons: LoopLessonCfg[];
  /** combo rounds: one weight per lesson, summing to 1 */
  weights?: number[];
}

export interface SignalCfg {
  rounds: string[];
  criteria?: string[];
  drill?: "stuck" | "edge" | "slow";
  signal: string;
  cause: string;
  fix: FixLink[];
}

export interface LoopCfg {
  track: RoleTrack;
  title: string;
  loopModule: string;
  firstLessonHref: string;
  scorecard: { title: string; href: string };
  rounds: LoopRoundCfg[];
  signals: SignalCfg[];
}

export interface GradedLessonCfg {
  id: string;
  title: string;
  href: string;
  track: string;
  moduleLabel: string;
}

export interface DrillCfg {
  id: string;
  title: string;
  href: string;
  levels: number;
  timeLimit: number;
}

/** A module as the onboarding plan sees it. */
export interface PlanModule {
  slug: string;
  track: string;
  code: string;
  title: string;
  minutes: number;
  /** minutes of graded work (exercises, drills, written, role-play) */
  gradedMinutes: number;
  href: string;
}

/** The learner profile as /api/profile speaks it (camelCase). */
export interface Profile {
  handle?: string | null;
  publicProfile?: boolean;
  targetRole?: RoleTrack | null;
  interviewDate?: string | null;
  hoursPerWeek?: number | null;
  background?: string | null;
  diagnostic?: Diagnostic | null;
  loopMode?: { track: RoleTrack; startedAt: string } | null;
  nudges?: boolean;
  capstoneUrl?: string | null;
}

export interface PlanWeek {
  week: number;
  start: string;
  hours: number;
  items: { slug: string; code: string; title: string; status: "do" | "skim" | "skip"; hours: number }[];
  note?: string;
}

export interface Diagnostic {
  version: 1;
  createdAt: string;
  answers: number[];
  score: number;
  ratings: Record<string, number>;
  statuses: Record<string, "do" | "skim" | "skip">;
  plan: PlanWeek[];
  totalHours: number;
  capacityHours: number;
}
