/** Only allow redirects to paths on this site (blocks `//evil.com` and absolute URLs). */
export function safeNext(next: string | null | undefined, fallback = "/learn"): string {
  if (!next || !next.startsWith("/") || next.startsWith("//") || next.startsWith("/\\")) return fallback;
  return next;
}
