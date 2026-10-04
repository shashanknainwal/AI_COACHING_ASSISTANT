import { NextResponse } from "next/server";
import { supabaseConfigured } from "@/lib/config";
import { safeNext } from "@/lib/safe-next";
import { createClient } from "@/lib/supabase/server";

// The magic link in the login email lands here with a one-time code.
export async function GET(req: Request) {
  const url = new URL(req.url);
  const code = url.searchParams.get("code");
  const next = safeNext(url.searchParams.get("next"));

  if (code && supabaseConfigured) {
    const supabase = await createClient();
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    if (!error) return NextResponse.redirect(new URL(next, url.origin));
  }
  return NextResponse.redirect(new URL(`/login?error=link&next=${encodeURIComponent(next)}`, url.origin));
}
