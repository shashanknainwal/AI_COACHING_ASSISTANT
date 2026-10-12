import { NextResponse } from "next/server";
import { getViewer } from "@/lib/access";
import { passingLessonIds } from "@/lib/attempts";
import { getCourse } from "@/lib/content";
import { createClient } from "@/lib/supabase/server";

// Completion of a written or role-play lesson is accepted only when the server has recorded a
// passing grade for it (grade_attempts, migration 0003). Until that table exists, completions
// are accepted as before. Code lessons (exercises, drills) stay self-reported: their tests run
// in the browser. lib/attempts.ts getVerifiedSummary() marks which completions are verified.

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

  // Drop written/role-play completions that have no passing grade on record.
  const rejected: string[] = [];
  if (completions.length) {
    const types = new Map<string, string>(getCourse().modules.flatMap((m) => m.lessons.map((l) => [`${m.slug}/${l.slug}`, l.type] as const)));
    const graded = completions.filter((c) => types.get(c.lesson_id) === "written" || types.get(c.lesson_id) === "roleplay").map((c) => c.lesson_id);
    const passed = graded.length ? await passingLessonIds(userId, graded) : null;
    if (passed) {
      for (let i = completions.length - 1; i >= 0; i--) {
        const id = completions[i].lesson_id;
        if (graded.includes(id) && !passed.has(id)) {
          rejected.push(id);
          completions.splice(i, 1);
        }
      }
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
  return NextResponse.json(rejected.length ? { ok: true, rejected } : { ok: true });
}
