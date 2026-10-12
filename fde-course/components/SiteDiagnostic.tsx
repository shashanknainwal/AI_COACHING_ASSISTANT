// The onboarding diagnostic: ten original fundamentals questions, skill areas for a self-rating,
// and the week-by-week plan built from the interview date, hours per week and the answers.
// Pure functions; used by app/start (SiteOnboarding).

import { MOCK_LOOP_MODULES } from "@/lib/config";
import type { Diagnostic, PlanModule, PlanWeek, RoleTrack } from "./SiteTypes";

export interface DiagQuestion {
  q: string;
  options: string[];
  answer: number;
  area: string;
  explain: string;
}

// Correct answers are spread across positions (A B C D A B C D A B) and are not the longest option by habit.
export const QUESTIONS: DiagQuestion[] = [
  {
    q: "On claude-sonnet-5-5 ($2 input, $10 output per million tokens), what does one request with 10,000 input tokens and 500 output tokens cost, ignoring thinking?",
    options: ["$0.025", "$0.25", "$0.0025", "$0.07"],
    answer: 0,
    area: "fundamentals",
    explain: "10,000 × $2/1M = $0.02, plus 500 × $10/1M = $0.005. Thinking tokens bill as output, so real requests often cost more.",
  },
  {
    q: "Your system prompt is the same on every call, but prompt caching never registers a hit. What is the most likely cause?",
    options: ["The prompt is longer than 512 tokens", "A timestamp is inserted at the very start of the prompt", "Requests arrive about one minute apart", "The cache_control marker sits at the end of the shared part"],
    answer: 1,
    area: "fundamentals",
    explain: "The cache matches an exact prefix. Anything that changes at the top, like a timestamp, breaks every later match.",
  },
  {
    q: "Prompt B beats prompt A on 22 of 40 golden cases; A wins the other 18. What should you conclude?",
    options: ["B is better, so ship it to everyone today", "A is safer, so keep it and drop B", "Too close to call yet; add cases and read the flips", "Ask Claude which prompt it prefers"],
    answer: 2,
    area: "evals",
    explain: "A 22–18 split on 40 cases is well inside the noise. More cases narrow the interval, and the flipped cases tell you what changed.",
  },
  {
    q: "Claude returns stop_reason \"tool_use\" for a custom tool you defined. Who runs the tool?",
    options: ["Anthropic runs it on its own servers for you", "Claude runs it inside a secure code sandbox", "Nobody: the model simulates the result itself", "Your code runs it and sends back a tool_result"],
    answer: 3,
    area: "agents",
    explain: "For tools you define, Claude only asks. Your code validates the input, runs the tool and returns a tool_result with the matching id.",
  },
  {
    q: "A RAG answer cites the right policy document but quotes last year's version. What's the best first fix?",
    options: ["Filter retrieval by document version or effective date", "Raise the temperature so it explores more", "Switch to a larger embedding dimension", "Tell the model to double-check its quotes"],
    answer: 0,
    area: "agents",
    explain: "The retriever handed over the stale version. Metadata filters (version, date, status) fix it at the source; prompting can't.",
  },
  {
    q: "A partner API starts returning HTTP 429. What should your client do?",
    options: ["Retry at once in a tight loop until it works", "Back off with jitter and honour Retry-After", "Drop the request as a permanent failure", "Rotate to a second API key to dodge the limit"],
    answer: 1,
    area: "production",
    explain: "429 means slow down. Exponential backoff with jitter, respecting Retry-After when it's sent, is the standard, polite fix.",
  },
  {
    q: "Which request is safe to retry after a timeout, with no idempotency key?",
    options: ["POST /orders to create an order", "PATCH /orders/42 to add one to the quantity", "PUT /orders/42 with the full order", "Any of them, if the timeout was short"],
    answer: 2,
    area: "production",
    explain: "PUT replaces the resource with the same body, so repeating it is harmless. POST and an incrementing PATCH can apply twice.",
  },
  {
    q: "Which current Claude models default to effort \"medium\"?",
    options: ["Only Opus 5.5", "Sonnet 5.5 and Haiku 5.5", "Every current Claude model", "Opus 5.5 and Haiku 5.5"],
    answer: 3,
    area: "fundamentals",
    explain: "Opus 5.5 and Haiku 5.5 default to medium; Sonnet 5.5 defaults to high. Set effort explicitly when you estimate cost and latency.",
  },
  {
    q: "In a first discovery call, a VP says \"we need an AI agent\". What's your best first move?",
    options: ["Ask what outcome they need and how it's measured today", "Demo the most impressive agent you've built", "Quote a price and a timeline for the build", "Explain how large language models work"],
    answer: 0,
    area: "customer",
    explain: "Start from the outcome and today's baseline. Whether it should be an agent at all comes later.",
  },
  {
    q: "In a behavioural answer about a team project, what matters most to the interviewer?",
    options: ["How large and well known the team was", "What you personally decided and did", "Which frameworks and tools the team used", "How senior leaders praised the project"],
    answer: 1,
    area: "stories",
    explain: "Interviewers score your part: the decisions you made, what you did, and what you learned. \"We\" answers hide it.",
  },
];

