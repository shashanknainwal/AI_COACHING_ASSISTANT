/* Runs learner Python in a module Web Worker so the page never freezes.
 * Messages in:  { id, type: "run", code, setup, tests, mode: "run" | "submit" }
 * Messages out: { id, type: "ready" | "status" | "result" | "error", ... }
 */
import { loadPyodide } from "/pyodide/pyodide.mjs";

const PYODIDE_VERSION = "314.0.7";
const CDN = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;


let pyodideReady = null;
let simulated = new Set();

async function boot() {
  postMessage({ type: "status", message: "Loading Python…" });
  const pyodide = await loadPyodide({
    indexURL: "/pyodide/",
    packageBaseUrl: CDN,
  });
  const manifest = await (await fetch("/py/manifest.json")).json();
  for (const rel of manifest.files) {
    const src = await (await fetch(`/py/${rel}`)).text();
    const path = `/home/pyodide/lib/${rel}`;
    const dir = path.slice(0, path.lastIndexOf("/"));
    pyodide.FS.mkdirTree(dir);
    pyodide.FS.writeFile(path, src);
  }
  // Top-level names the course simulates (anthropic, requests, ...). Never download
  // the real packages for these: the simulators must win.
  simulated = new Set(manifest.files.map((f) => f.split("/")[0].replace(/\.py$/, "")));
  pyodide.runPython(`
import sys
sys.path.insert(0, "/home/pyodide/lib")
import fde_harness
`);
  postMessage({ type: "ready" });
  return pyodide;
}

self.onmessage = async (event) => {
  const msg = event.data;
  if (!pyodideReady) pyodideReady = boot();
  let pyodide;
  try {
    pyodide = await pyodideReady;
  } catch (err) {
    pyodideReady = null;
    postMessage({ id: msg.id, type: "error", message: `Python failed to load: ${err}` });
    return;
  }
  if (msg.type === "warmup") return;
  if (msg.type !== "run") return;

  try {
    // Fetch pandas/numpy etc. on demand when the code imports them.
    const all = [msg.setup || "", msg.code || "", msg.tests || ""].join("\n");
    let imports = [];
    try {
      imports = pyodide.pyimport("pyodide.code").find_imports(all).toJs();
    } catch {
      // Syntax errors: let the harness report them.
    }
    const needed = imports.filter((name) => !simulated.has(name));
    if (needed.length) {
      await pyodide.loadPackagesFromImports(needed.map((n) => `import ${n}`).join("\n"), {
        messageCallback: (m) => postMessage({ type: "status", message: m }),
      });
    }
    const run = pyodide.globals.get("fde_harness").run;
    const json = run(msg.code || "", msg.setup || "", msg.tests || "", msg.mode || "run");
    run.destroy?.();
    postMessage({ id: msg.id, type: "result", result: JSON.parse(json) });
  } catch (err) {
    postMessage({ id: msg.id, type: "error", message: String(err) });
  }
};
