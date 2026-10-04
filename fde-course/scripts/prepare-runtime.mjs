// 1. Copies the Pyodide runtime from node_modules into public/pyodide so the
//    browser loads it from our own origin (extra packages like pandas still
//    come from the jsDelivr CDN on demand).
// 2. Copies Monaco's prebuilt files into public/monaco.
// 3. Writes public/py/manifest.json listing the Python files the worker
//    installs into Pyodide's filesystem (harness + simulated SDKs).
import { cpSync, mkdirSync, existsSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { join, relative } from "node:path";

const src = join("node_modules", "pyodide");
const dest = join("public", "pyodide");
if (existsSync(src)) {
  mkdirSync(dest, { recursive: true });
  for (const f of ["pyodide.js", "pyodide.mjs", "pyodide.asm.mjs", "pyodide.asm.wasm", "python_stdlib.zip", "pyodide-lock.json"]) {
    cpSync(join(src, f), join(dest, f));
  }
  console.log("Copied Pyodide runtime to public/pyodide");
} else {
  console.warn("pyodide not installed; skipping copy");
}

// Monaco editor, self-hosted so the editor doesn't depend on a third-party CDN.
const monacoSrc = join("node_modules", "monaco-editor", "min", "vs");
if (existsSync(monacoSrc)) {
  cpSync(monacoSrc, join("public", "monaco", "vs"), { recursive: true });
  console.log("Copied Monaco editor to public/monaco");
}

const pyRoot = join("public", "py");
const files = [];
(function walk(dir) {
  for (const name of readdirSync(dir).sort()) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) walk(p);
    else if (name.endsWith(".py")) files.push(relative(pyRoot, p).split("\\").join("/"));
  }
})(pyRoot);
writeFileSync(join(pyRoot, "manifest.json"), JSON.stringify({ files }, null, 2) + "\n");
console.log(`Wrote public/py/manifest.json (${files.length} files)`);
