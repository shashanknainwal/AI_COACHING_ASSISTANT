"use client";

// "Did you get the offer?" survey → POST /api/outcome. Quoting needs the explicit consent box.
// When the server isn't recording outcomes, the answer is kept in this browser only.

import { useState } from "react";

const RESULTS: [string, string][] = [
  ["offer", "Yes, I got an offer"],
  ["no-offer", "No offer this time"],
  ["pending", "Still waiting"],
  ["withdrew", "I withdrew"],
];

const TRACKS: [string, string][] = [
  ["engineer", "Applied AI Engineer"],
  ["architect", "Applied AI Architect"],
  ["fde", "Forward Deployed Engineer"],
];

export default function DashboardOutcome({ defaultTrack }: { defaultTrack?: string }) {
  const [track, setTrack] = useState(defaultTrack ?? "");
  const [result, setResult] = useState("");
  const [company, setCompany] = useState("");
  const [note, setNote] = useState("");
  const [consent, setConsent] = useState(false);
  const [state, setState] = useState<"idle" | "busy" | "done" | "local">("idle");
  const [error, setError] = useState<string | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!result) {
      setError("Pick one answer.");
      return;
    }
    setError(null);
    setState("busy");
    const body = { track: track || null, result, company, note, consentQuote: consent };
    try {
      const res = await fetch("/api/outcome", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      const data = (await res.json().catch(() => ({}))) as { ok?: boolean; disabled?: boolean; error?: string };
      if (data.ok) return setState("done");
      if (!data.disabled) {
        setState("idle");
        return setError(data.error ?? "Couldn't send. Try again in a minute.");
      }
    } catch {
      // Offline: keep it locally.
    }
    try {
      window.localStorage.setItem("fde-outcome-v1", JSON.stringify({ ...body, at: new Date().toISOString() }));
    } catch {
      // Storage blocked.
    }
    setState("local");
  };

  if (state === "done" || state === "local") {
    return (
      <p className="rounded-2xl border border-forest/30 bg-forest/5 p-4 text-sm text-graphite-2" role="status">
        Thank you. {result === "offer" ? "Congratulations on the offer. " : ""}
        {state === "local" ? "Your answer is saved in this browser; sign in so it reaches us." : "Your answer helps us make the course better."}
      </p>
    );
  }

  return (
    <form onSubmit={submit} className="space-y-4 text-sm" aria-labelledby="outcome-title">
      <div>
        <p id="outcome-title" className="font-serif text-lg font-semibold text-graphite">
          Did you get the offer?
        </p>
        <p className="mt-1 text-graphite-3">Tell us how your real interview went. It takes 30 seconds and tells us what to improve.</p>
      </div>
      <fieldset>
        <legend className="sr-only">Result</legend>
        <div className="grid gap-2 sm:grid-cols-2">
          {RESULTS.map(([v, label]) => (
            <label key={v} className={`flex cursor-pointer items-center gap-2 rounded-xl border px-3 py-2 ${result === v ? "border-graphite bg-white" : "border-rule bg-white/60"}`}>
              <input type="radio" name="outcome-result" value={v} checked={result === v} onChange={() => setResult(v)} className="accent-forest" />
              {label}
            </label>
          ))}
        </div>
      </fieldset>
      <div className="grid gap-3 sm:grid-cols-2">
        <label className="block">
          <span className="text-graphite-2">Role you interviewed for</span>
          <select value={track} onChange={(e) => setTrack(e.target.value)} className="mt-1 w-full rounded-xl border border-rule bg-white px-3 py-2">
            <option value="">Prefer not to say</option>
            {TRACKS.map(([v, l]) => (
              <option key={v} value={v}>
                {l}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="text-graphite-2">Company (optional)</span>
          <input value={company} onChange={(e) => setCompany(e.target.value)} maxLength={120} className="mt-1 w-full rounded-xl border border-rule bg-white px-3 py-2" />
        </label>
      </div>
      <label className="block">
        <span className="text-graphite-2">Anything you'd like to tell us (optional)</span>
        <textarea value={note} onChange={(e) => setNote(e.target.value)} maxLength={2000} rows={3} className="mt-1 w-full rounded-xl border border-rule bg-white px-3 py-2" />
      </label>
      <label className="flex items-start gap-2 text-graphite-2">
        <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} className="mt-1 accent-forest" />
        <span>You may quote my note on the site, with my first name only. Leave this unticked and we&apos;ll never publish it.</span>
      </label>
      {error && (
        <p className="text-vermilion" role="alert">
          {error}
        </p>
      )}
      <button type="submit" disabled={state === "busy"} className="rounded-full bg-graphite px-5 py-2 font-semibold text-paper hover:bg-black disabled:opacity-50">
        {state === "busy" ? "Sending…" : "Send"}
      </button>
    </form>
  );
}
