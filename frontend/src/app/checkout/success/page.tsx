"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";

export default function CheckoutSuccessPage() {
  const search = useSearchParams();
  const orderId = search.get("order");

  return (
    <section className="section">
      <div className="container auth-card">
        <h1>Thank you!</h1>
        <p className="auth-subtitle">
          {orderId ? `Order #${orderId} has been placed.` : "Your order has been placed."}
          We will contact you soon to confirm the details.
        </p>
        <div className="checkout-success__actions">
          <Link className="btn btn-primary" href="/products">
            Continue shopping
          </Link>
          <Link className="btn btn-outline" href="/">
            Go to homepage
          </Link>
        </div>
      </div>
    </section>
  );
}

