import { NextResponse } from "next/server";
import type Stripe from "stripe";
import { getStripe, recordPurchase, recordRefund } from "@/lib/purchases";

// Stripe → us. Configure in the Stripe dashboard (Developers → Webhooks) with events:
//   checkout.session.completed, checkout.session.async_payment_succeeded, charge.refunded
export async function POST(req: Request) {
  const secret = process.env.STRIPE_WEBHOOK_SECRET;
  if (!secret || !process.env.STRIPE_SECRET_KEY) {
    return NextResponse.json({ error: "Stripe is not configured" }, { status: 500 });
  }

  const signature = req.headers.get("stripe-signature");
  if (!signature) return NextResponse.json({ error: "Missing stripe-signature header" }, { status: 400 });

  const body = await req.text(); // the raw body is required for signature verification
  let event: Stripe.Event;
  try {
    event = getStripe().webhooks.constructEvent(body, signature, secret);
  } catch {
    return NextResponse.json({ error: "Invalid signature" }, { status: 400 });
  }

  try {
    switch (event.type) {
      case "checkout.session.completed":
      case "checkout.session.async_payment_succeeded":
        await recordPurchase(event.data.object);
        break;
      case "charge.refunded": {
        const charge = event.data.object;
        const pi = typeof charge.payment_intent === "string" ? charge.payment_intent : charge.payment_intent?.id;
        // Partial refunds keep access; only a full refund revokes it.
        if (pi && charge.refunded) await recordRefund(pi);
        break;
      }
      default:
        break;
    }
  } catch (err) {
    console.error(`Stripe webhook ${event.type} failed`, err);
    // 500 makes Stripe retry the event later.
    return NextResponse.json({ error: "Handler failed" }, { status: 500 });
  }

  return NextResponse.json({ received: true });
}
