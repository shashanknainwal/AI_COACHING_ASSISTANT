import Anthropic from "@anthropic-ai/sdk";
import { NextResponse } from "next/server";

// TODO(auth): once Supabase auth + Stripe are added, reject requests from
// users who haven't purchased, and rate-limit per user.

const SYSTEM = `You are the AI tutor inside an online course on Forward Deployed Engineering.
Learners write Python in a browser editor. Their code is graded by hidden tests.
In the exercises, the \`anthropic\` package is a faithful offline simulator of the real Anthropic Python SDK.

Your job is to get the learner unstuck while they still do the thinking:
- Point at the specific line or concept that is wrong and explain why.
- Ask a guiding question or give the next small step.
- Never paste a complete working solution or rewrite their whole function. A short snippet of 1-3 lines that illustrates a concept is fine.
- If their code already looks correct, say so and suggest what to check (e.g. exact return type, edge cases the tests mention).
- Keep it under 150 words. Use plain text with short paragraphs or a short list.`;

interface TutorRequest {
  lessonTitle?: string;
  instructions?: string;
  code?: string;
  output?: string;
  question?: string;
}

export async function POST(req: Request) {
  if (!process.env.ANTHROPIC_API_KEY) {
    return NextResponse.json({
      answer: "The AI tutor isn't switched on for this site yet (ANTHROPIC_API_KEY is not set). Use the hints above in the meantime.",
    });
  }

  let body: TutorRequest;
  try {
    body = (await req.json()) as TutorRequest;
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  const clip = (s: unknown, n: number) => String(s ?? "").slice(0, n);
  const userContent = [
    `<exercise title="${clip(body.lessonTitle, 200)}">\n${clip(body.instructions, 12000)}\n</exercise>`,
    `<learner_code>\n${clip(body.code, 12000)}\n</learner_code>`,
    `<latest_output>\n${clip(body.output, 6000) || "(not run yet)"}\n</latest_output>`,
    body.question ? `<learner_question>\n${clip(body.question, 2000)}\n</learner_question>` : "The learner didn't type a question. Give the most useful next hint.",
  ].join("\n\n");

  const client = new Anthropic();
  try {
    const response = await client.beta.messages.create({
      model: "claude-opus-5-5",
      max_tokens: 16000,
      thinking: { type: "adaptive" },
      output_config: { effort: "low" },
      betas: ["server-side-fallback-2026-07-01"],
      fallbacks: "default",
      system: [{ type: "text", text: SYSTEM, cache_control: { type: "ephemeral" } }],
      messages: [{ role: "user", content: userContent }],
    });

    if (response.stop_reason === "refusal") {
      return NextResponse.json({ answer: "The tutor couldn't help with that request. Try rephrasing your question." });
    }
    const answer = response.content
      .filter((b): b is Anthropic.Beta.BetaTextBlock => b.type === "text")
      .map((b) => b.text)
      .join("\n")
      .trim();
    return NextResponse.json({ answer: answer || "The tutor had nothing to add. Try asking a specific question." });
  } catch (error) {
    if (error instanceof Anthropic.RateLimitError) {
      return NextResponse.json({ error: "The tutor is busy right now. Try again in a minute." }, { status: 429 });
    }
    if (error instanceof Anthropic.AuthenticationError) {
      console.error("Tutor: invalid ANTHROPIC_API_KEY");
      return NextResponse.json({ error: "The tutor is misconfigured. Please contact support." }, { status: 500 });
    }
    if (error instanceof Anthropic.APIError) {
      console.error(`Tutor: API error ${error.status}`, error.message);
      return NextResponse.json({ error: "The tutor hit an error. Try again." }, { status: 502 });
    }
    console.error("Tutor: unexpected error", error);
    return NextResponse.json({ error: "The tutor hit an error. Try again." }, { status: 500 });
  }
}
