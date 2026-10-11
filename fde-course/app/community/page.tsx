import Link from "next/link";
import { getViewer, toClientViewer } from "@/lib/access";
import { freeLessonIds } from "@/lib/content";
import SiteCommunity from "@/components/SiteCommunity";
import SiteHeader from "@/components/SiteHeader";
import { getPeerScripts } from "@/components/SiteServerData";

export const metadata = { title: "Peer mocks" };
export const dynamic = "force-dynamic";

const STEPS: [string, string][] = [
  ["Pair up", "Find a partner preparing for a similar role. Book 90 minutes: two 30-minute sessions, two debriefs, a short break."],
  ["Pick a round", "Choose a role-play lesson below. The interviewer prints its script; the candidate doesn't read the score sheet first."],
  ["Run it closed book", "Cameras on, no notes beyond what a real loop allows. The interviewer keeps time and stays in character."],
  ["Score and debrief", "Score each rubric line, then debrief: the candidate first, then the two lowest lines with one moment each."],
  ["Swap", "Change roles on a different round, so neither of you has seen the scenario."],
];

const LOOP_NIGHT: [string, string][] = [
  ["0:00", "Check-in: each person names the round they're weakest at (from their scorecard)."],
  ["0:05", "Session 1: 30 minutes in pairs, on that weakest round."],
  ["0:35", "Debrief 1: 10 minutes with the score sheet."],
  ["0:45", "Session 2: swap roles, 30 minutes."],
  ["1:15", "Debrief 2, then the whole group shares one fix each and books next week."],
];

export default async function CommunityPage() {
  const viewer = await getViewer();
  const scripts = getPeerScripts(viewer, freeLessonIds());
  const community = process.env.NEXT_PUBLIC_COMMUNITY_URL;
  const booking = process.env.NEXT_PUBLIC_MOCK_BOOKING_URL;
  return (
    <div className="playbook-page min-h-screen">
      <div className="print:hidden">
        <SiteHeader viewer={toClientViewer(viewer)} current="/community" />
      </div>
      <main className="mx-auto max-w-5xl px-4 pb-20 pt-8 sm:px-6 sm:pt-10 print:p-0">
        <div className="print:hidden">
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-vermilion">Peer mocks</p>
          <h1 className="mt-2 font-serif text-4xl font-semibold leading-tight tracking-[-0.02em] text-graphite">Practise with a person, too</h1>
          <p className="mt-3 max-w-2xl text-graphite-2">
            The AI interviewers grade you on the rubric. A human partner adds what they can&apos;t: real interruptions, silence and nerves. Here&apos;s a kit
            to run a fair peer mock with the same rubrics.
          </p>

          {(community || booking) && (
            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              {community && (
                <div className="rounded-3xl bg-graphite p-6 text-paper">
                  <p className="font-serif text-xl">Join the community</p>
                  <p className="mt-1 text-sm text-paper-3">Find a mock partner, join a weekly loop night and swap notes with others preparing.</p>
                  <a href={community} target="_blank" rel="noopener noreferrer" className="mt-4 inline-block rounded-full bg-emerald-400 px-5 py-2 font-semibold text-graphite hover:bg-emerald-300">
                    Join →
                  </a>
                </div>
              )}
              {booking && (
                <div className="rounded-3xl border border-rule bg-white/80 p-6">
                  <p className="font-serif text-xl text-graphite">A 1:1 mock with the instructor</p>
                  <p className="mt-1 text-sm text-graphite-2">An optional paid add-on: one live mock round with written feedback against the course rubric.</p>
                  <a href={booking} target="_blank" rel="noopener noreferrer" className="mt-4 inline-block rounded-full bg-graphite px-5 py-2 font-semibold text-paper hover:bg-black">
                    Book a mock →
                  </a>
                </div>
              )}
            </div>
          )}

          <div className="mt-10 grid gap-6 lg:grid-cols-2">
            <section aria-labelledby="how-title" className="rounded-3xl border border-rule bg-white/70 p-5 sm:p-6">
              <h2 id="how-title" className="font-serif text-2xl font-semibold text-graphite">
                How to run a peer mock
              </h2>
              <ol className="mt-4 space-y-3">
                {STEPS.map(([t, d], i) => (
                  <li key={t} className="flex gap-3 text-sm">
                    <span className="font-mono font-semibold text-vermilion">0{i + 1}</span>
                    <span>
                      <span className="font-semibold text-graphite">{t}.</span> <span className="text-graphite-2">{d}</span>
                    </span>
                  </li>
                ))}
              </ol>
            </section>
            <section aria-labelledby="night-title" className="rounded-3xl border border-rule bg-white/70 p-5 sm:p-6">
              <h2 id="night-title" className="font-serif text-2xl font-semibold text-graphite">
                Weekly loop night
              </h2>
              <p className="mt-1 text-sm text-graphite-3">A 90-minute format for a study group of four to eight, same time every week.</p>
              <ol className="mt-4 space-y-2 text-sm">
                {LOOP_NIGHT.map(([t, d]) => (
                  <li key={t} className="flex gap-3">
                    <span className="w-10 shrink-0 font-mono text-graphite-3">{t}</span>
                    <span className="text-graphite-2">{d}</span>
                  </li>
                ))}
              </ol>
              <p className="mt-4 text-sm text-graphite-2">
                Bring your{" "}
                <Link href="/learn/progress" className="font-semibold text-forest hover:underline">
                  scorecard
                </Link>{" "}
                so the group works on everyone&apos;s weakest round, not their favourite one.
              </p>
            </section>
          </div>

          <h2 className="mt-12 font-serif text-2xl font-semibold text-graphite">Interviewer scripts</h2>
          <p className="mt-1 max-w-2xl text-sm text-graphite-2">
            Built from each lesson&apos;s own text and rubric. The AI interviewer&apos;s private brief stays private, so the human version is a little
            plainer: play it straight and use the score sheet.
            {!viewer.hasPurchased && " Free rounds are listed now; the rest appear with full access."}
          </p>
        </div>
        <div className="mt-5">
          <SiteCommunity scripts={scripts} />
        </div>
      </main>
    </div>
  );
}
