import "server-only";
import { cache } from "react";
import { appMode, FREE_MODULES, freeAccessEmails, stripeConfigured, type AppMode } from "@/lib/config";
import { createClient } from "@/lib/supabase/server";

export interface Viewer {
  mode: AppMode;
  user: { id: string; email: string | null } | null;
  hasPurchased: boolean;
  canBuy: boolean;
}

/** Who is looking at the page, and what they've paid for. Cached per request. */
export const getViewer = cache(async (): Promise<Viewer> => {
  const mode = appMode();
  if (mode !== "live") {
    return { mode, user: null, hasPurchased: mode === "dev", canBuy: false };
  }

  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return { mode, user: null, hasPurchased: false, canBuy: stripeConfigured() };

  // Signing in proves the email (magic link), so listed emails can skip the purchase check.
  if (user.email && freeAccessEmails().has(user.email.toLowerCase())) {
    return { mode, user: { id: user.id, email: user.email }, hasPurchased: true, canBuy: false };
  }

  const { data, error } = await supabase
    .from("purchases")
    .select("id")
    .eq("user_id", user.id)
    .eq("status", "paid")
    .limit(1);
  if (error) console.error("getViewer: purchases lookup failed", error.message);

  return {
    mode,
    user: { id: user.id, email: user.email ?? null },
    hasPurchased: Boolean(data && data.length > 0),
    canBuy: stripeConfigured(),
  };
});

export function canAccessModule(viewer: Viewer, moduleSlug: string): boolean {
  return FREE_MODULES.has(moduleSlug) || viewer.hasPurchased;
}

/** The subset of Viewer that is safe and useful to pass to client components. */
export interface ClientViewer {
  mode: AppMode;
  signedIn: boolean;
  email: string | null;
  hasPurchased: boolean;
  canBuy: boolean;
}

export function toClientViewer(v: Viewer): ClientViewer {
  return { mode: v.mode, signedIn: Boolean(v.user), email: v.user?.email ?? null, hasPurchased: v.hasPurchased, canBuy: v.canBuy };
}
