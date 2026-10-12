"use client";

// Shown across the top of mock-loop lessons while a loop is running: the session clock and an
// "End loop" button. During the loop the tutor, hints and reveals are off and the first graded
// attempt on each lesson is recorded as the loop score.

import { useState } from "react";
import { clock, useTicker, type LoopState } from "./practice-shared";

export default function LoopBanner({ loop, onEnd }: { loop: LoopState; onEnd: () => Promise<void> }) {
  const now = useTicker(true);
  const [ending, setEnding] = useState(false);
  const started = Date.parse(loop.startedAt);
  const elapsed = Number.isFinite(started) ? now - started : 0;
  return (
    <div role="region" aria-label="Mock loop" className="flex shrink-0 flex-wrap items-center gap-x-4 gap-y-1 border-b border-vermilion/30 bg-vermilion/[0.08] px-4 py-2 text-sm">
      <span className="flex items-center gap-2 font-mono text-[11px] font-semibold uppercase tracking-[0.14em] text-vermilion">
        <span aria-hidden="true" className="h-2 w-2 animate-pulse rounded-full bg-vermilion" />
        Mock loop running
      </span>
      <span className="font-mono tabular-nums text-graphite" aria-label={`Loop session time ${clock(elapsed)}`}>
        {clock(elapsed)}
      </span>
      <span className="hidden text-graphite-2 md:inline">Tutor, hints and reveals are off. Your first graded attempt on each round is your loop score.</span>
      <button
        type="button"
        disabled={ending}
        onClick={async () => {
          if (!confirm("End the mock loop? Hints and the tutor come back, and later attempts won't count as loop scores.")) return;
          setEnding(true);
          await onEnd();
          setEnding(false);
        }}
        className="ml-auto rounded-lg border border-vermilion/40 px-3 py-1 text-xs font-semibold text-vermilion hover:bg-vermilion/10 disabled:opacity-50"
      >
        {ending ? "Ending…" : "End loop"}
      </button>
    </div>
  );
}
