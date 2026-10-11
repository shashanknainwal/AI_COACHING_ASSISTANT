"use client";

// The learner profile in the browser: /api/profile when it's available, otherwise a copy in
// localStorage ("fde-profile-v1") so onboarding, loop mode and settings still work in dev mode,
// when signed out, or before the profiles table exists.

import { useCallback, useEffect, useState } from "react";
import type { Profile } from "./SiteTypes";

export const PROFILE_KEY = "fde-profile-v1";

export function readLocalProfile(): Profile | null {
  try {
    const raw = window.localStorage.getItem(PROFILE_KEY);
    const p = raw ? (JSON.parse(raw) as Profile) : null;
    return p && typeof p === "object" ? p : null;
  } catch {
    return null;
  }
}

function writeLocalProfile(p: Profile) {
  try {
    window.localStorage.setItem(PROFILE_KEY, JSON.stringify(p));
  } catch {
    // Storage blocked: the profile lasts for this visit.
  }
}

export type ProfileSource = "loading" | "server" | "local";

export function useProfile() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [source, setSource] = useState<ProfileSource>("loading");

  useEffect(() => {
    let live = true;
    (async () => {
      try {
        const res = await fetch("/api/profile", { cache: "no-store" });
        const data = (await res.json()) as { disabled?: boolean; profile?: Profile | null };
        if (!live) return;
        if (res.ok && !data.disabled) {
          setProfile(data.profile ?? null);
          setSource("server");
          return;
        }
      } catch {
        // Offline or no route: fall through to the local copy.
      }
      if (!live) return;
      setProfile(readLocalProfile());
      setSource("local");
    })();
    return () => {
      live = false;
    };
  }, []);

  /** Saves a partial profile. Returns an error message, or null on success. */
  const save = useCallback(async (patch: Partial<Profile>): Promise<string | null> => {
    const local = () => {
      const base = readLocalProfile() ?? {};
      const next: Profile = { ...base, ...patch };
      if (patch.loopMode) next.loopMode = { track: patch.loopMode.track, startedAt: new Date().toISOString() };
      writeLocalProfile(next);
      setProfile(next);
      setSource("local");
      return null;
    };
    try {
      const res = await fetch("/api/profile", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(patch) });
      const data = (await res.json().catch(() => ({}))) as { disabled?: boolean; profile?: Profile; error?: string };
      if (data.disabled) return local();
      if (!res.ok) return data.error ?? "Couldn't save. Try again in a minute.";
      if (data.profile) setProfile(data.profile);
      setSource("server");
      return null;
    } catch {
      return local();
    }
  }, []);

  return { profile, source, save };
}

/** Whole days from today (local time) to a YYYY-MM-DD date. */
export function daysUntil(date: string | null | undefined): number | null {
  if (!date || !/^\d{4}-\d{2}-\d{2}$/.test(date)) return null;
  const [y, m, d] = date.split("-").map(Number);
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  return Math.round((new Date(y, m - 1, d).getTime() - today) / 86_400_000);
}

export function countdownText(days: number | null): string | null {
  if (days === null) return null;
  if (days < 0) return "Your interview date has passed";
  if (days === 0) return "Your interview is today";
  return `${days} day${days === 1 ? "" : "s"} to your interview`;
}
