import Link from "next/link";
import { notFound } from "next/navigation";
import { getPublicPortfolio, type VerifiedSummary } from "@/lib/attempts";
import { SITE_NAME } from "@/lib/config";
import { createAdminClient } from "@/lib/supabase/server";
import { Mark } from "@/components/Playbook";
import { PASS_MARK, mmss, scoreLoop, type DrillRec, type GradeRec } from "@/components/DashboardScore";
import { getLoopConfigs } from "@/components/SiteServerData";
import { ROLE_LABEL, type RoleTrack } from "@/components/SiteTypes";

// Public portfolio and verified certificate. Shown only when the learner set profiles.public_profile.
// Everything comes from server-recorded attempts (lib/attempts.ts getPublicPortfolio).

export const dynamic = "force-dynamic";

const HANDLE = /^[a-z0-9-]{3,30}$/;

export async function generateMetadata({ params }: { params: Promise<{ handle: string }> }) {
  const { handle } = await params;
  return { title: HANDLE.test(handle) ? `${handle} · verified practice record` : "Portfolio" };
}

async function capstoneUrl(handle: string): Promise<string | null> {
  try {
    const { data } = await createAdminClient().from("profiles").select("capstone_url").eq("handle", handle).eq("public_profile", true).maybeSingle();
    const url = (data?.capstone_url as string | null) ?? null;
    return url && url.startsWith("https://") ? url : null;
  } catch {
    return null;
  }
}

const day = (iso: string) => new Date(iso).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });

function loopsFor(summary: VerifiedSummary) {
  // Loop scores are the first loop-mode attempt per round (graded by the server). Drill rounds use
  // the best recorded clear, since drill timings are measured in the browser.
  const grades = new Map<string, GradeRec[]>();
  for (const s of summary.loopScores) grades.set(s.lessonId, [{ lessonId: s.lessonId, percent: s.percent, passed: s.passed, createdAt: s.at, loopMode: true, criteria: [] }]);
  const drills = new Map<string, DrillRec[]>();
  for (const d of summary.drills) {
    drills.set(d.lessonId, [
      { lessonId: d.lessonId, startedAt: Date.parse(d.lastAt), finishedAt: null, timeLimitMin: 0, levelMs: [], cleared: d.bestCleared, clearedInTime: d.bestClearedInTime, loopMode: true },
    ]);
  }
  return getLoopConfigs()
    .map((cfg) => ({ cfg, result: scoreLoop(cfg, grades, drills) }))
    .filter(({ cfg }) => summary.loopScores.some((s) => cfg.rounds.some((r) => r.lessons.some((l) => l.id === s.lessonId))));
}

