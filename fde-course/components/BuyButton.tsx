import type { ClientViewer } from "@/lib/access";

/** Plain <a> (not next/link) so prefetching never creates Stripe Checkout sessions. */
export default function BuyButton({ viewer, price, className = "" }: { viewer: ClientViewer; price: number; className?: string }) {
  const base = `inline-block rounded-lg px-6 py-3 font-semibold ${className}`;
  if (viewer.hasPurchased) {
    return (
      <a href="/learn" className={`${base} bg-accent text-ink hover:opacity-90`}>
        {viewer.mode === "dev" ? "All modules unlocked (dev preview)" : "You own the course · Go to it →"}
      </a>
    );
  }
  if (!viewer.canBuy) {
    return <span className={`${base} cursor-not-allowed border border-line text-gray-500`}>Full access coming soon</span>;
  }
  return (
    <a href="/buy" className={`${base} bg-accent text-ink hover:opacity-90`}>
      {viewer.signedIn ? `Buy full access · $${price}` : `Get full access · $${price}`}
    </a>
  );
}
