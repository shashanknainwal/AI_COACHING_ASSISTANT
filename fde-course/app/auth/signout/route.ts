import { NextResponse } from "next/server";
import { supabaseConfigured } from "@/lib/config";
import { createClient } from "@/lib/supabase/server";

export async function POST(req: Request) {
  if (supabaseConfigured) {
    const supabase = await createClient();
    await supabase.auth.signOut();
  }
  return NextResponse.redirect(new URL("/", req.url), 303);
}
