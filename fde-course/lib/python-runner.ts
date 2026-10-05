"use client";

export interface TestResult {
  name: string;
  passed: boolean;
  message: string;
}

export interface TraceBlock {
  type: "text" | "tool_use" | "thinking";
  text?: string;
  id?: string;
  name?: string;
  input?: string;
}

export interface TraceStep {
  model: string;
  attempt: number;
  error: string | null;
  stop_reason?: string;
  usage?: { input: number; output: number; cache_read: number; cache_write: number };
  blocks?: TraceBlock[];
  results?: { id: string; is_error: boolean; content: string }[];
}

export interface TraceRun {
  question: string;
  steps: TraceStep[];
}

export interface RunResult {
  ok: boolean;
  stdout: string;
  error: string | null;
  tests: TestResult[];
  passed: boolean | null;
  /** Claude calls made by the learner's code, grouped into runs (empty when Claude wasn't called). */
  trace?: TraceRun[];
}

type Listener = (status: string) => void;

const TIMEOUT_MS = 20_000;

let worker: Worker | null = null;
let nextId = 1;
const pending = new Map<number, { resolve: (r: RunResult) => void; reject: (e: Error) => void }>();
const statusListeners = new Set<Listener>();
let ready = false;

function emit(status: string) {
  statusListeners.forEach((l) => l(status));
}

function getWorker(): Worker {
  if (worker) return worker;
  worker = new Worker("/pyodide-worker.mjs", { type: "module" });
  worker.onerror = (e) => {
    emit("Python failed to start. Reload the page to try again.");
    pending.forEach((p) => p.reject(new Error(e.message || "Python worker crashed.")));
    pending.clear();
  };
  worker.onmessage = (e: MessageEvent) => {
    const msg = e.data;
    if (msg.type === "status") emit(msg.message);
    else if (msg.type === "ready") {
      ready = true;
      emit("ready");
    } else if (msg.id && pending.has(msg.id)) {
      const p = pending.get(msg.id)!;
      pending.delete(msg.id);
      if (msg.type === "result") p.resolve(msg.result as RunResult);
      else p.reject(new Error(msg.message));
    }
  };
  return worker;
}

/** Kills the worker (e.g. after an infinite loop). The next run starts a fresh one. */
function resetWorker() {
  worker?.terminate();
  worker = null;
  ready = false;
  pending.forEach((p) => p.reject(new Error("Python was restarted.")));
  pending.clear();
}

export function onPythonStatus(l: Listener): () => void {
  statusListeners.add(l);
  if (ready) l("ready");
  return () => statusListeners.delete(l);
}

export function warmUpPython() {
  getWorker().postMessage({ type: "warmup" });
}

export function runPython(opts: { code: string; setup?: string; tests?: string; mode: "run" | "submit" }): Promise<RunResult> {
  const w = getWorker();
  const id = nextId++;
  return new Promise<RunResult>((resolve, reject) => {
    // The first run includes the Python download, so only start the clock once ready.
    let timer: ReturnType<typeof setTimeout> | null = null;
    const arm = () => {
      timer = setTimeout(() => {
        if (!pending.has(id)) return;
        pending.delete(id);
        unsubscribe?.();
        resetWorker();
        resolve({
          ok: false,
          stdout: "",
          error: `Your code ran for more than ${TIMEOUT_MS / 1000} seconds and was stopped. Check for an infinite loop.`,
          tests: [],
          passed: opts.mode === "submit" ? false : null,
        });
      }, TIMEOUT_MS);
    };
    let unsubscribe: (() => void) | null = null;
    if (ready) arm();
    else
      unsubscribe = onPythonStatus((s) => {
        if (s === "ready" && !timer) arm();
      });
    pending.set(id, {
      resolve: (r) => {
        if (timer) clearTimeout(timer);
        unsubscribe?.();
        resolve(r);
      },
      reject: (e) => {
        if (timer) clearTimeout(timer);
        unsubscribe?.();
        reject(e);
      },
    });
    w.postMessage({ id, type: "run", code: opts.code, setup: opts.setup ?? "", tests: opts.tests ?? "", mode: opts.mode });
  });
}
