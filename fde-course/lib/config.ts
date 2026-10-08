// Which external services are switched on is decided purely by environment variables.
//
//   dev          `next dev` with no Supabase keys: everything unlocked for previewing.
//   unconfigured production build with no Supabase keys: free modules only, nothing to buy.
//   live         Supabase keys set: logins work, paid modules need a purchase.
//
// PREVIEW_UNLOCK_ALL=true turns a Vercel *preview* deployment into dev mode (everything
// unlocked) for testing. It is ignored on production deployments, so fdeplaybook.dev
// always keeps its paywall.

export const FREE_MODULES = new Set(["01-fde-role-and-mindset", "c1-how-labs-hire"]);

/**
 * The three-track course (shared core + Applied AI Engineer + Applied AI Architect + FDE).
 * Shown in dev and on unlocked previews; production keeps the original FDE course until
 * TRACKS_LIVE=true is set at launch.
 */
export function tracksEnabled(): boolean {
  return appMode() === "dev" || process.env.TRACKS_LIVE === "true";
}

/** Claude-backed actions (tutor, grading, role-play turns) a learner may make per day. */
export function aiDailyLimit(): number {
  const n = Number(process.env.AI_DAILY_LIMIT);
  return Number.isFinite(n) && n > 0 ? n : 60;
}

export const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL ?? "";
// The Vercel–Supabase integration names the public key NEXT_PUBLIC_SUPABASE_ANON_KEY; either works.
export const SUPABASE_PUBLISHABLE_KEY = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

/** Server-only key that can write purchases. The integration names it SUPABASE_SERVICE_ROLE_KEY. */
export function supabaseSecretKey(): string {
  return process.env.SUPABASE_SECRET_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY || "";
}

export const supabaseConfigured = Boolean(SUPABASE_URL && SUPABASE_PUBLISHABLE_KEY);

export type AppMode = "dev" | "unconfigured" | "live";

export function previewUnlocked(): boolean {
  return process.env.VERCEL_ENV === "preview" && process.env.PREVIEW_UNLOCK_ALL === "true";
}

export function appMode(): AppMode {
  if (previewUnlocked()) return "dev";
  if (supabaseConfigured) return "live";
  return process.env.NODE_ENV === "production" ? "unconfigured" : "dev";
}

export function stripeConfigured(): boolean {
  return Boolean(process.env.STRIPE_SECRET_KEY);
}

export const PRICE_USD = 149;

/** Emails that get full access without paying (comma-separated in FREE_ACCESS_EMAILS), e.g. the instructor. */
export function freeAccessEmails(): Set<string> {
  return new Set(
    (process.env.FREE_ACCESS_EMAILS ?? "")
      .split(",")
      .map((e) => e.trim().toLowerCase())
      .filter(Boolean),
  );
}

export const SITE_NAME = "FDE Playbook";
export const SITE_URL = (process.env.NEXT_PUBLIC_SITE_URL || "https://fdeplaybook.dev").replace(/\/$/, "");
