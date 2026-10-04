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
      <div className="mt-6 rounded-lg border border-accent/40 bg-accent/10 p-4 text-sm text-gray-200">
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
        className="w-full rounded-lg border border-line bg-panel px-3 py-2 text-gray-100 placeholder:text-gray-600"
      />
      <button
        type="submit"
        disabled={state === "sending"}
        className="w-full rounded-lg bg-accent px-4 py-2 font-semibold text-ink hover:opacity-90 disabled:opacity-50"
      >
        {state === "sending" ? "Sending…" : "Email me a login link"}
      </button>
      {state === "error" && <p className="text-sm text-red-300">{message}</p>}
    </form>
  );
}
