// Shapes shared by /api/coach and the browser components that call it.

export interface TranscriptLine {
  from: "persona" | "learner";
  text: string;
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
}
