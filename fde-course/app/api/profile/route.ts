import { NextResponse } from "next/server";
import { getViewer } from "@/lib/access";
import { isMissingRelation } from "@/lib/attempts";
import { createClient } from "@/lib/supabase/server";
import { ROLE_TRACKS, type Profile, type RoleTrack } from "@/components/SiteTypes";

// GET  /api/profile            → { profile: Profile | null }
// POST /api/profile (partial)  → { profile }
// Without Supabase, signed out, or before supabase/migrations/0004_profiles.sql is run:
// { disabled: true } with status 200, and the browser keeps the profile in localStorage.

const HANDLE = /^[a-z0-9-]{3,30}$/;
const RESERVED = new Set(["admin", "api", "learn", "login", "start", "review", "community", "certificate", "support", "help", "fde-playbook", "fdeplaybook"]);
const DATE = /^\d{4}-\d{2}-\d{2}$/;
const MAX_DIAGNOSTIC = 30_000;

interface Row {
  handle: string | null;
  public_profile: boolean;
  target_role: string | null;
  interview_date: string | null;
  hours_per_week: number | null;
  background: string | null;
  diagnostic: unknown;
  loop_mode: unknown;
  nudges: boolean;
  capstone_url: string | null;
}

const COLUMNS = "handle, public_profile, target_role, interview_date, hours_per_week, background, diagnostic, loop_mode, nudges, capstone_url";

function toProfile(r: Row): Profile {
  return {
    handle: r.handle,
    publicProfile: r.public_profile,
    targetRole: (r.target_role as RoleTrack | null) ?? null,
    interviewDate: r.interview_date,
    hoursPerWeek: r.hours_per_week,
    background: r.background,
    diagnostic: (r.diagnostic as Profile["diagnostic"]) ?? null,
    loopMode: (r.loop_mode as Profile["loopMode"]) ?? null,
    nudges: r.nudges,
    capstoneUrl: r.capstone_url,
  };
}

async function signedIn() {
  const viewer = await getViewer();
  if (viewer.mode !== "live" || !viewer.user) return null;
  return viewer.user;
}

export async function GET() {
  const user = await signedIn();
  if (!user) return NextResponse.json({ disabled: true });
  const supabase = await createClient();
  const { data, error } = await supabase.from("profiles").select(COLUMNS).eq("user_id", user.id).maybeSingle();
  if (error) {
    if (isMissingRelation(error)) return NextResponse.json({ disabled: true });
    console.error("profile GET failed", error.message);
    return NextResponse.json({ error: "Could not load your profile" }, { status: 500 });
  }
  return NextResponse.json({ profile: data ? toProfile(data as Row) : null });
}

type Patch = Partial<Record<keyof Row, unknown>>;

/** Validates a partial Profile into column values. Returns an error message for bad input. */
function validate(body: Record<string, unknown>): Patch | string {
  const patch: Patch = {};
  if ("handle" in body) {
    const h = body.handle == null || body.handle === "" ? null : String(body.handle).trim().toLowerCase();
    if (h !== null && (!HANDLE.test(h) || RESERVED.has(h))) return "Handles are 3 to 30 characters: lowercase letters, numbers and hyphens.";
    patch.handle = h;
  }
  if ("publicProfile" in body) patch.public_profile = body.publicProfile === true;
  if ("targetRole" in body) {
    const r = body.targetRole ?? null;
    if (r !== null && !ROLE_TRACKS.includes(r as RoleTrack)) return "Unknown role";
    patch.target_role = r;
  }
  if ("interviewDate" in body) {
    const d = body.interviewDate == null || body.interviewDate === "" ? null : String(body.interviewDate);
    if (d !== null && (!DATE.test(d) || Number.isNaN(Date.parse(d)))) return "Invalid interview date";
    patch.interview_date = d;
  }
  if ("hoursPerWeek" in body) {
    const n = body.hoursPerWeek == null ? null : Number(body.hoursPerWeek);
    if (n !== null && (!Number.isInteger(n) || n < 1 || n > 80)) return "Hours per week must be 1 to 80";
    patch.hours_per_week = n;
  }
  if ("background" in body) {
    const b = body.background == null ? null : String(body.background).slice(0, 500);
    patch.background = b;
  }
  if ("diagnostic" in body) {
    const d = body.diagnostic ?? null;
    if (d !== null && (typeof d !== "object" || Array.isArray(d) || JSON.stringify(d).length > MAX_DIAGNOSTIC)) return "Invalid diagnostic";
    patch.diagnostic = d;
  }
  if ("loopMode" in body) {
    const lm = body.loopMode as { track?: unknown } | null | undefined;
    if (lm == null) patch.loop_mode = null;
    else if (typeof lm === "object" && ROLE_TRACKS.includes(lm.track as RoleTrack)) patch.loop_mode = { track: lm.track, startedAt: new Date().toISOString() };
    else return "Invalid loop mode";
  }
  if ("nudges" in body) patch.nudges = body.nudges !== false;
  if ("capstoneUrl" in body) {
    const u = body.capstoneUrl == null || body.capstoneUrl === "" ? null : String(body.capstoneUrl).trim();
    if (u !== null) {
      let ok = false;
      try {
        ok = new URL(u).protocol === "https:" && u.length <= 300;
      } catch {
        ok = false;
      }
      if (!ok) return "The capstone link must be an https:// URL (300 characters at most).";
    }
    patch.capstone_url = u;
  }
  return patch;
}

export async function POST(req: Request) {
  let body: Record<string, unknown>;
  try {
    const parsed = await req.json();
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) throw new Error("not an object");
    body = parsed as Record<string, unknown>;
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }
  const user = await signedIn();
  if (!user) return NextResponse.json({ disabled: true });

  const patch = validate(body);
  if (typeof patch === "string") return NextResponse.json({ error: patch }, { status: 400 });

  const supabase = await createClient();
  const { data, error } = await supabase
    .from("profiles")
    .upsert({ user_id: user.id, ...patch, updated_at: new Date().toISOString() }, { onConflict: "user_id" })
    .select(COLUMNS)
    .single();
  if (error) {
    if (isMissingRelation(error)) return NextResponse.json({ disabled: true });
    if (error.code === "23505") return NextResponse.json({ error: "That handle is taken. Try another." }, { status: 409 });
    console.error("profile POST failed", error.message);
    return NextResponse.json({ error: "Could not save your profile" }, { status: 500 });
  }
  return NextResponse.json({ profile: toProfile(data as Row) });
}
