"use client";

import { useState } from "react";
import { createClient } from "@/lib/supabase/client";

export default function LoginForm({ next }: { next: string }) {
  const [email, setEmail] = useState("");
  const [state, setState] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const [message, setMessage] = useState("");

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setState("sending");
    const { error } = await createClient().auth.signInWithOtp({
      email: email.trim(),
      options: { emailRedirectTo: `${window.location.origin}/auth/callback?next=${encodeURIComponent(next)}` },
    });
    if (error) {
      setState("error");
      setMessage(error.message);
    } else {
      setState("sent");
    }
  };

  if (state === "sent") {
    return (
      <div className="mt-6 rounded-xl border border-forest/30 bg-forest/5 p-4 text-sm text-graphite-2">
        Check <strong>{email}</strong> for a login link. You can close this tab.
      </div>
    );
  }

  return (
    <form onSubmit={submit} className="mt-6 space-y-3">
      <input
        type="email"
        required
        autoComplete="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="you@company.com"
        className="w-full rounded-xl border border-rule bg-paper/70 px-3.5 py-2.5 text-graphite placeholder:text-graphite-3 focus:border-forest focus:outline-none"
      />
      <button
        type="submit"
        disabled={state === "sending"}
        className="w-full rounded-full bg-graphite px-4 py-2.5 font-semibold text-paper hover:bg-black disabled:opacity-50"
      >
        {state === "sending" ? "Sending…" : "Email me a login link"}
      </button>
      {state === "error" && <p className="text-sm text-vermilion">{message}</p>}
    </form>
  );
}
