// Checks every lesson the way a learner's browser would run it:
//  - exercise solution.py passes all tests
//  - exercise starter.py does NOT pass (otherwise the exercise is free)
//  - reading-lesson scratchpads run without errors
//  - quiz questions are well-formed
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

const read = (p) => (existsSync(p) ? readFileSync(p, "utf8") : "");
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
    if (!["reading", "exercise", "quiz"].includes(data.type)) fail(where, `bad type ${data.type}`);
    if (!(Number(data.minutes) > 0)) fail(where, "missing minutes");

    if (data.type === "exercise") {
      if (!starter || !tests || !solution) {
        fail(where, "exercise needs starter.py, solution.py and tests.py");
        continue;
      }
      const sol = JSON.parse(await pyodide.loadPackagesFromImports(setup + solution + tests).then(() => run(solution, setup, tests, "submit")));
      if (!sol.passed) {
        fail(where, "solution does not pass:\n" + (sol.error ?? "") + sol.tests.filter((t) => !t.passed).map((t) => `    - ${t.name}: ${t.message}`).join("\n"));
      }
      const st = JSON.parse(run(starter, setup, tests, "submit"));
      if (st.passed) fail(where, "starter code already passes the tests");
      if (!sol.tests.length) fail(where, "no tests found");
      else console.log(`✓ ${where} (${sol.tests.length} tests)`);
    } else if (data.type === "quiz") {
      const qs = data.questions;
      if (!Array.isArray(qs) || qs.length === 0) fail(where, "quiz has no questions");
      else {
        qs.forEach((q, i) => {
          if (!q.q || !Array.isArray(q.options) || !(q.answer >= 0 && q.answer < q.options.length)) fail(where, `question ${i + 1} malformed`);
        });
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
