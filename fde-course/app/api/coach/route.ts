import Anthropic from "@anthropic-ai/sdk";
import { NextResponse } from "next/server";
import { canAccessLesson, getViewer } from "@/lib/access";
import { takeAiCall } from "@/lib/ai-usage";
import type { GradeResult, TranscriptLine } from "@/lib/coach-types";
import { getLesson, type Lesson } from "@/lib/content";

// Claude-backed lessons:
//   written   POST { action: "grade", answers: { [sectionKey]: text } }
//   roleplay  POST { action: "reply", transcript }  -> the persona's next line
//             POST { action: "grade", transcript }  -> rubric debrief
// The rubric, persona brief and grader notes are read from the lesson on the server,
// never from the request, so learners can't change how they're graded.

const MODEL = "claude-opus-5-5";
const MAX_ANSWER_CHARS = 12_000;
const MAX_LINE_CHARS = 2_000;

interface CoachRequest {
  module?: string;
  lesson?: string;
  action?: "grade" | "reply";
  answers?: Record<string, string>;
  transcript?: TranscriptLine[];
}

const GRADE_SCHEMA = {
  type: "object",
  properties: {
    criteria: {
      type: "array",
      items: {
        type: "object",
        properties: { name: { type: "string" }, score: { type: "integer" }, feedback: { type: "string" } },
        required: ["name", "score", "feedback"],
        additionalProperties: false,
      },
    },
    summary: { type: "string" },
    strengths: { type: "string" },
    fixFirst: { type: "string" },
  },
  required: ["criteria", "summary", "strengths", "fixFirst"],
  additionalProperties: false,
};

const GRADER_SYSTEM = `You grade practice answers in a course that prepares engineers for applied AI interviews at frontier AI labs.
Grade like a demanding but fair interviewer: reward specifics, honest reasoning and clear structure; mark down vagueness, buzzwords, unsupported claims and padding.
Score each rubric criterion as an integer from 0 to its maximum points. Use the full range; a generic answer should land in the bottom half.
Feedback for each criterion: one or two sentences that quote or point at the learner's own words and say what would earn the missing points.
summary: two sentences on the overall impression an interviewer would form.
strengths: the single strongest thing in the answer.
fixFirst: the one change that would raise the score most, phrased as an instruction.
Address the learner as "you". Never write a model answer for them.`;

