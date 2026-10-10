import "server-only";
import { aiDailyLimit } from "@/lib/config";
import { isStaff, type Viewer } from "@/lib/access";
import { createClient } from "@/lib/supabase/server";

/** Claude-backed calls allowed per day across all learners (AI_GLOBAL_DAILY_LIMIT, default 3000). */
export function aiGlobalDailyLimit(): number {
  const n = Number(process.env.AI_GLOBAL_DAILY_LIMIT);
  return Number.isFinite(n) && n > 0 ? Math.floor(n) : 3000;
}

const UNAVAILABLE = "AI feedback is paused for a moment because we couldn't check today's usage. Try again in a few minutes.";

/**
 * Counts one Claude-backed action against the learner's daily limit and the site-wide breaker.
 * Returns an error message when the call must not go ahead, or null when it may.
 *
 * Fails closed in live mode: if either usage check errors (for example the 0002/0003 SQL
 * hasn't been run), learners get a friendly error instead of unmetered Opus calls.
 * Staff (FREE_ACCESS_EMAILS) are exempt from both limits and from the fail-closed rule.
 */
export async function takeAiCall(viewer: Viewer): Promise<string | null> {
  if (viewer.mode !== "live" || !viewer.user || isStaff(viewer)) return null;
  const supabase = await createClient();
  const perUser = aiDailyLimit();

  // Global breaker first, so a tripped breaker doesn't also burn the learner's own quota.
  const global = await supabase.rpc("ai_usage_global_today", { per_user_cap: perUser });
  if (global.error || typeof global.data !== "number") {
    console.error("takeAiCall: global usage check failed", global.error?.message ?? "no data");
    return UNAVAILABLE;
  }
  if (global.data >= aiGlobalDailyLimit()) {
    console.error(`takeAiCall: global daily AI limit reached (${global.data}/${aiGlobalDailyLimit()})`);
    return "AI feedback has reached today's site-wide limit. It resets at midnight UTC; your work is saved.";
  }

  const { data, error } = await supabase.rpc("use_ai_call");
  if (error || typeof data !== "number") {
    console.error("takeAiCall: usage counter failed", error?.message ?? "no data");
    return UNAVAILABLE;
  }
  if (data > perUser) {
    return `You've used today's ${perUser} AI reviews and tutor answers. They reset at midnight UTC.`;
  }
  return null;
}
