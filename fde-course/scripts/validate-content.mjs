// Checks every lesson the way a learner's browser would run it:
//  - exercise solution.py passes all tests
//  - exercise starter.py does NOT pass (otherwise the exercise is free)
//  - starter.py and solution.py both run without raising
//  - reading-lesson scratchpads run without errors
//  - quiz questions are well-formed
//  - drills: every test is named test_l<level>_..., each level has tests, and the
//    solution clears every level while the starter clears none
//  - written and role-play lessons have a rubric (and a persona and opening for role-play)
//  - new frontmatter: mode, diagram, timeLimit (role-play), constraints, contextFrom, anchors
//  - quiz bias: with 8+ questions, no answer position holds more than 40% of answers and every
//    position is used; the correct option isn't the strictly longest in more than 60% of
//    questions (5+ questions); explanations don't say "option A/B/C/D" (the letter goes stale
//    as soon as options are reordered to fix bias)
// Usage: npm run validate-content
import { readFileSync, readdirSync, existsSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import matter from "gray-matter";
import { loadPyodide } from "pyodide";

const root = process.cwd();
const modulesDir = join(root, "content", "modules");
const pyRoot = join(root, "public", "py");

const pyodide = await loadPyodide({ indexURL: join(root, "node_modules", "pyodide") + "/" });
(function install(dir) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) install(p);
    else if (name.endsWith(".py")) {
      const dest = "/home/pyodide/lib/" + relative(pyRoot, p).split("\\").join("/");
      pyodide.FS.mkdirTree(dest.slice(0, dest.lastIndexOf("/")));
      pyodide.FS.writeFile(dest, readFileSync(p, "utf8"));
    }
  }
})(pyRoot);
pyodide.runPython('import sys; sys.path.insert(0, "/home/pyodide/lib"); import fde_harness');
const run = pyodide.globals.get("fde_harness").run;
const simulated = new Set(readdirSync(pyRoot).filter((n) => !n.endsWith(".json")).map((n) => n.replace(/\.py$/, "")));
const findImports = pyodide.pyimport("pyodide.code").find_imports;
async function loadNeeded(code) {
  let names = [];
  try {
    names = findImports(code).toJs();
  } catch {
    return;
  }
  const needed = names.filter((n) => !simulated.has(n));
  if (needed.length) await pyodide.loadPackagesFromImports(needed.map((n) => `import ${n}`).join("\n"));
}

const read = (p) => (existsSync(p) ? readFileSync(p, "utf8") : "");
const allLessons = new Set(
  readdirSync(modulesDir).flatMap((m) =>
    statSync(join(modulesDir, m)).isDirectory() ? readdirSync(join(modulesDir, m)).filter((f) => f.endsWith(".md")).map((f) => `${m}/${f.replace(/\.md$/, "")}`) : [],
  ),
);

