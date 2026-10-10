import "server-only";
import { createHash, createHmac, timingSafeEqual } from "node:crypto";

// Persona lines in a role-play are signed by the server, so a learner can't rewrite what
// the interviewer said (or invent an interviewer line) before asking for a grade.
// sig = HMAC-SHA256(key, `${lessonId}|${index}|${text}`), hex.

function signingKey(): Buffer {
  const explicit = process.env.COACH_SIGNING_SECRET;
  if (explicit) return Buffer.from(explicit, "utf8");
  // No dedicated secret: derive one from a server-only secret that is always set when AI is on.
  const base = process.env.SUPABASE_SECRET_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.ANTHROPIC_API_KEY || "fde-playbook-dev-only";
  return createHash("sha256").update(`coach-signing-v1:${base}`).digest();
}

export function signPersonaLine(lessonId: string, index: number, text: string): string {
  return createHmac("sha256", signingKey()).update(`${lessonId}|${index}|${text}`).digest("hex");
}

export function verifyPersonaLine(lessonId: string, index: number, text: string, sig: unknown): boolean {
  if (typeof sig !== "string" || !/^[0-9a-f]{64}$/.test(sig)) return false;
  const expected = Buffer.from(signPersonaLine(lessonId, index, text), "hex");
  const given = Buffer.from(sig, "hex");
  return expected.length === given.length && timingSafeEqual(expected, given);
}