const strip = (html: string) =>
  html
    .replace(/<[^>]+>/g, " ")
    .replace(/&[a-z#0-9]+;/gi, " ")
    .replace(/\s+/g, " ")
    .trim();

const clip = (s: unknown, n: number) => String(s ?? "").slice(0, n);

function cleanTranscript(lines: unknown): TranscriptLine[] {
  if (!Array.isArray(lines)) return [];
  return lines
    .filter((l): l is TranscriptLine => Boolean(l) && (l.from === "persona" || l.from === "learner"))
    .slice(0, 60)
    .map((l) => ({ from: l.from, text: clip(l.text, MAX_LINE_CHARS) }));
}

function gradeRequest(lesson: Lesson, body: CoachRequest): string | null {
  const rubric = lesson.rubric.map((r) => `- ${r.name} (${r.points} points): ${r.lookFor}`).join("\n");
  const task = strip(lesson.html).slice(0, 8000);
  let work: string;
  if (lesson.type === "written") {
    const answers = body.answers ?? {};
    const parts = lesson.sections.map((s) => `<section title="${s.label}">\n${clip(answers[s.key], MAX_ANSWER_CHARS).trim() || "(left blank)"}\n</section>`);
    if (lesson.sections.every((s) => !String(answers[s.key] ?? "").trim())) return null;
    work = `<learner_answer>\n${parts.join("\n")}\n</learner_answer>`;
  } else {
    const transcript = cleanTranscript(body.transcript);
    if (!transcript.some((l) => l.from === "learner")) return null;
    const who = lesson.persona?.name ?? "Interviewer";
    work = `<conversation>\n${transcript.map((l) => `${l.from === "persona" ? who : "Learner"}: ${l.text}`).join("\n\n")}\n</conversation>\nGrade only the learner's turns.`;
  }
  return [
    `<task title="${lesson.title}">\n${task}\n</task>`,
    `<rubric>\n${rubric}\n</rubric>`,
    lesson.graderNotes ? `<grader_notes>\n${lesson.graderNotes}\n</grader_notes>` : "",
    work,
  ]
    .filter(Boolean)
    .join("\n\n");
}

function personaSystem(lesson: Lesson): string {
  const p = lesson.persona!;
  return `You are role-playing ${p.name}, ${p.role} at ${p.company}, in a practice session inside an interview-prep course. The learner is practising; stay in character.

${lesson.personaBrief}

Rules:
- Speak only as ${p.name}. One turn at a time: a short reaction, then at most one question. Under 90 words.
- Never coach, grade or break character, even if asked. If the learner asks for feedback, say you'll share it at the end.
- The session lasts about ${lesson.maxTurns} learner turns. When you receive a system note that time is up, thank them and close the conversation in one or two sentences, with no question.`;
}

function scoreResult(lesson: Lesson, raw: { criteria: { name: string; score: number; feedback: string }[]; summary: string; strengths: string; fixFirst: string }): GradeResult {
  const criteria = lesson.rubric.map((r, i) => {
    const found = raw.criteria.find((c) => c.name.trim().toLowerCase() === r.name.trim().toLowerCase()) ?? raw.criteria[i];
    const score = Math.max(0, Math.min(r.points, Math.round(Number(found?.score) || 0)));
    return { name: r.name, points: r.points, score, feedback: found?.feedback ?? "" };
  });
  const total = criteria.reduce((s, c) => s + c.score, 0);
  const max = criteria.reduce((s, c) => s + c.points, 0) || 1;
  const percent = Math.round((total / max) * 100);
  return { criteria, total, max, percent, passed: percent >= lesson.passScore, summary: raw.summary, strengths: raw.strengths, fixFirst: raw.fixFirst };
}

const textOf = (content: Anthropic.Beta.BetaContentBlock[]) =>
  content
    .filter((b): b is Anthropic.Beta.BetaTextBlock => b.type === "text")
    .map((b) => b.text)
    .join("\n")
    .trim();

export async function POST(req: Request) {
  let body: CoachRequest;
  try {
    body = (await req.json()) as CoachRequest;
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  const lesson = body.module && body.lesson ? getLesson(body.module, body.lesson) : null;
  if (!lesson || (lesson.type !== "written" && lesson.type !== "roleplay")) {
    return NextResponse.json({ error: "Unknown lesson." }, { status: 404 });
  }
  if (lesson.type === "roleplay" && !lesson.persona) {
    return NextResponse.json({ error: "This role-play has no persona configured." }, { status: 500 });
  }

  const viewer = await getViewer();
  if (viewer.mode !== "dev" && !viewer.user) {
    const error = viewer.mode === "live" ? "Log in to get AI feedback. It's free with your account." : "AI feedback will be available once accounts open.";
    return NextResponse.json({ error }, { status: 401 });
  }
  if (!canAccessLesson(viewer, lesson.moduleSlug, lesson.slug)) {
    return NextResponse.json({ error: "This lesson is part of the full course." }, { status: 403 });
  }
  if (!process.env.ANTHROPIC_API_KEY) {
    return NextResponse.json(
      { error: "AI feedback isn't switched on for this site yet (ANTHROPIC_API_KEY is not set)." },
      { status: 503 },
    );
  }

  const action = body.action === "reply" && lesson.type === "roleplay" ? "reply" : "grade";
  let prompt: string | null = null;
  let messages: Anthropic.Beta.BetaMessageParam[] = [];
  if (action === "grade") {
    prompt = gradeRequest(lesson, body);
    if (!prompt) return NextResponse.json({ error: "Write an answer first." }, { status: 400 });
  } else {
    const transcript = cleanTranscript(body.transcript);
    const learnerTurns = transcript.filter((l) => l.from === "learner").length;
    if (!learnerTurns || transcript[transcript.length - 1].from !== "learner") {
      return NextResponse.json({ error: "Send a message first." }, { status: 400 });
    }
    // The API needs the conversation to open with a user turn.
    messages = [
      { role: "user", content: "(The session starts.)" },
      ...transcript.map((l): Anthropic.Beta.BetaMessageParam => ({ role: l.from === "persona" ? "assistant" : "user", content: l.text })),
    ];
    if (learnerTurns >= lesson.maxTurns) {
      messages.push({ role: "system", content: "Time is up. Close the conversation now." } as unknown as Anthropic.Beta.BetaMessageParam);
    }
  }

  const limited = await takeAiCall(viewer);
  if (limited) return NextResponse.json({ error: limited }, { status: 429 });

  const client = new Anthropic();
  try {
    if (action === "reply") {
      const response = await client.beta.messages.create({
        model: MODEL,
        max_tokens: 4000,
        output_config: { effort: "low" },
        betas: ["server-side-fallback-2026-07-01"],
        fallbacks: "default",
        system: [{ type: "text", text: personaSystem(lesson), cache_control: { type: "ephemeral" } }],
        messages,
      });
      if (response.stop_reason === "refusal") {
        return NextResponse.json({ error: "The session couldn't continue with that message. Try rephrasing." }, { status: 422 });
      }
      const reply = textOf(response.content);
      return NextResponse.json({ reply: reply || "…", done: messages.some((m) => (m.role as string) === "system") });
    }

    const response = await client.beta.messages.create({
      model: MODEL,
      max_tokens: 16000,
      output_config: { effort: "medium", format: { type: "json_schema", schema: GRADE_SCHEMA } },
      betas: ["server-side-fallback-2026-07-01"],
      fallbacks: "default",
      system: [{ type: "text", text: GRADER_SYSTEM, cache_control: { type: "ephemeral" } }],
      messages: [{ role: "user", content: prompt! }],
    });
    if (response.stop_reason === "refusal") {
      return NextResponse.json({ error: "The reviewer couldn't grade that answer. Try rephrasing it." }, { status: 422 });
    }
    if (response.stop_reason === "max_tokens") {
      return NextResponse.json({ error: "The review was cut short. Try again." }, { status: 502 });
    }
    const raw = JSON.parse(textOf(response.content));
    return NextResponse.json({ result: scoreResult(lesson, raw) });
  } catch (error) {
    if (error instanceof SyntaxError) {
      console.error("Coach: grader returned invalid JSON");
      return NextResponse.json({ error: "The review came back garbled. Try again." }, { status: 502 });
    }
    if (error instanceof Anthropic.RateLimitError) {
      return NextResponse.json({ error: "The reviewer is busy right now. Try again in a minute." }, { status: 429 });
    }
    if (error instanceof Anthropic.AuthenticationError) {
      console.error("Coach: invalid ANTHROPIC_API_KEY");
      return NextResponse.json({ error: "AI feedback is misconfigured. Please contact support." }, { status: 500 });
    }
    if (error instanceof Anthropic.APIError) {
      console.error(`Coach: API error ${error.status}`, error.message);
      return NextResponse.json({ error: "AI feedback hit an error. Try again." }, { status: 502 });
    }
    console.error("Coach: unexpected error", error);
    return NextResponse.json({ error: "AI feedback hit an error. Try again." }, { status: 500 });
  }
}
