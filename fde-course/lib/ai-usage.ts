import "server-only";
import { aiDailyLimit } from "@/lib/config";
import { isStaff, type Viewer } from "@/lib/access";
import { createClient } from "@/lib/supabase/server";

/**
 * Counts one Claude-backed action against the learner's daily limit.
 * Returns an error message when they're over it, or null when the call may go ahead.
 */
export async function takeAiCall(viewer: Viewer): Promise<string | null> {
  if (viewer.mode !== "live" || !viewer.user || isStaff(viewer)) return null;
  const supabase = await createClient();
  const { data, error } = await supabase.rpc("use_ai_call");
  if (error) {
    // Most likely supabase/migrations/0002_ai_usage.sql hasn't been run yet. Don't block learners for that.
    console.error("takeAiCall: usage counter failed", error.message);
    return null;
  }
  if (typeof data === "number" && data > aiDailyLimit()) {
    return `You've used today's ${aiDailyLimit()} AI reviews and tutor answers. They reset at midnight UTC.`;
  }
  return null;
}
