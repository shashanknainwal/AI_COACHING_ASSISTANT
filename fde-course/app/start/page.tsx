import { getViewer, toClientViewer } from "@/lib/access";
import { getCourse } from "@/lib/content";
import SiteHeader from "@/components/SiteHeader";
import SiteOnboarding from "@/components/SiteOnboarding";
import { getPlanModules } from "@/components/SiteServerData";
import { ROLE_TRACKS, type RoleTrack } from "@/components/SiteTypes";

export const metadata = { title: "Build my plan" };
export const dynamic = "force-dynamic";

export default async function StartPage() {
  const viewer = toClientViewer(await getViewer());
  const visible = new Set(getCourse().tracks.map((t) => t.slug));
  const roles = ROLE_TRACKS.filter((r) => visible.has(r)) as RoleTrack[];
  return (
    <div className="playbook-page min-h-screen">
      <SiteHeader viewer={viewer} current="/start" />
      <main className="mx-auto max-w-3xl px-4 pb-20 pt-8 sm:px-6 sm:pt-10">
        <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-vermilion">Your plan</p>
        <h1 className="mt-2 font-serif text-4xl font-semibold leading-tight tracking-[-0.02em] text-graphite">Plan your prep, week by week</h1>
        <p className="mt-3 text-graphite-2">
          Tell us your role, your interview date and how much time you have. A ten-question self-check and a quick self-rating mark what to skim, and
          the plan ends with a full mock loop the week before your interview.
        </p>
        <div className="mt-8">
          <SiteOnboarding modules={getPlanModules()} roles={roles} />
        </div>
      </main>
    </div>
  );
}