export default async function PortfolioPage({ params }: { params: Promise<{ handle: string }> }) {
  const { handle } = await params;
  if (!HANDLE.test(handle)) notFound();
  const portfolio = await getPublicPortfolio(handle);
  if (!portfolio) notFound();
  const { summary } = portfolio;
  const capstone = await capstoneUrl(portfolio.handle);
  const loops = loopsFor(summary);
  const role = portfolio.targetRole && portfolio.targetRole in ROLE_LABEL ? ROLE_LABEL[portfolio.targetRole as RoleTrack] : null;
  const rounds = [...summary.passedRounds].sort((a, b) => a.firstPassedAt.localeCompare(b.firstPassedAt));
  const drillClears = summary.drills.filter((d) => d.bestCleared > 0);
  const verifiedDone = summary.completions.filter((c) => c.verified).length;
  const selfDone = summary.completions.length - verifiedDone;
  const readyLoops = loops.filter((l) => l.result.verdict === "ready");

  return (
    <div className="playbook-page min-h-screen">
      <header className="border-b border-rule print:hidden">
        <div className="mx-auto flex h-14 max-w-4xl items-center gap-2 px-4 sm:px-6">
          <Link href="/" className="flex items-center gap-2 font-serif text-base font-semibold text-graphite">
            <Mark />
            {SITE_NAME}
          </Link>
        </div>
      </header>
      <main className="mx-auto max-w-4xl px-4 pb-20 pt-10 sm:px-6">
        <section aria-labelledby="cert-title" className="relative overflow-hidden rounded-[2rem] border-2 border-graphite bg-white p-6 text-center sm:p-10">
          <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-vermilion">Verified practice record</p>
          <h1 id="cert-title" className="mt-3 break-words font-serif text-4xl font-semibold text-graphite sm:text-5xl">
            {portfolio.handle}
          </h1>
          {role && <p className="mt-2 text-graphite-2">Preparing for {role} roles</p>}
          <dl className="mx-auto mt-8 grid max-w-xl grid-cols-3 gap-3">
            {[
              [String(rounds.length), "AI-graded rounds passed"],
              [String(summary.loopScores.length), "loop rounds scored"],
              [String(drillClears.length), "timed drills cleared"],
            ].map(([n, l]) => (
              <div key={l} className="rounded-2xl border border-rule bg-paper/60 px-3 py-3">
                <dt className="font-serif text-3xl font-semibold text-graphite">{n}</dt>
                <dd className="text-xs text-graphite-3">{l}</dd>
              </div>
            ))}
          </dl>
          {readyLoops.length > 0 && (
            <p className="mt-6 font-serif text-xl text-forest">
              Passed every round of the {readyLoops.map((l) => ROLE_LABEL[l.cfg.track]).join(" and ")} mock loop
            </p>
          )}
          <p className="mx-auto mt-6 max-w-xl text-xs leading-relaxed text-graphite-3">
            Written answers and live sessions were graded by Claude against the course rubrics, and recorded by {SITE_NAME}&apos;s server. Coding exercises run in
            the learner&apos;s browser and are self-reported. This is a record of practice, not an employment credential.
          </p>
        </section>

        {capstone && (
          <section className="mt-8 rounded-3xl border border-rule bg-white/70 p-5 sm:p-6">
            <h2 className="font-serif text-2xl font-semibold text-graphite">Capstone project</h2>
            <p className="mt-1 text-sm text-graphite-2">Built against the real API with the learner&apos;s own key. Linked by the learner.</p>
            <a href={capstone} rel="nofollow ugc noopener noreferrer" target="_blank" className="mt-3 inline-block break-all font-semibold text-forest hover:underline">
              {capstone}
            </a>
          </section>
        )}

        {loops.length > 0 && (
          <section className="mt-8 rounded-3xl border border-rule bg-white/70 p-5 sm:p-6">
            <h2 className="font-serif text-2xl font-semibold text-graphite">Mock loop scores</h2>
            <p className="mt-1 text-xs text-graphite-3">
              Graded rounds show the first attempt taken in loop mode (closed book). Coding rounds show the best recorded clear: 25 points per level in time, 10
              after.
            </p>
            {loops.map(({ cfg, result }) => (
              <div key={cfg.track} className="mt-5">
                <h3 className="font-semibold text-graphite">{ROLE_LABEL[cfg.track]}</h3>
                <ul className="mt-2 divide-y divide-rule text-sm">
                  {result.rounds.map((r) => (
                    <li key={r.cfg.key} className="flex items-center gap-3 py-2">
                      <span className="min-w-0 flex-1 text-graphite-2">{r.cfg.label}</span>
                      <span className="font-mono tabular-nums text-graphite">{r.score ?? "–"}</span>
                      <span
                        className={`w-14 shrink-0 rounded-full px-2 py-0.5 text-center text-[11px] font-semibold ${
                          r.score === null ? "border border-rule text-graphite-3" : r.score >= PASS_MARK ? "bg-forest text-white" : "bg-paper-3 text-graphite-2"
                        }`}
                      >
                        {r.score === null ? "–" : r.score >= PASS_MARK ? "Pass" : "Below"}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </section>
        )}

        <section className="mt-8 rounded-3xl border border-rule bg-white/70 p-5 sm:p-6">
          <h2 className="font-serif text-2xl font-semibold text-graphite">AI-graded rounds passed</h2>
          {rounds.length ? (
            <ul className="mt-3 divide-y divide-rule text-sm">
              {rounds.map((r) => (
                <li key={r.lessonId} className="flex flex-wrap items-baseline gap-x-3 py-2">
                  <span className="min-w-0 flex-1 text-graphite">{r.title}</span>
                  <span className="font-mono tabular-nums text-graphite-2">best {r.bestPercent}%</span>
                  <span className="text-xs text-graphite-3">
                    first passed {day(r.firstPassedAt)} · {r.attempts} attempt{r.attempts === 1 ? "" : "s"}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-2 text-sm text-graphite-2">No graded rounds passed yet.</p>
          )}
        </section>

        {drillClears.length > 0 && (
          <section className="mt-8 rounded-3xl border border-rule bg-white/70 p-5 sm:p-6">
            <h2 className="font-serif text-2xl font-semibold text-graphite">Timed drills</h2>
            <p className="mt-1 text-xs text-graphite-3">Recorded by the server; the clock runs in the learner&apos;s browser.</p>
            <ul className="mt-3 divide-y divide-rule text-sm">
              {drillClears.map((d) => (
                <li key={d.lessonId} className="flex flex-wrap items-baseline gap-x-3 py-2">
                  <span className="min-w-0 flex-1 text-graphite">{d.title}</span>
                  <span className="text-graphite-2">
                    {d.bestCleared}/{d.levels} levels · {d.bestClearedInTime} in time
                  </span>
                  {d.fastestFullClearMs !== null && <span className="text-xs text-graphite-3">fastest full clear {mmss(d.fastestFullClearMs)}</span>}
                </li>
              ))}
            </ul>
          </section>
        )}

        <p className="mt-8 text-sm text-graphite-3">
          {summary.completions.length} lessons completed: {verifiedDone} backed by a passing AI grade, {selfDone} self-reported (readings, quizzes and coding
          exercises, which run in the learner&apos;s browser).
        </p>
      </main>
    </div>
  );
}
