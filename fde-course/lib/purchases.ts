import "server-only";
import Stripe from "stripe";
import { createAdminClient } from "@/lib/supabase/server";

let stripeClient: Stripe | null = null;

export function getStripe(): Stripe {
  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) throw new Error("STRIPE_SECRET_KEY is not set");
  stripeClient ??= new Stripe(key);
  return stripeClient;
}

/**
 * Records a paid Checkout Session as a purchase. Idempotent: the webhook and the
 * success page may both call it for the same session.
 * Returns false if the session isn't paid or has no user attached.
 */
export async function recordPurchase(session: Stripe.Checkout.Session): Promise<boolean> {
  const userId = session.client_reference_id;
  if (session.payment_status !== "paid" || !userId) return false;

  const paymentIntent = typeof session.payment_intent === "string" ? session.payment_intent : session.payment_intent?.id ?? null;
  const { error } = await createAdminClient()
    .from("purchases")
    .upsert(
      {
        user_id: userId,
        stripe_session_id: session.id,
        stripe_payment_intent: paymentIntent,
        amount_total: session.amount_total,
        currency: session.currency,
        status: "paid",
      },
      { onConflict: "stripe_session_id", ignoreDuplicates: true },
    );
  if (error) throw new Error(`recordPurchase failed: ${error.message}`);
  return true;
}

/** Marks every purchase tied to a fully refunded payment as refunded, which removes access. */
export async function recordRefund(paymentIntentId: string): Promise<void> {
  const { error } = await createAdminClient()
    .from("purchases")
    .update({ status: "refunded" })
    .eq("stripe_payment_intent", paymentIntentId);
  if (error) throw new Error(`recordRefund failed: ${error.message}`);
}
