import { NextResponse } from "next/server";
import { getViewer } from "@/lib/access";
import { createClient } from "@/lib/supabase/server";

const LESSON_ID = /^[a-z0-9-]{1,100}\/[a-z0-9-]{1,100}$/;
const MAX_CODE = 100_000;
const MAX_ITEMS = 200;

interface IncomingItem {
  lessonId: string;
  completedAt?: string;
  code?: string;
}

/** GET → this learner's saved progress. */
export async function GET() {
  const viewer = await getViewer();
  if (!viewer.user) return NextResponse.json({ error: "Not signed in" }, { status: 401 });

  const supabase = await createClient();
  const { data, error } = await supabase.from("lesson_progress").select("lesson_id, completed_at, code");
  if (error) return NextResponse.json({ error: "Could not load progress" }, { status: 500 });
  return NextResponse.json({ items: data });
}

/** POST { items: [{ lessonId, completedAt?, code? }] } → upsert progress rows. */
export async function POST(req: Request) {
  const viewer = await getViewer();
  if (!viewer.user) return NextResponse.json({ error: "Not signed in" }, { status: 401 });

  let items: IncomingItem[];
  try {
    const body = await req.json();
    items = Array.isArray(body?.items) ? body.items : [];
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }
  if (items.length === 0 || items.length > MAX_ITEMS) {
    return NextResponse.json({ error: `Send 1 to ${MAX_ITEMS} items` }, { status: 400 });
  }

  const userId = viewer.user.id;
  const now = new Date().toISOString();
  const completions: { user_id: string; lesson_id: string; completed_at: string; updated_at: string }[] = [];
  const codes: { user_id: string; lesson_id: string; code: string; updated_at: string }[] = [];

  for (const it of items) {
    if (typeof it?.lessonId !== "string" || !LESSON_ID.test(it.lessonId)) {
      return NextResponse.json({ error: "Invalid lessonId" }, { status: 400 });
    }
    if (it.completedAt !== undefined) {
      const t = Date.parse(it.completedAt);
      if (Number.isNaN(t)) return NextResponse.json({ error: "Invalid completedAt" }, { status: 400 });
      completions.push({ user_id: userId, lesson_id: it.lessonId, completed_at: new Date(Math.min(t, Date.now())).toISOString(), updated_at: now });
    }
    if (it.code !== undefined) {
      if (typeof it.code !== "string" || it.code.length > MAX_CODE) {
        return NextResponse.json({ error: "Code too large" }, { status: 400 });
      }
      codes.push({ user_id: userId, lesson_id: it.lessonId, code: it.code, updated_at: now });
    }
  }

  // Two separate upserts so a code save never clears completed_at (and vice versa):
  // an upsert only overwrites the columns present in its payload.
  const supabase = await createClient();
  const results = await Promise.all([
    completions.length ? supabase.from("lesson_progress").upsert(completions, { onConflict: "user_id,lesson_id" }) : null,
    codes.length ? supabase.from("lesson_progress").upsert(codes, { onConflict: "user_id,lesson_id" }) : null,
  ]);
  const failed = results.find((r) => r?.error);
  if (failed?.error) {
    console.error("progress upsert failed", failed.error.message);
    return NextResponse.json({ error: "Could not save progress" }, { status: 500 });
  }
  return NextResponse.json({ ok: true });
}
