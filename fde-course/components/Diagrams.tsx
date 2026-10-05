"use client";

import { useEffect, useRef, useState } from "react";

// Interactive diagrams embedded in readings with <div data-diagram="name"></div>.

interface Step {
  actor: string;
  label: string;
  detail: string;
}

interface StepDiagramSpec {
  kind: "steps";
  title: string;
  caption: string;
  steps: Step[];
  /** Index the "repeat" arrow jumps back to after the step before the last (agent loop). */
  loopTo?: number;
}

const ACTOR_TONE: Record<string, string> = {
  You: "bg-graphite text-paper",
  "Your code": "bg-forest text-white",
  Claude: "bg-vermilion text-white",
  Search: "bg-[#0e7490] text-white",
  API: "bg-[#7c3aed] text-white",
};

const DIAGRAMS: Record<string, StepDiagramSpec> = {
  "tool-cycle": {
    kind: "steps",
    title: "The tool-use cycle",
    caption: "One question, two API calls. Claude asks; your code decides and runs.",
    steps: [
      { actor: "You", label: "Question + tools", detail: "messages=[{\"role\": \"user\", \"content\": \"Where's my order B-1001?\"}], tools=[lookup_order]" },
      { actor: "Claude", label: "stop_reason: tool_use", detail: "A tool_use block: lookup_order(order_id=\"B-1001\") with id toolu_01. Claude has not run anything." },
      { actor: "Your code", label: "Run the tool", detail: "Validate the input and the customer's permissions, then call your order system. This is where safety lives." },
      { actor: "You", label: "History + tool_result", detail: "Append Claude's full turn, then one user message with a tool_result for toolu_01 (is_error: true if it failed)." },
      { actor: "Claude", label: "stop_reason: end_turn", detail: "\"Order B-1001 is shipped. Its shipment ID is SHP-1003.\" The final answer uses your data." },
    ],
  },
  "agent-loop": {
    kind: "steps",
    title: "The agent loop",
    caption: "Call, run every requested tool, send all results back, repeat until Claude stops asking, with a step budget.",
    loopTo: 0,
    steps: [
      { actor: "Your code", label: "Call Claude", detail: "Send the system prompt, tools and the full message history. Count this API call against max_steps." },
      { actor: "Claude", label: "tool_use?", detail: "If stop_reason is tool_use, Claude wants one or more tools. Anything else means it's done." },
      { actor: "Your code", label: "Run every tool", detail: "Execute each tool_use block through your guarded executor; errors become is_error results, not crashes." },
      { actor: "Your code", label: "One message of results", detail: "Append Claude's turn, then a single user message with every tool_result. Record each call in the trace." },
      { actor: "Claude", label: "end_turn → answer", detail: "When Claude stops asking for tools, return its text. If max_steps runs out first, stop and hand off to a human." },
    ],
  },
  "rag-pipeline": {
    kind: "steps",
    title: "A RAG pipeline",
    caption: "Retrieval decides what Claude can know. Measure it separately from the answer.",
    steps: [
      { actor: "Your code", label: "Chunk", detail: "Split documents into self-contained chunks with stable IDs (KB-01#2) and metadata: title, URL, permissions." },
      { actor: "Search", label: "Index", detail: "Build a keyword index (TF-IDF/BM25), embeddings, or both. Include titles so chunks make sense alone." },
      { actor: "Search", label: "Retrieve top k", detail: "Score chunks for the question and keep the best few. If nothing relevant comes back, skip Claude and say so." },
      { actor: "Your code", label: "Grounded prompt", detail: "<documents> first, <question> last, and rules: answer only from the documents, cite IDs, say when they don't cover it." },
      { actor: "Claude", label: "Answer + citations", detail: "A structured answer: {answer, citations, answerable}." },
      { actor: "Your code", label: "Check citations", detail: "Drop cited IDs that weren't retrieved. No valid citation left? Show the honest fallback instead." },
    ],
  },
  "prompt-caching": {
    kind: "steps",
    title: "How prompt caching pays off",
    caption: "Caching is a prefix match: stable content first, anything that changes last.",
    steps: [
      { actor: "You", label: "Request 1", detail: "tools + 3,000-token system prompt (marked for caching) + the ticket. The prefix is written to the cache: cache_creation_input_tokens = 3,000." },
      { actor: "API", label: "Request 2, same prefix", detail: "Identical tools and system prompt, a different ticket. cache_read_input_tokens = 3,000, billed at a fraction of the input price." },
      { actor: "You", label: "A timestamp sneaks in", detail: "Someone adds today's date and time to the start of the system prompt. Every request's prefix is now unique." },
      { actor: "API", label: "Cache misses, every time", detail: "cache_read_input_tokens stays 0. Cost and latency jump, and uncached input can push you into rate limits. Verify with usage." },
    ],
  },
};

