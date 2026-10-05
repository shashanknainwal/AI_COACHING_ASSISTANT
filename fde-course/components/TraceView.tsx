"use client";

import { useState } from "react";
import type { TraceRun, TraceStep } from "@/lib/python-runner";

function prettyInput(input?: string) {
  if (!input) return "";
  try {
    const obj = JSON.parse(input) as Record<string, unknown>;
    return Object.entries(obj)
      .map(([k, v]) => `${k}=${typeof v === "string" ? JSON.stringify(v) : JSON.stringify(v)}`)
      .join(", ");
  } catch {
    return input;
  }
}

function StepNode({ step, index }: { step: TraceStep; index: number }) {
  const tools = (step.blocks ?? []).filter((b) => b.type === "tool_use");
  const texts = (step.blocks ?? []).filter((b) => b.type === "text" && b.text);
  const thought = (step.blocks ?? []).some((b) => b.type === "thinking");
  const results = new Map((step.results ?? []).map((r) => [r.id, r]));
  const final = step.stop_reason && step.stop_reason !== "tool_use";

  return (
    <li className="check-in relative pb-4 pl-7" style={{ animationDelay: `${index * 90}ms` }}>
      <span className="absolute bottom-0 left-[7px] top-4 w-px bg-console-line" aria-hidden="true" />
      <span
        className={`absolute left-0 top-1 flex h-[15px] w-[15px] items-center justify-center rounded-full border text-[8px] ${
          step.error ? "border-amber-400 bg-amber-400/20 text-amber-300" : final ? "border-emerald-400 bg-emerald-400 text-console" : "border-sky-400/70 bg-console-2 text-sky-300"
        }`}
        aria-hidden="true"
      >
        {step.error ? "!" : final ? "✓" : ""}
      </span>

      <div className="flex flex-wrap items-baseline gap-x-2 font-mono text-[11px] text-gray-500">
        <span className="text-gray-300">Call {index + 1}</span>
        {step.error ? (
          <span className="text-amber-300">
            {step.error}
            {step.attempt >= 0 ? " · SDK retries" : ""}
          </span>
        ) : (
          <>
            <span>stop: {step.stop_reason}</span>
            {step.usage && (
              <span>
                {step.usage.input}→{step.usage.output} tok{step.usage.cache_read ? ` · ${step.usage.cache_read} cached` : ""}
              </span>
            )}
          </>
        )}
      </div>

      {thought && <div className="mt-1 font-mono text-[11px] italic text-gray-600">thinking…</div>}

      {tools.map((t) => {
        const r = t.id ? results.get(t.id) : undefined;
        return (
          <div key={t.id} className="mt-1.5 rounded-lg border border-console-line bg-console-2/70 p-2.5">
            <div className="font-mono text-xs">
              <span className="text-sky-300">{t.name}</span>
              <span className="text-gray-500">(</span>
              <span className="text-gray-300">{prettyInput(t.input)}</span>
              <span className="text-gray-500">)</span>
            </div>
            {r && (
              <div className={`mt-1.5 flex gap-2 border-t border-console-line pt-1.5 font-mono text-[11px] leading-relaxed ${r.is_error ? "text-red-300" : "text-gray-400"}`}>
                <span className={r.is_error ? "text-red-400" : "text-emerald-400"}>{r.is_error ? "✗" : "→"}</span>
                <span className="min-w-0 break-words">{r.content}</span>
              </div>
            )}
          </div>
        );
      })}

      {texts.map((t, i) => (
        <p key={i} className={`mt-1.5 text-[13px] leading-relaxed ${final ? "font-serif text-gray-100" : "text-gray-400"}`}>
          {final ? <>&ldquo;{t.text}&rdquo;</> : t.text}
        </p>
      ))}
    </li>
  );
}

export default function TraceView({ trace }: { trace: TraceRun[] }) {
  const [open, setOpen] = useState(0);
  if (trace.length === 0) {
    return <div className="font-mono text-sm text-gray-600">Run code that calls Claude to see each request, tool call and result here.</div>;
  }
  const calls = trace.reduce((s, r) => s + r.steps.length, 0);
  const tools = trace.reduce((s, r) => s + r.steps.reduce((t, st) => t + (st.blocks ?? []).filter((b) => b.type === "tool_use").length, 0), 0);
  const tokens = trace.reduce((s, r) => s + r.steps.reduce((t, st) => t + (st.usage ? st.usage.input + st.usage.output : 0), 0), 0);
  const run = trace[Math.min(open, trace.length - 1)];

  return (
    <div>
      <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1 font-mono text-[11px] uppercase tracking-wider text-gray-500">
        <span className="text-gray-300">Agent trace</span>
        <span>
          {trace.length} run{trace.length === 1 ? "" : "s"}
        </span>
        <span>{calls} API calls</span>
        <span>{tools} tool calls</span>
        <span>~{tokens.toLocaleString()} tokens</span>
      </div>

      {trace.length > 1 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {trace.map((r, i) => (
            <button
              key={i}
              onClick={() => setOpen(i)}
              title={r.question}
              className={`rounded-md px-2.5 py-1 font-mono text-[11px] ${i === open ? "bg-gray-100 text-console" : "bg-console-2 text-gray-400 hover:text-gray-200"}`}
            >
              Run {i + 1}
            </button>
          ))}
        </div>
      )}

      <div className="mt-4 rounded-lg border-l-2 border-sky-400/50 bg-console-2/50 px-3 py-2 text-[13px] text-gray-300">
        <span className="mr-2 font-mono text-[10px] uppercase tracking-wider text-gray-500">User</span>
        {run.question || "(no text)"}
      </div>
      <ol key={open} className="mt-4">
        {run.steps.map((s, i) => (
          <StepNode key={i} step={s} index={i} />
        ))}
      </ol>
    </div>
  );
}