/** Checks the design-mode, context and calibration fields. */
function checkNewFields(where, data) {
  const graded = data.type === "written" || data.type === "roleplay";
  const onlyFor = (field, ok, kinds) => {
    if (data[field] !== undefined && !ok) fail(where, `${field} is only allowed on ${kinds} lessons`);
  };
  onlyFor("mode", data.type === "roleplay", "roleplay");
  onlyFor("constraints", data.type === "roleplay", "roleplay");
  onlyFor("diagram", graded, "written and roleplay");
  onlyFor("contextFrom", graded, "written and roleplay");
  onlyFor("anchors", graded, "written and roleplay");
  if (data.mode !== undefined && data.mode !== "design") fail(where, `mode must be "design" (got ${JSON.stringify(data.mode)})`);
  if (data.diagram !== undefined && typeof data.diagram !== "boolean") fail(where, "diagram must be true or false");
  if (data.type === "roleplay" && data.timeLimit !== undefined && !(Number(data.timeLimit) > 0)) fail(where, "timeLimit must be a positive number of minutes");
  const maxTurns = Number(data.maxTurns ?? 8);
  if (data.constraints !== undefined) {
    if (!Array.isArray(data.constraints)) fail(where, "constraints must be a list of {afterTurn, text}");
    else
      data.constraints.forEach((c, i) => {
        if (!Number.isInteger(c?.afterTurn) || c.afterTurn < 1) fail(where, `constraint ${i + 1}: afterTurn must be a whole number from 1`);
        else if (c.afterTurn >= maxTurns) fail(where, `constraint ${i + 1}: afterTurn ${c.afterTurn} must be below maxTurns (${maxTurns})`);
        if (typeof c?.text !== "string" || !c.text.trim()) fail(where, `constraint ${i + 1}: text is required`);
        if (data.constraints.findIndex((d) => d?.afterTurn === c?.afterTurn) !== i) fail(where, `constraint ${i + 1}: two constraints after turn ${c?.afterTurn}`);
      });
  }
  if (data.contextFrom !== undefined) {
    if (!Array.isArray(data.contextFrom)) fail(where, "contextFrom must be a list of \"module/lesson\" ids");
    else
      data.contextFrom.forEach((id) => {
        if (typeof id !== "string" || !allLessons.has(id)) fail(where, `contextFrom points to a lesson that doesn't exist: ${JSON.stringify(id)}`);
        else if (id === where) fail(where, "contextFrom can't point to the lesson itself");
      });
  }
  if (data.anchors !== undefined) {
    if (!Array.isArray(data.anchors) || !data.anchors.length) fail(where, "anchors must be a non-empty list of {label, expect: [min, max], answer}");
    else {
      const keys = (Array.isArray(data.sections) && data.sections.length ? data.sections : [{ key: "answer" }]).map((s) => s.key);
      data.anchors.forEach((a, i) => {
        const at = `anchor ${i + 1}${a?.label ? ` (${a.label})` : ""}`;
        if (typeof a?.label !== "string" || !a.label.trim()) fail(where, `${at}: label is required`);
        const e = a?.expect;
        if (!Array.isArray(e) || e.length !== 2 || !e.every((n) => Number.isInteger(n) && n >= 0 && n <= 100) || e[0] > e[1]) {
          fail(where, `${at}: expect must be [min, max], whole percents from 0 to 100 with min <= max`);
        }
        const ans = a?.answer;
        if (typeof ans === "string") {
          // A string answer on a multi-section written lesson is graded as one combined section.
          if (!ans.trim()) fail(where, `${at}: answer is empty`);
        } else if (Array.isArray(ans)) {
          if (data.type !== "roleplay") fail(where, `${at}: a transcript answer is only for role-plays`);
          else if (!ans.length || !ans.every((l) => (l?.from === "persona" || l?.from === "learner") && typeof l.text === "string")) {
            fail(where, `${at}: transcript lines need from ("persona" or "learner") and text`);
          } else if (!ans.some((l) => l.from === "learner")) fail(where, `${at}: transcript has no learner turns`);
        } else if (ans && typeof ans === "object") {
          if (data.type !== "written") fail(where, `${at}: an answer keyed by section is only for written lessons`);
          else {
            for (const k of Object.keys(ans)) if (!keys.includes(k)) fail(where, `${at}: unknown section key ${k}`);
            if (!Object.values(ans).some((v) => typeof v === "string" && v.trim())) fail(where, `${at}: answer is empty`);
          }
        } else fail(where, `${at}: answer is required`);
      });
    }
  }
}

/** Answer-position and answer-length bias in a quiz. */
function checkQuizBias(where, qs) {
  const n = qs.length;
  const positions = Math.min(...qs.map((q) => q.options.length));
  if (n >= 8) {
    const counts = new Array(positions).fill(0);
    for (const q of qs) if (q.answer < positions) counts[q.answer]++;
    const letters = counts.map((c, i) => `${"ABCDEFGH"[i]}=${c}`).join(" ");
    counts.forEach((c, i) => {
      if (c > 0.4 * n) fail(where, `answer bias: ${c} of ${n} answers are option ${"ABCDEFGH"[i]} (max 40%) [${letters}]`);
    });
    const unused = counts.map((c, i) => (c === 0 ? "ABCDEFGH"[i] : null)).filter(Boolean);
    if (unused.length) fail(where, `answer bias: option position(s) ${unused.join(", ")} never correct [${letters}]`);
  }
  if (n >= 5) {
    const longest = qs.filter((q) => {
      const len = q.options.map((o) => String(o).length);
      const mine = len[q.answer];
      return len.every((l, i) => i === q.answer || l < mine);
    }).length;
    if (longest > 0.6 * n) fail(where, `length bias: the correct option is the strictly longest in ${longest} of ${n} questions (max 60%)`);
  }
  qs.forEach((q, i) => {
    if (typeof q.explain === "string" && /\boption\s+[A-D]\b/i.test(q.explain)) fail(where, `question ${i + 1}: explanation names "option ${/\boption\s+([A-D])\b/i.exec(q.explain)[1]}"; refer to the idea, not the letter`);
  });
}
let failures = 0;
let checked = 0;
const fail = (where, msg) => {
  failures++;
  console.error(`✗ ${where}: ${msg}`);
};