function StepDiagram({ spec }: { spec: StepDiagramSpec }) {
  const [active, setActive] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [round, setRound] = useState(1);
  const ref = useRef<HTMLDivElement>(null);
  const n = spec.steps.length;

  // Start playing once the diagram scrolls into view (unless the reader prefers reduced motion).
  useEffect(() => {
    if (typeof window === "undefined" || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) {
          setPlaying(true);
          io.disconnect();
        }
      },
      { threshold: 0.5 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  useEffect(() => {
    if (!playing) return;
    const t = setTimeout(() => {
      setActive((a) => {
        if (spec.loopTo !== undefined && a === n - 2 && round < 2) {
          setRound((r) => r + 1);
          return spec.loopTo;
        }
        if (a === n - 1) {
          setPlaying(false);
          return a;
        }
        return a + 1;
      });
    }, 2300);
    return () => clearTimeout(t);
  }, [playing, active, n, round, spec.loopTo]);

  const go = (i: number) => {
    setPlaying(false);
    setActive(Math.max(0, Math.min(n - 1, i)));
  };
  const replay = () => {
    setRound(1);
    setActive(0);
    setPlaying(true);
  };
  const step = spec.steps[active];

  return (
    <figure ref={ref} className="not-prose my-8 overflow-hidden rounded-2xl border border-rule bg-white/75 shadow-[0_20px_40px_-32px_rgba(29,27,22,0.6)]">
      <div className="flex items-center gap-3 border-b border-rule bg-paper-2/70 px-4 py-2.5">
        <span className="font-mono text-[11px] font-semibold uppercase tracking-[0.14em] text-vermilion">Diagram</span>
        <span className="font-serif text-[15px] font-semibold text-graphite">{spec.title}</span>
        <div className="ml-auto flex items-center gap-1">
          <button onClick={() => go(active - 1)} className="rounded-md px-2 py-0.5 text-graphite-2 hover:bg-paper-3" aria-label="Previous step">
            ‹
          </button>
          <button
            onClick={() => (playing ? setPlaying(false) : active === n - 1 ? replay() : setPlaying(true))}
            className="rounded-md bg-graphite px-2.5 py-0.5 text-xs font-semibold text-paper"
          >
            {playing ? "Pause" : active === n - 1 ? "Replay" : "Play"}
          </button>
          <button onClick={() => go(active + 1)} className="rounded-md px-2 py-0.5 text-graphite-2 hover:bg-paper-3" aria-label="Next step">
            ›
          </button>
        </div>
      </div>

      <ol className="flex flex-wrap items-stretch gap-2 px-4 pt-5">
        {spec.steps.map((s, i) => {
          const state = i === active ? "active" : i < active || (spec.loopTo !== undefined && round > 1) ? "past" : "future";
          return (
            <li key={i} className="flex min-w-[8.5rem] flex-1 items-center gap-2">
              <button
                onClick={() => go(i)}
                className={`flex-1 rounded-xl border px-3 py-2.5 text-left transition duration-300 ${
                  state === "active"
                    ? "-translate-y-0.5 border-graphite bg-white shadow-[0_12px_24px_-16px_rgba(29,27,22,0.7)]"
                    : state === "past"
                      ? "border-rule bg-paper/70"
                      : "border-dashed border-rule bg-transparent opacity-60"
                }`}
              >
                <span className={`inline-block rounded px-1.5 py-0.5 font-mono text-[9px] font-semibold uppercase tracking-wider ${ACTOR_TONE[s.actor] ?? "bg-graphite text-paper"}`}>
                  {s.actor}
                </span>
                <span className="mt-1.5 block text-[13px] font-semibold leading-snug text-graphite">{s.label}</span>
              </button>
              {i < n - 1 && (
                <span className={`hidden text-lg transition sm:block ${i < active ? "text-forest" : "text-paper-3"}`} aria-hidden="true">
                  →
                </span>
              )}
            </li>
          );
        })}
      </ol>

      {spec.loopTo !== undefined && (
        <div className="px-4 pt-2 font-mono text-[11px] text-graphite-3">
          ↺ repeats while Claude asks for tools · loop {round}
        </div>
      )}

      <div className="m-4 rounded-xl bg-graphite p-4 text-paper" aria-live="polite">
        <div className="font-mono text-[10px] uppercase tracking-[0.14em] text-emerald-300">
          Step {active + 1} of {n} · {step.actor}
        </div>
        <p key={active} className="check-in mt-1.5 text-[14px] leading-relaxed text-paper/90">
          {step.detail}
        </p>
      </div>
      <figcaption className="px-4 pb-4 text-sm text-graphite-3">{spec.caption}</figcaption>
    </figure>
  );
}

/** Interactive state machine: break the API, let time pass, and watch the breaker react. */
function CircuitBreakerDiagram() {
  const THRESHOLD = 3;
  const COOLDOWN = 30;
  const [state, setState] = useState<"closed" | "open" | "half_open">("closed");
  const [failures, setFailures] = useState(0);
  const [clock, setClock] = useState(0);
  const [openedAt, setOpenedAt] = useState<number | null>(null);
  const [log, setLog] = useState<string[]>(["t=0s · closed: requests go to Claude"]);

  const add = (line: string) => setLog((l) => [`t=${clock}s · ${line}`, ...l].slice(0, 5));

  const request = (succeeds: boolean) => {
    const current = state;
    if (current === "open") {
      add("open: skipped Claude, used the rules fallback instantly");
      return;
    }
    if (succeeds) {
      setState("closed");
      setFailures(0);
      setOpenedAt(null);
      add(current === "half_open" ? "half-open trial succeeded → closed" : "Claude answered → closed");
      return;
    }
    const f = failures + 1;
    setFailures(f);
    if (current === "half_open" || f >= THRESHOLD) {
      setState("open");
      setOpenedAt(clock);
      add(current === "half_open" ? "half-open trial failed → open again" : `${f} failures in a row → open`);
    } else {
      add(`API error ${f} of ${THRESHOLD} → fallback, still closed`);
    }
  };

  const wait = () => {
    const t = clock + 10;
    const cooled = state === "open" && openedAt !== null && t - openedAt >= COOLDOWN;
    setClock(t);
    if (cooled) setState("half_open");
    setLog((l) => [`t=${t}s · 10 seconds pass${cooled ? " → cooldown over, half-open" : ""}`, ...l].slice(0, 5));
  };

  const nodes: { key: typeof state; label: string; sub: string }[] = [
    { key: "closed", label: "Closed", sub: "call Claude" },
    { key: "open", label: "Open", sub: "skip Claude, use fallback" },
    { key: "half_open", label: "Half-open", sub: "one trial request" },
  ];

  return (
    <figure className="not-prose my-8 overflow-hidden rounded-2xl border border-rule bg-white/75 shadow-[0_20px_40px_-32px_rgba(29,27,22,0.6)]">
      <div className="flex items-center gap-3 border-b border-rule bg-paper-2/70 px-4 py-2.5">
        <span className="font-mono text-[11px] font-semibold uppercase tracking-[0.14em] text-vermilion">Try it</span>
        <span className="font-serif text-[15px] font-semibold text-graphite">Circuit breaker</span>
        <span className="ml-auto font-mono text-[11px] text-graphite-3">
          failures {failures}/{THRESHOLD} · t={clock}s
        </span>
      </div>
      <div className="grid gap-3 p-4 sm:grid-cols-3">
        {nodes.map((n) => (
          <div
            key={n.key}
            className={`rounded-xl border px-4 py-3 transition duration-300 ${
              state === n.key ? "border-graphite bg-graphite text-paper shadow-[0_14px_28px_-18px_rgba(29,27,22,0.8)]" : "border-rule bg-paper/60 text-graphite"
            }`}
          >
            <div className="font-serif text-lg font-semibold">{n.label}</div>
            <div className={`text-xs ${state === n.key ? "text-paper/70" : "text-graphite-3"}`}>{n.sub}</div>
          </div>
        ))}
      </div>
      <div className="flex flex-wrap gap-2 px-4">
        <button onClick={() => request(false)} className="rounded-lg bg-vermilion px-3 py-1.5 text-sm font-semibold text-white">
          API call fails
        </button>
        <button onClick={() => request(true)} className="rounded-lg bg-forest px-3 py-1.5 text-sm font-semibold text-white">
          API call succeeds
        </button>
        <button onClick={wait} className="rounded-lg border border-rule px-3 py-1.5 text-sm font-semibold text-graphite">
          Wait 10 s
        </button>
      </div>
      <ol className="m-4 space-y-1 rounded-xl bg-graphite p-4 font-mono text-[12px] text-paper/85">
        {log.map((l, i) => (
          <li key={`${l}-${i}`} className={i === 0 ? "check-in text-emerald-300" : "opacity-70"}>
            {l}
          </li>
        ))}
      </ol>
      <figcaption className="px-4 pb-4 text-sm text-graphite-3">
        Threshold {THRESHOLD} consecutive failures, cooldown {COOLDOWN} s. Fail three times, try a request while open, then wait 30 s and try again.
      </figcaption>
    </figure>
  );
}

export function Diagram({ name }: { name: string }) {
  if (name === "circuit-breaker") return <CircuitBreakerDiagram />;
  const spec = DIAGRAMS[name];
  return spec ? <StepDiagram spec={spec} /> : null;
}

export const DIAGRAM_PATTERN = /<div data-diagram="([a-z-]+)"><\/div>/;
