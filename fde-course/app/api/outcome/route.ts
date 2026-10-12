import { NextResponse } from "next/server";
import { getViewer } from "@/lib/access";
import { isMissingRelation } from "@/lib/attempts";
import { createClient } from "@/lib/supabase/server";

// POST /api/outcome { track, result, company?, note?, consentQuote? } → { ok: true }
// "Did you get the offer?" answers. Quotes are used only when consentQuote is true.
// Without Supabase, signed out, or before 0004_profiles.sql: { disabled: true } (the page keeps a local copy).

const TRACKS = new Set(["core", "engineer", "architect", "fde"]);
const RESULTS = new Set(["offer", "no-offer", "pending", "withdrew"]);

export async function POST(req: Request) {
  let body: Record<string, unknown>;
  try {
    body = (await req.json()) as Record<string, unknown>;
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }
  const result = String(body?.result ?? "");
  if (!RESULTS.has(result)) return NextResponse.json({ error: "Pick a result" }, { status: 400 });
  const track = body.track == null || body.track === "" ? null : String(body.track);
  if (track !== null && !TRACKS.has(track)) return NextResponse.json({ error: "Unknown track" }, { status: 400 });
  const company = body.company ? String(body.company).trim().slice(0, 120) || null : null;
  const note = body.note ? String(body.note).trim().slice(0, 2000) || null : null;

  const viewer = await getViewer();
  if (viewer.mode !== "live" || !viewer.user) return NextResponse.json({ disabled: true });

  const supabase = await createClient();
  const { error } = await supabase.from("outcomes").insert({ user_id: viewer.user.id, track, result, company, note, consent_quote: body.consentQuote === true });
  if (error) {
    if (isMissingRelation(error)) return NextResponse.json({ disabled: true });
    console.error("outcome insert failed", error.message);
    return NextResponse.json({ error: "Could not save your answer" }, { status: 500 });
  }
  return NextResponse.json({ ok: true });
}
