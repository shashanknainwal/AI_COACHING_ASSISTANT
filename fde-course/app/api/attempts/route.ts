import { NextResponse } from "next/server";
import { canAccessLesson, getViewer } from "@/lib/access";
import { listAttempts, recordDrillAttempt } from "@/lib/attempts";
import type { DrillAttemptInput } from "@/lib/coach-types";
import { getLesson } from "@/lib/content";

// GET  /api/attempts?lesson=<module>/<lesson>  → { grades, drills } for one lesson, newest first
// GET  /api/attempts                           → { grades, drills } for every lesson (dashboard)
// POST /api/attempts { kind: "drill", ... }     → { ok: true }
// Without Supabase, or before supabase/migrations/0003_attempts.sql is run: { disabled: true }.

const LESSON_ID = /^[a-z0-9-]{1,100}\/[a-z0-9-]{1,100}$/;

export async function GET(req: Request) {
  const viewer = await getViewer();
  if (viewer.mode !== "live") return NextResponse.json({ disabled: true });
  if (!viewer.user) return NextResponse.json({ error: "Not signed in" }, { status: 401 });
  const lesson = new URL(req.url).searchParams.get("lesson") ?? undefined;
  if (lesson !== undefined && !LESSON_ID.test(lesson)) return NextResponse.json({ error: "Invalid lesson" }, { status: 400 });
  const attempts = await listAttempts(viewer, lesson);
  return NextResponse.json(attempts ?? { disabled: true });
}

export async function POST(req: Request) {
  let body: DrillAttemptInput;
  try {
    body = (await req.json()) as DrillAttemptInput;
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }
  if (body?.kind !== "drill") return NextResponse.json({ error: "Unknown attempt kind" }, { status: 400 });
  if (typeof body.lesson !== "string" || !LESSON_ID.test(body.lesson)) return NextResponse.json({ error: "Invalid lesson" }, { status: 400 });

  const viewer = await getViewer();
  if (viewer.mode !== "live") return NextResponse.json({ disabled: true });
  if (!viewer.user) return NextResponse.json({ error: "Not signed in" }, { status: 401 });

  const [moduleSlug, lessonSlug] = body.lesson.split("/");
  const lesson = getLesson(moduleSlug, lessonSlug);
  if (!lesson || lesson.type !== "drill") return NextResponse.json({ error: "Unknown drill" }, { status: 404 });
  if (!canAccessLesson(viewer, moduleSlug, lessonSlug)) return NextResponse.json({ error: "This lesson is part of the full course." }, { status: 403 });

  const saved = await recordDrillAttempt(viewer, body, lesson.levels.length);
  if (saved === "disabled") return NextResponse.json({ disabled: true });
  if (saved !== "ok") return NextResponse.json({ error: saved.error }, { status: 400 });
  return NextResponse.json({ ok: true });
}
