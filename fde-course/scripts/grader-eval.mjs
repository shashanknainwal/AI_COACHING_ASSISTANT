// Grader calibration: grades every lesson's `anchors` (weak / borderline / strong answers with
// an expected percent range) through the same code path as /api/coach (lib/grader.ts), and
// fails when a grade drifts outside its range.
//
//   node scripts/grader-eval.mjs                 grade all anchors (needs ANTHROPIC_API_KEY)
//   node scripts/grader-eval.mjs --dry-run       parse anchors and build every prompt, no API calls
//   node scripts/grader-eval.mjs --lesson e4-evals-engineering/05-written-gate   one lesson only
//
// Without ANTHROPIC_API_KEY (and without --dry-run) it prints a message and exits 0, so it is
// safe in CI before the key exists. Cost: one Opus 5.5 grade per anchor (two for borderline
// grades), roughly $0.03–0.06 each.
//
// Anchor frontmatter (validated by scripts/validate-content.mjs):
//   anchors:
//     - label: weak
//       expect: [10, 45]
//       answer: "..."                  # written (a multi-section lesson grades it as one combined section) or a role-play conversation as text
//     - label: strong
//       expect: [75, 100]
//       answer: { tradeoffs: "...", rollout: "..." }        # written, keyed by section
//     - label: borderline
//       expect: [55, 80]
//       answer: [{ from: persona, text: "..." }, { from: learner, text: "..." }]   # role-play
//       diagram: "..."                 # optional, design-mode lessons

import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import matter from "gray-matter";
import { marked } from "marked";
import { GRADER_MODEL, gradeUserTurn, gradeWork, graderSystem } from "../lib/grader.ts";

const args = process.argv.slice(2);
const dryRun = args.includes("--dry-run");
const only = args.includes("--lesson") ? args[args.indexOf("--lesson") + 1] : null;
const modulesDir = join(process.cwd(), "content", "modules");

/** Lessons with anchors, shaped like lib/content.ts's Lesson as far as the grader reads it. */
function loadAnchoredLessons() {
  const lessons = [];
  for (const moduleSlug of readdirSync(modulesDir).sort()) {
    const dir = join(modulesDir, moduleSlug);
    if (!statSync(dir).isDirectory()) continue;
    for (const file of readdirSync(dir).filter((f) => f.endsWith(".md")).sort()) {
      const slug = file.replace(/\.md$/, "");
      const id = `${moduleSlug}/${slug}`;
      if (only && id !== only) continue;
      const { data, content } = matter(readFileSync(join(dir, file), "utf8"));
      if (!Array.isArray(data.anchors) || !data.anchors.length) continue;
      if (data.type !== "written" && data.type !== "roleplay") continue;
      const sections = Array.isArray(data.sections) && data.sections.length ? data.sections : data.type === "written" ? [{ key: "answer", label: "Your answer" }] : [];
      lessons.push({
        id,
        anchors: data.anchors,
        lesson: {
          moduleSlug,
          slug,
          title: String(data.title ?? slug),
          type: data.type,
          html: marked.parse(content, { async: false }),
          rubric: Array.isArray(data.rubric) ? data.rubric : [],
          passScore: Number(data.passScore ?? 70),
          graderNotes: String(data.graderNotes ?? ""),
          sections,
          persona: data.persona ?? null,
          diagram: data.diagram === true,
          mode: data.mode === "design" ? "design" : null,
        },
      });
    }
  }
  return lessons;
}

/** A string answer on a multi-section written lesson is graded as one combined section. */
function lessonFor(lesson, anchor) {
  if (lesson.type !== "written" || typeof anchor.answer !== "string" || lesson.sections.length <= 1) return lesson;
  return { ...lesson, sections: [{ key: "answer", label: `Full answer (${lesson.sections.map((s) => s.label).join("; ")})` }] };
}

function workFor(lesson, anchor) {
  const a = anchor.answer;
  const work = {};
  if (lesson.type === "written") work.answers = typeof a === "string" ? { [lesson.sections[0].key]: a } : { ...(a ?? {}) };
  else if (Array.isArray(a)) work.transcript = a.map((l) => ({ from: l.from, text: String(l.text ?? "") }));
  else work.conversationText = String(a ?? "");
  if (typeof anchor.diagram === "string") work.diagram = anchor.diagram;
  return work;
}

function table(rows) {
  const head = ["lesson", "anchor", "expect", "got", "result"];
  const all = [head, ...rows];
  const widths = head.map((_, i) => Math.max(...all.map((r) => String(r[i]).length)));
  const line = (r) => r.map((c, i) => String(c).padEnd(widths[i])).join("  ");
  console.log(line(head));
  console.log(widths.map((w) => "-".repeat(w)).join("  "));
  rows.forEach((r) => console.log(line(r)));
}

const lessons = loadAnchoredLessons();
const anchorCount = lessons.reduce((s, l) => s + l.anchors.length, 0);
if (only && !lessons.length) {
  console.error(`No anchors found for ${only}.`);
  process.exit(1);
}
if (!anchorCount) {
  console.log("No lessons have grader anchors yet. Add `anchors` to written or role-play lessons to calibrate the grader.");
  process.exit(0);
}

if (dryRun) {
  const rows = [];
  let problems = 0;
  for (const { id, lesson, anchors } of lessons) {
    const system = graderSystem(lesson).map((b) => b.text).join("\n\n");
    for (const anchor of anchors) {
      const l = lessonFor(lesson, anchor);
      const user = gradeUserTurn(l, workFor(l, anchor));
      const ok = Boolean(user) && Array.isArray(anchor.expect) && lesson.rubric.length > 0;
      if (!ok) problems++;
      rows.push([id, anchor.label ?? "?", JSON.stringify(anchor.expect), `~${Math.round((system.length + (user?.length ?? 0)) / 4)} tok`, ok ? "prompt ok" : "EMPTY OR INVALID"]);
    }
  }
  table(rows);
  console.log(`\nDry run: ${anchorCount} anchor(s) in ${lessons.length} lesson(s), ${problems} problem(s). No API calls made.`);
  process.exit(problems ? 1 : 0);
}

if (!process.env.ANTHROPIC_API_KEY) {
  console.log(`ANTHROPIC_API_KEY is not set: skipping the grader eval (${anchorCount} anchor(s) in ${lessons.length} lesson(s)). Run with --dry-run to check the anchors parse.`);
  process.exit(0);
}

const { default: Anthropic } = await import("@anthropic-ai/sdk");
const client = new Anthropic();
const rows = [];
let drift = 0;
for (const { id, lesson, anchors } of lessons) {
  for (const anchor of anchors) {
    const [min, max] = anchor.expect;
    try {
      const l = lessonFor(lesson, anchor);
      const result = await gradeWork(client, l, workFor(l, anchor), GRADER_MODEL);
      const ok = result.percent >= min && result.percent <= max;
      if (!ok) drift++;
      rows.push([id, anchor.label, `${min}-${max}`, `${result.percent}%${result.graderRuns === 2 ? " (2 runs)" : ""}`, ok ? "ok" : "DRIFT"]);
    } catch (error) {
      drift++;
      rows.push([id, anchor.label, `${min}-${max}`, "-", `ERROR ${error?.message ?? error}`]);
    }
  }
}
table(rows);
console.log(`\n${anchorCount} anchor(s) graded, ${drift} outside their expected range.`);
process.exit(drift ? 1 : 0);
