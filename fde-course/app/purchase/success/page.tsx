import Link from "next/link";
import { redirect } from "next/navigation";
import { getViewer } from "@/lib/access";
import { getStripe, recordPurchase } from "@/lib/purchases";

export const metadata = { title: "Thanks for your purchase" };

// Stripe redirects here after payment. We confirm the session directly with Stripe
// so access is granted immediately, even if the webhook hasn't arrived yet.
export default async function PurchaseSuccess({ searchParams }: { searchParams: Promise<{ session_id?: string }> }) {
  const { session_id } = await searchParams;
  const viewer = await getViewer();
  if (!viewer.user) redirect("/login?next=/learn");

  let ok = viewer.hasPurchased;
  if (!ok && session_id && viewer.mode === "live") {
    try {
      const session = await getStripe().checkout.sessions.retrieve(session_id);
      if (session.client_reference_id === viewer.user.id) ok = await recordPurchase(session);
    } catch (err) {
      console.error("Purchase confirmation failed", err);
    }
  }

  return (
    <main className="playbook-page flex min-h-screen items-center justify-center px-6 py-16 text-center">
      <div className="w-full max-w-lg rounded-3xl border border-rule bg-white/80 p-10 shadow-[0_30px_60px_-40px_rgba(29,27,22,0.6)]">
      {ok ? (
        <>
          <div className="text-5xl">🎉</div>
          <h1 className="mt-4 font-serif text-4xl font-semibold text-graphite">You&apos;re in.</h1>
          <p className="mt-3 text-graphite-2">All modules are unlocked for {viewer.user.email}. A receipt is on its way to your inbox.</p>
          <Link href="/learn" className="mt-8 inline-block rounded-full bg-graphite px-6 py-3 font-semibold text-paper hover:bg-black">
            Go to the course →
          </Link>
        </>
      ) : (
        <>
          <h1 className="font-serif text-3xl font-semibold text-graphite">Confirming your payment…</h1>
          <p className="mt-3 text-graphite-2">
            This usually takes a few seconds. Refresh this page in a moment. If access still isn&apos;t unlocked after a few minutes,
            reply to your Stripe receipt email and we&apos;ll sort it out.
          </p>
          <Link href="/learn" className="mt-8 inline-block font-semibold text-forest hover:underline">
            Back to the course
          </Link>
        </>
      )}
      </div>
    </main>
  );
}
