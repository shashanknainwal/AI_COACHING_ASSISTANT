// Which external services are switched on is decided purely by environment variables.
//
//   dev          `next dev` with no Supabase keys: everything unlocked for previewing.
//   unconfigured production build with no Supabase keys: free modules only, nothing to buy.
//   live         Supabase keys set: logins work, paid modules need a purchase.

export const FREE_MODULES = new Set(["01-fde-role-and-mindset"]);

export const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL ?? "";
export const SUPABASE_PUBLISHABLE_KEY = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY ?? "";

export const supabaseConfigured = Boolean(SUPABASE_URL && SUPABASE_PUBLISHABLE_KEY);

export type AppMode = "dev" | "unconfigured" | "live";

export function appMode(): AppMode {
  if (supabaseConfigured) return "live";
  return process.env.NODE_ENV === "production" ? "unconfigured" : "dev";
}

export function stripeConfigured(): boolean {
  return Boolean(process.env.STRIPE_SECRET_KEY);
}

export const PRICE_USD = 149;

export const SITE_NAME = "FDE Playbook";
export const SITE_URL = (process.env.NEXT_PUBLIC_SITE_URL || "https://fdeplaybook.dev").replace(/\/$/, "");
