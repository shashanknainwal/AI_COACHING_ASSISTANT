"use client";

// "Start mock loop" for one track: explains the rules, then sets profile.loopMode = { track, startedAt }.
// The lesson pages (LoopBanner) read it to switch off the tutor, hints and reveals, and to mark
// the first graded attempt on each round as the loop score.

import Link from "next/link";
import { useState } from "react";
import { useProfile } from "./SiteProfile";
import { ROLE_LABEL, type RoleTrack } from "./SiteTypes";

export const LOOP_RULES = [
  "Closed book: the AI tutor, hints and solution reveals are off on the loop's lessons.",
  "Your first graded attempt on each round is your loop score. Retries still get feedback, but they don't change the score.",
  "Drills run on their real clock. Levels cleared after time still count, for fewer points.",
  "Take the rounds in order, ideally within a week, like a real onsite.",
  "End the loop when you're done; the tutor and hints come back.",
];

function elapsed(startedAt: string): string {
  const ms = Date.now() - Date.parse(startedAt);
  if (!Number.isFinite(ms) || ms < 0) return "just now";
  const h = Math.floor(ms / 3_600_000);
  if (h < 1) return `${Math.max(1, Math.round(ms / 60_000))} min ago`;
  if (h < 48) return `${h} h ago`;
  return `${Math.floor(h / 24)} days ago`;
}

export default function DashboardLoopStart({ track, firstLessonHref, compact = false }: { track: RoleTrack; firstLessonHref: string; compact?: boolean }) {
  const { profile, source, save } = useProfile();
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const loop = profile?.loopMode ?? null;
  const running = loop?.track === track;
  const otherRunning = loop && loop.track !== track;

  const start = async () => {
    setBusy(true);
    setError(null);
    const err = await save({ loopMode: { track, startedAt: new Date().toISOString() } });
    setBusy(false);
    if (err) setError(err);
    else setOpen(false);
  };
  const end = async () => {
    if (!confirm("End the mock loop? Hints and the tutor come back, and later attempts won't count as loop scores.")) return;
    setBusy(true);
    const err = await save({ loopMode: null });
    setBusy(false);
    if (err) setError(err);
  };

  if (source === "loading") return <div className={compact ? "h-9" : "h-16"} aria-hidden="true" />;

  if (running) {
    return (
      <div className="rounded-2xl border border-vermilion/30 bg-vermilion/[0.06] p-4 text-sm" role="status">
        <p className="flex flex-wrap items-center gap-2 font-semibold text-graphite">
          <span aria-hidden="true" className="h-2 w-2 animate-pulse rounded-full bg-vermilion" />
          {ROLE_LABEL[track]} mock loop running
          <span className="font-normal text-graphite-3">· started {elapsed(loop!.startedAt)}</span>
        </p>
        <div className="mt-3 flex flex-wrap gap-2">
          <Link href={firstLessonHref} className="rounded-full bg-graphite px-4 py-1.5 font-semibold text-paper hover:bg-black">
            Go to the loop →
          </Link>
          <button type="button" onClick={end} disabled={busy} className="rounded-full border border-vermilion/40 px-4 py-1.5 font-semibold text-vermilion hover:bg-vermilion/10 disabled:opacity-50">
            End loop
          </button>
        </div>
        {source === "local" && <p className="mt-2 text-xs text-graphite-3">Saved in this browser only. Sign in to keep loop scores on your account.</p>}
        {error && <p className="mt-2 text-xs text-vermilion" role="alert">{error}</p>}
      </div>
    );
  }

  return (
    <div className={compact ? "" : "rounded-2xl border border-rule bg-white/70 p-4"}>
      {!open ? (
        <button
          type="button"
          onClick={() => setOpen(true)}
          aria-expanded={false}
          className="rounded-full bg-vermilion px-4 py-2 text-sm font-semibold text-white hover:bg-vermilion/90"
        >
          Start mock loop
        </button>
      ) : (
        <div className="rounded-2xl border border-rule bg-white p-4 text-sm">
          <p className="font-serif text-lg font-semibold text-graphite">Before you start the {ROLE_LABEL[track]} loop</p>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-graphite-2">
            {LOOP_RULES.map((r) => (
              <li key={r}>{r}</li>
            ))}
          </ul>
          {otherRunning && <p className="mt-2 text-graphite-2">This ends the {ROLE_LABEL[loop!.track]} loop you have running.</p>}
          <div className="mt-4 flex flex-wrap gap-2">
            <button type="button" onClick={start} disabled={busy} className="rounded-full bg-vermilion px-4 py-2 font-semibold text-white hover:bg-vermilion/90 disabled:opacity-50">
              {busy ? "Starting…" : "Start the loop now"}
            </button>
            <button type="button" onClick={() => setOpen(false)} className="rounded-full border border-rule px-4 py-2 text-graphite-2 hover:bg-paper-2">
              Not yet
            </button>
          </div>
          {error && <p className="mt-2 text-xs text-vermilion" role="alert">{error}</p>}
        </div>
      )}
    </div>
  );
}