export const AREAS: { key: string; label: string; modules: string[] }[] = [
  { key: "python", label: "Python under a clock", modules: ["c3-progressive-coding"] },
  { key: "fundamentals", label: "LLM fundamentals: tokens, cost, caching, effort", modules: ["c2-llm-fundamentals", "06-building-with-claude", "e1-production-prompting"] },
  { key: "agents", label: "Tool use, agents and retrieval", modules: ["e2-tools-and-agents", "e3-retrieval-at-scale", "07-tool-use-rag-agents"] },
  { key: "evals", label: "Evals and measurement", modules: ["e4-evals-engineering", "08-evals-and-reliability", "a4-poc-that-closes"] },
  { key: "production", label: "Production: reliability, integrations, observability", modules: ["e5-production-concerns", "09-shipping-to-production", "04-apis-and-integrations"] },
  { key: "design", label: "LLM system design", modules: ["e6-llm-system-design", "a6-reference-architectures", "a3-choosing-the-approach"] },
  { key: "customer", label: "Customer and executive conversations", modules: ["01-fde-role-and-mindset", "02-customer-discovery", "a1-architects-job", "a5-executive-communication"] },
  { key: "stories", label: "Stories, motivation and values", modules: ["c4-reading-the-labs", "c5-values-and-behavioral"] },
  { key: "data", label: "Messy data and SQL", modules: ["03-python-data-wrangling", "05-sql-and-data-modeling"] },
  { key: "enterprise", label: "Enterprise deployment and security", modules: ["a2-enterprise-deployment"] },
];

export const RATING_LABELS = ["New to me", "Read about it", "Done it once", "Do it at work", "Could teach it"];

/** Modules the plan always keeps: how the loop works, the capstone and the mock loops. */
const NEVER_SKIP = new Set(["c1-how-labs-hire", "10-capstone", ...MOCK_LOOP_MODULES]);

const DEFAULT_WEEKS_WITHOUT_DATE = 8;

export type ModuleStatus = "do" | "skim" | "skip";

export function moduleStatuses(answers: number[], ratings: Record<string, number>, modules: PlanModule[]): Record<string, ModuleStatus> {
  const areaOf = new Map<string, string>();
  for (const a of AREAS) for (const m of a.modules) areaOf.set(m, a.key);
  const quiz = new Map<string, { right: number; total: number }>();
  QUESTIONS.forEach((q, i) => {
    const s = quiz.get(q.area) ?? { right: 0, total: 0 };
    s.total++;
    if (answers[i] === q.answer) s.right++;
    quiz.set(q.area, s);
  });
  const out: Record<string, ModuleStatus> = {};
  for (const m of modules) {
    const area = areaOf.get(m.slug);
    if (!area || NEVER_SKIP.has(m.slug)) {
      out[m.slug] = "do";
      continue;
    }
    const r = ratings[area] ?? 3;
    const q = quiz.get(area);
    const f = q ? q.right / q.total : null;
    if (r >= 5 && f === 1) out[m.slug] = "skip";
    else if ((r >= 4 && (f === null || f >= 0.5)) || (r >= 3 && f === 1)) out[m.slug] = "skim";
    else out[m.slug] = "do";
  }
  return out;
}

