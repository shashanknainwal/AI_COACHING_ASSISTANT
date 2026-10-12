import { NextResponse } from "next/server";
import { isMissingRelation } from "@/lib/attempts";
import { SITE_NAME, SITE_URL } from "@/lib/config";
import { createAdminClient } from "@/lib/supabase/server";

// Weekly study nudge, run by Vercel Cron (vercel.json: Mondays 14:00 UTC).
// Vercel sends "Authorization: Bearer $CRON_SECRET" when CRON_SECRET is set in the project.
// Sends one short email per learner with an upcoming interview_date and nudges = true, through
// the Resend REST API. Without RESEND_API_KEY and NUDGE_FROM_EMAIL it does nothing.

export const maxDuration = 60;

const MAX_PER_RUN = 300;
const MIN_GAP_MS = 6 * 24 * 3600_000;

interface ProfileRow {
  user_id: string;
  interview_date: string;
  target_role: string | null;
  last_nudge_at: string | null;
  diagnostic: { plan?: { week: number; start: string; items?: { title: string; status: string }[] }[] } | null;
}

const ROLE: Record<string, string> = { engineer: "Applied AI Engineer", architect: "Applied AI Architect", fde: "Forward Deployed Engineer" };

function daysUntil(date: string, now: Date): number {
  const today = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate());
  return Math.round((Date.parse(`${date}T00:00:00Z`) - today) / 86_400_000);
}

function compose(p: ProfileRow, now: Date): { subject: string; text: string } {
  const days = daysUntil(p.interview_date, now);
  const role = p.target_role ? ROLE[p.target_role] : null;
  const weeks = p.diagnostic?.plan ?? [];
  const todayIso = now.toISOString().slice(0, 10);
  const week = [...weeks].reverse().find((w) => w.start <= todayIso);
  const focus = (week?.items ?? []).filter((i) => i.status !== "skip").slice(0, 3).map((i) => `- ${i.title}`);
  const subject = days <= 0 ? "Your interview is today. Good luck." : `${days} day${days === 1 ? "" : "s"} to your ${role ? `${role} ` : ""}interview`;
  const lines = [
    days <= 0 ? "Your interview is today. Rest, read your notes once, and trust the reps you've done." : `${days} day${days === 1 ? "" : "s"} to go.`,
    "",
    ...(focus.length ? ["This week's plan:", ...focus, ""] : []),
    days > 0 && days <= 14
      ? "With two weeks or less to go, run a full mock loop on fresh material and fix your weakest round."
      : "Keep to the plan: a little every day beats a weekend cram.",
    "",
    `Your plan: ${SITE_URL}/start`,
    `Your scorecard: ${SITE_URL}/learn/progress`,
    `Five-minute review: ${SITE_URL}/review`,
    "",
    `To stop these emails, turn off reminders at ${SITE_URL}/learn/progress#settings.`,
    `${SITE_NAME}`,
  ];
  return { subject, text: lines.join("\n") };
}

export async function GET(req: Request) {
  const secret = process.env.CRON_SECRET;
  if (!secret || req.headers.get("authorization") !== `Bearer ${secret}`) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }
  const apiKey = process.env.RESEND_API_KEY;
  const from = process.env.NUDGE_FROM_EMAIL;
  if (!apiKey || !from) return NextResponse.json({ ok: true, sent: 0, skipped: "RESEND_API_KEY or NUDGE_FROM_EMAIL not set" });

  let admin: ReturnType<typeof createAdminClient>;
  try {
    admin = createAdminClient();
  } catch {
    return NextResponse.json({ ok: true, sent: 0, skipped: "Supabase secret key not set" });
  }

  const now = new Date();
  const today = now.toISOString().slice(0, 10);
  const { data, error } = await admin
    .from("profiles")
    .select("user_id, interview_date, target_role, last_nudge_at, diagnostic")
    .eq("nudges", true)
    .gte("interview_date", today)
    .order("interview_date", { ascending: true })
    .limit(MAX_PER_RUN);
  if (error) {
    if (isMissingRelation(error)) return NextResponse.json({ ok: true, sent: 0, skipped: "profiles table missing" });
    console.error("nudges: profile query failed", error.message);
    return NextResponse.json({ error: "Query failed" }, { status: 500 });
  }

  let sent = 0;
  let failed = 0;
  for (const p of (data ?? []) as ProfileRow[]) {
    if (p.last_nudge_at && now.getTime() - Date.parse(p.last_nudge_at) < MIN_GAP_MS) continue;
    const { data: u } = await admin.auth.admin.getUserById(p.user_id);
    const email = u?.user?.email;
    if (!email) continue;
    const { subject, text } = compose(p, now);
    try {
      const res = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: { Authorization: `Bearer ${apiKey}`, "Content-Type": "application/json" },
        body: JSON.stringify({ from, to: [email], subject, text }),
      });
      if (!res.ok) {
        failed++;
        console.error("nudges: Resend returned", res.status);
        continue;
      }
      sent++;
      await admin.from("profiles").update({ last_nudge_at: now.toISOString() }).eq("user_id", p.user_id);
    } catch (err) {
      failed++;
      console.error("nudges: send failed", err);
    }
  }
  return NextResponse.json({ ok: true, sent, failed });
}