for (const mod of readdirSync(modulesDir).sort()) {
  const modDir = join(modulesDir, mod);
  for (const file of readdirSync(modDir).filter((f) => f.endsWith(".md")).sort()) {
    const slug = file.replace(/\.md$/, "");
    const where = `${mod}/${slug}`;
    const { data } = matter(read(join(modDir, file)));
    const exDir = join(modDir, slug);
    const starter = read(join(exDir, "starter.py"));
    const setup = read(join(exDir, "setup.py"));
    const tests = read(join(exDir, "tests.py"));
    const solution = read(join(exDir, "solution.py"));
    checked++;

    if (!data.title) fail(where, "missing title");
    if (!["reading", "exercise", "quiz", "drill", "written", "roleplay"].includes(data.type)) fail(where, `bad type ${data.type}`);
    if (!(Number(data.minutes) > 0)) fail(where, "missing minutes");
    checkNewFields(where, data);

    if (data.type === "drill") {
      const levels = Array.isArray(data.levels) ? data.levels.length : 0;
      if (!levels) fail(where, "drill needs a levels list in its frontmatter");
      const body = read(join(modDir, file));
      const headings = (body.match(/^## Level \d+/gm) ?? []).length;
      if (headings !== levels) fail(where, `drill lists ${levels} levels but has ${headings} "## Level N" headings`);
      for (const name of tests.match(/^def (test_\w+)/gm) ?? []) {
        const n = Number(/test_l(\d+)_/.exec(name)?.[1] ?? 0);
        if (!(n >= 1 && n <= levels)) fail(where, `${name.slice(4)} must be named test_l<1..${levels}>_...`);
      }
      for (let n = 1; n <= levels; n++) if (!new RegExp(`^def test_l${n}_`, "m").test(tests)) fail(where, `level ${n} has no tests`);
      const st = JSON.parse(run(starter, setup, tests, "submit"));
      const lvl1 = st.tests.filter((t) => /^test_l1_/.test(t.id ?? ""));
      if (lvl1.length && lvl1.every((t) => t.passed)) fail(where, "starter code already clears level 1");
    }

    if (data.type === "written" || data.type === "roleplay") {
      const rubric = data.rubric;
      if (!Array.isArray(rubric) || !rubric.length) fail(where, "needs a rubric");
      else {
        rubric.forEach((r, i) => {
          if (!r.name || !(r.points > 0) || !r.lookFor) fail(where, `rubric item ${i + 1} needs name, points and lookFor`);
        });
        // The grader returns criteria by exact name (a JSON-schema enum), so names must be unique.
        const names = rubric.map((r) => r.name);
        if (new Set(names).size !== names.length) fail(where, "rubric criterion names must be unique");
      }
      if (data.type === "written" && data.sections) {
        const keys = new Set();
        data.sections.forEach((s, i) => {
          if (!s.key || !s.label) fail(where, `section ${i + 1} needs key and label`);
          if (keys.has(s.key)) fail(where, `duplicate section key ${s.key}`);
          keys.add(s.key);
        });
      }
      if (data.type === "roleplay") {
        const p = data.persona;
        if (!p?.name || !p?.role || !p?.company) fail(where, "role-play needs persona.name, persona.role and persona.company");
        if (!data.opening) fail(where, "role-play needs an opening line");
        if (!data.personaBrief) fail(where, "role-play needs a personaBrief");
      }
      console.log(`✓ ${where} (${data.type}, ${data.rubric?.length ?? 0} rubric lines)`);
      continue;
    }

    if (data.type === "exercise" || data.type === "drill") {
      if (!starter || !tests || !solution) {
        fail(where, "exercise needs starter.py, solution.py and tests.py");
        continue;
      }
      await loadNeeded([setup, solution, tests].join("\n"));
      const sol = JSON.parse(run(solution, setup, tests, "submit"));
      if (!sol.passed) {
        fail(where, "solution does not pass:\n" + (sol.error ?? "") + sol.tests.filter((t) => !t.passed).map((t) => `    - ${t.name}: ${t.message}`).join("\n"));
      }
      const st = JSON.parse(run(starter, setup, tests, "submit"));
      if (st.passed) fail(where, "starter code already passes the tests");
      // Pressing Run on untouched starter code must not crash: learners' first click should feel safe.
      const stRun = JSON.parse(run(starter, setup, "", "run"));
      if (!stRun.ok) fail(where, "starter code raises when run:\n" + stRun.error);
      const solRun = JSON.parse(run(solution, setup, "", "run"));
      if (!solRun.ok) fail(where, "solution raises when run:\n" + solRun.error);
      if (!sol.tests.length) fail(where, "no tests found");
      else console.log(`✓ ${where} (${sol.tests.length} tests)`);
    } else if (data.type === "quiz") {
      const qs = data.questions;
      if (!Array.isArray(qs) || qs.length === 0) fail(where, "quiz has no questions");
      else {
        let wellFormed = true;
        qs.forEach((q, i) => {
          if (!q.q || !Array.isArray(q.options) || !(q.answer >= 0 && q.answer < q.options.length)) {
            fail(where, `question ${i + 1} malformed`);
            wellFormed = false;
          }
        });
        if (wellFormed) checkQuizBias(where, qs);
        console.log(`✓ ${where} (${qs.length} questions)`);
      }
    } else {
      if (starter) {
        const r = JSON.parse(run(starter, setup, "", "run"));
        if (!r.ok) fail(where, "scratchpad raises: " + r.error);
      }
      console.log(`✓ ${where}`);
    }
  }
}

console.log(`\n${checked} lessons checked, ${failures} problem(s).`);
process.exit(failures ? 1 : 0);
