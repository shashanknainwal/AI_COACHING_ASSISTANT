"use client";

// Portfolio and reminder settings: handle, public profile, capstone repo link, weekly emails.

import Link from "next/link";
import { useEffect, useState } from "react";
import { useProfile } from "./SiteProfile";

export default function DashboardSettings({ signedIn }: { signedIn: boolean }) {
  const { profile, source, save } = useProfile();
  const [handle, setHandle] = useState("");
  const [pub, setPub] = useState(false);
  const [capstone, setCapstone] = useState("");
  const [nudges, setNudges] = useState(true);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!profile) return;
    setHandle(profile.handle ?? "");
    setPub(Boolean(profile.publicProfile));
    setCapstone(profile.capstoneUrl ?? "");
    setNudges(profile.nudges !== false);
  }, [profile]);

  const onSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setMsg(null);
    const h = handle.trim().toLowerCase();
    if (pub && !h) {
      setBusy(false);
      return setMsg({ ok: false, text: "Pick a handle before making your portfolio public." });
    }
    const err = await save({ handle: h || null, publicProfile: pub, capstoneUrl: capstone.trim() || null, nudges });
    setBusy(false);
    setMsg(err ? { ok: false, text: err } : { ok: true, text: "Saved." });
  };

  const serverSaved = source === "server";
  const savedHandle = profile?.handle;

  return (
    <form onSubmit={onSave} className="space-y-4 text-sm">
      {source === "local" && (
        <p className="rounded-xl border border-rule bg-paper-2/70 p-3 text-graphite-2">
          {signedIn
            ? "Your account isn't storing profiles yet, so these settings stay in this browser and your portfolio isn't public."
            : "Sign in to publish a portfolio. Settings stay in this browser until then."}
        </p>
      )}
      <div className="grid gap-4 sm:grid-cols-2">
        <label className="block">
          <span className="text-graphite-2">Portfolio handle</span>
          <span className="mt-1 flex items-center rounded-xl border border-rule bg-white px-3">
            <span className="shrink-0 text-graphite-3">/u/</span>
            <input
              value={handle}
              onChange={(e) => setHandle(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, ""))}
              maxLength={30}
              pattern="[a-z0-9-]{3,30}"
              title="3 to 30 lowercase letters, numbers or hyphens"
              className="min-w-0 flex-1 bg-transparent py-2 pl-0.5 outline-none"
              aria-describedby="handle-help"
            />
          </span>
          <span id="handle-help" className="mt-1 block text-xs text-graphite-3">
            3 to 30 lowercase letters, numbers or hyphens.
          </span>
        </label>
        <label className="block">
          <span className="text-graphite-2">Capstone repository (https link)</span>
          <input
            type="url"
            value={capstone}
            onChange={(e) => setCapstone(e.target.value)}
            placeholder="https://github.com/you/capstone"
            maxLength={300}
            className="mt-1 w-full rounded-xl border border-rule bg-white px-3 py-2 placeholder:text-graphite-3"
          />
        </label>
      </div>
      <label className="flex items-start gap-2 text-graphite-2">
        <input type="checkbox" checked={pub} onChange={(e) => setPub(e.target.checked)} className="mt-1 accent-forest" />
        <span>
          Make my portfolio public. It shows only server-verified results: AI-graded rounds passed, loop scores and drill clears, plus your capstone link.
          Your email is never shown.
        </span>
      </label>
      <label className="flex items-start gap-2 text-graphite-2">
        <input type="checkbox" checked={nudges} onChange={(e) => setNudges(e.target.checked)} className="mt-1 accent-forest" />
        <span>Send me a short weekly email with my countdown and this week&apos;s plan (only when an interview date is set).</span>
      </label>
      <div className="flex flex-wrap items-center gap-3">
        <button type="submit" disabled={busy} className="rounded-full bg-graphite px-5 py-2 font-semibold text-paper hover:bg-black disabled:opacity-50">
          {busy ? "Saving…" : "Save settings"}
        </button>
        {serverSaved && profile?.publicProfile && savedHandle && (
          <Link href={`/u/${savedHandle}`} className="font-semibold text-forest hover:underline">
            View my public portfolio →
          </Link>
        )}
        {msg && (
          <span className={msg.ok ? "text-forest" : "text-vermilion"} role={msg.ok ? "status" : "alert"}>
            {msg.text}
          </span>
        )}
      </div>
    </form>
  );
}