/** Hours a module takes at a given status: all of it, graded work plus a fast read, or graded work only. */
export function moduleHours(m: PlanModule, s: ModuleStatus): number {
  const reading = Math.max(0, m.minutes - m.gradedMinutes);
  const minutes = s === "do" ? m.minutes : s === "skim" ? m.gradedMinutes + reading * 0.35 : m.gradedMinutes * 0.8;
  return Math.round((minutes / 60) * 10) / 10;
}

export function planModules(all: PlanModule[], role: RoleTrack): PlanModule[] {
  const core = all.filter((m) => m.track === "core");
  const roleMods = all.filter((m) => m.track === role);
  return [...core, ...roleMods];
}

const iso = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;

export function buildPlan(opts: {
  modules: PlanModule[];
  role: RoleTrack;
  interviewDate: string | null;
  hoursPerWeek: number;
  answers: number[];
  ratings: Record<string, number>;
}): Diagnostic {
  const mods = planModules(opts.modules, opts.role);
  const statuses = moduleStatuses(opts.answers, opts.ratings, mods);
  const hpw = Math.max(1, Math.min(80, Math.round(opts.hoursPerWeek || 6)));

  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  let days = DEFAULT_WEEKS_WITHOUT_DATE * 7;
  if (opts.interviewDate && /^\d{4}-\d{2}-\d{2}$/.test(opts.interviewDate)) {
    const [y, m, d] = opts.interviewDate.split("-").map(Number);
    days = Math.round((new Date(y, m - 1, d).getTime() - today.getTime()) / 86_400_000);
  }
  const weeksCount = Math.max(1, Math.ceil(Math.max(1, days) / 7));

  const loopMods = mods.filter((m) => (MOCK_LOOP_MODULES as readonly string[]).includes(m.slug));
  const study = mods.filter((m) => !loopMods.includes(m));
  // The last week is for the mock loop (when there's more than one week).
  const studyWeeks = weeksCount > 1 ? weeksCount - 1 : 1;

  const weeks: PlanWeek[] = Array.from({ length: weeksCount }, (_, i) => {
    const start = new Date(today);
    start.setDate(today.getDate() + i * 7);
    return { week: i + 1, start: iso(start), hours: 0, items: [] };
  });

  let used = 0;
  for (const m of study) {
    const s = statuses[m.slug];
    const h = moduleHours(m, s);
    const w = Math.min(studyWeeks - 1, Math.floor(used / hpw));
    weeks[w].items.push({ slug: m.slug, code: m.code, title: m.title, status: s, hours: h });
    weeks[w].hours += h;
    used += h;
  }
  const last = weeks[weeksCount - 1];
  for (const m of loopMods) {
    const h = moduleHours(m, "do");
    last.items.push({ slug: m.slug, code: m.code, title: m.title, status: "do", hours: h });
    last.hours += h;
  }
  if (loopMods.length) last.note = weeksCount > 1 ? "Mock-loop week: run the full loop in loop mode, then fix your weakest round." : "Run the mock loop as soon as you can.";
  for (const w of weeks) w.hours = Math.round(w.hours * 10) / 10;

  const totalHours = Math.round(weeks.reduce((s, w) => s + w.hours, 0) * 10) / 10;
  const score = QUESTIONS.reduce((s, q, i) => s + (opts.answers[i] === q.answer ? 1 : 0), 0);
  return {
    version: 1,
    createdAt: new Date().toISOString(),
    answers: opts.answers,
    score,
    ratings: opts.ratings,
    statuses,
    plan: weeks,
    totalHours,
    capacityHours: weeksCount * hpw,
  };
}
