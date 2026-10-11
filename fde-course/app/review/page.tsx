import prices from "@/content/prices.json";
import { getViewer, toClientViewer } from "@/lib/access";
import SiteHeader from "@/components/SiteHeader";
import SiteReview from "@/components/SiteReview";
import { getNumberCards, getQuizCards } from "@/components/SiteServerData";

export const metadata = { title: "Daily review" };
// Quiz cards depend on what the viewer has bought.
export const dynamic = "force-dynamic";

export default async function ReviewPage() {
  const viewer = await getViewer();
  const cards = [...getNumberCards(), ...getQuizCards(viewer)];
  return (
    <div className="playbook-page min-h-screen">
      <SiteHeader viewer={toClientViewer(viewer)} current="/review" />
      <main className="mx-auto max-w-3xl px-4 pb-24 pt-8 sm:px-6 sm:pt-10">
        <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-vermilion">Daily review</p>
        <h1 className="mt-2 font-serif text-4xl font-semibold leading-tight tracking-[-0.02em] text-graphite">Five minutes a day</h1>
        <p className="mt-3 text-graphite-2">
          The numbers interviewers expect you to know cold (prices, cache rules, effort defaults) plus every quiz question in the course, spaced so you see
          each one just before you&apos;d forget it.
        </p>
        <div className="mt-8">
          <SiteReview cards={cards} lockedNote={!viewer.hasPurchased} />
        </div>
        <p className="mt-10 text-xs text-graphite-3">Prices checked {prices.checked}. Always confirm current prices on the provider&apos;s pricing page.</p>
      </main>
    </div>
  );
}
