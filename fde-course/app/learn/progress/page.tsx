import { getViewer, toClientViewer } from "@/lib/access";
import DashboardView from "@/components/DashboardView";
import SiteHeader from "@/components/SiteHeader";
import { getDrills, getGradedLessons, getLoopConfigs } from "@/components/SiteServerData";

export const metadata = { title: "Your progress" };
export const dynamic = "force-dynamic";

export default async function ProgressPage({ searchParams }: { searchParams: Promise<{ track?: string }> }) {
  const { track } = await searchParams;
  const viewer = await getViewer();
  const clientViewer = toClientViewer(viewer);
  return (
    <div className="playbook-page min-h-screen">
      <SiteHeader viewer={clientViewer} current="/learn/progress" />
      <main className="mx-auto max-w-6xl px-4 pb-20 pt-8 sm:px-6 sm:pt-10">
        <DashboardView loops={getLoopConfigs()} graded={getGradedLessons()} drills={getDrills()} signedIn={clientViewer.signedIn} initialTrack={track} />
      </main>
    </div>
  );
}
