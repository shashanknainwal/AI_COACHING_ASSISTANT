import { NextResponse } from "next/server";
import { getViewer } from "@/lib/access";
import { priceUsd, SITE_NAME, tracksEnabled } from "@/lib/config";
import { getStripe } from "@/lib/purchases";

// GET /buy → sends the learner to Stripe Checkout (or to log in first).
export async function GET(req: Request) {
  const origin = new URL(req.url).origin;
  const viewer = await getViewer();

  if (viewer.mode !== "live" || !viewer.canBuy) {
    return NextResponse.redirect(new URL("/learn?checkout=unavailable", origin), 303);
  }
  if (!viewer.user) {
    return NextResponse.redirect(new URL("/login?next=/buy", origin), 303);
  }
  if (viewer.hasPurchased) {
    return NextResponse.redirect(new URL("/learn", origin), 303);
  }

  // A Stripe Price must match priceUsd(); without one, checkout charges priceUsd() inline.
  const priceId = process.env.STRIPE_PRICE_ID;
  const allTracks = tracksEnabled();
  try {
    const session = await getStripe().checkout.sessions.create({
      mode: "payment",
      line_items: [
        priceId
          ? { price: priceId, quantity: 1 }
          : {
              quantity: 1,
              price_data: {
                currency: "usd",
                unit_amount: priceUsd() * 100,
                product_data: {
                  name: allTracks ? `${SITE_NAME}: all tracks` : `${SITE_NAME}: Forward Deployed Engineering course`,
                  description: allTracks
                    ? "Lifetime access to Foundations and the Applied AI Engineer, Applied AI Architect and Forward Deployed Engineer tracks."
                    : "Lifetime access to all modules, exercises and the AI tutor.",
                },
              },
            },
      ],
      client_reference_id: viewer.user.id,
      customer_email: viewer.user.email ?? undefined,
      metadata: { user_id: viewer.user.id },
      allow_promotion_codes: true,
      success_url: `${origin}/purchase/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${origin}/#pricing`,
    });
    return NextResponse.redirect(session.url!, 303);
  } catch (err) {
    console.error("Checkout session creation failed", err);
    return NextResponse.redirect(new URL("/learn?checkout=error", origin), 303);
  }
}
