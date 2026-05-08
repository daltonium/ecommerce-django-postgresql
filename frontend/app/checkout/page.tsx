"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Header } from "@/components/header";
import { Footer } from "@/components/footer";

// ─── Razorpay global type declaration ────────────────────────────────────────
declare global {
  interface Window {
    Razorpay: new (options: RazorpayOptions) => { open: () => void };
  }
}
interface RazorpayOptions {
  key: string;
  amount: number;
  currency: string;
  name: string;
  description: string;
  order_id: string;
  handler: (response: RazorpayResponse) => void;
  prefill?: { name?: string; contact?: string };
  theme?: { color?: string };
  modal?: { ondismiss?: () => void };
}
interface RazorpayResponse {
  razorpay_order_id: string;
  razorpay_payment_id: string;
  razorpay_signature: string;
}

// ─── Types ────────────────────────────────────────────────────────────────────
interface CartItem {
  id: number;
  product: { id: number; name: string; price: string; image?: string };
  quantity: number;
  subtotal: string;
}
interface Cart {
  items: CartItem[];
  total_price: string;
  total_items: number;
}

// ─── SVG icon components (defined outside to avoid JSX parse errors) ─────────
const IconCart = () => (
  <svg className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
  </svg>
);

const IconCard = () => (
  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
  </svg>
);

const IconCheck = () => (
  <svg className="ml-auto h-5 w-5 text-coral" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
  </svg>
);

const IconWarning = () => (
  <svg className="h-5 w-5 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
  </svg>
);

const IconLock = () => {
  const d = "M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z";
  return (
    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d={d} />
    </svg>
  );
};

const IconLockSmall = () => {
  const d = "M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z";
  return (
    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d={d} />
    </svg>
  );
};

// ─── API helpers ──────────────────────────────────────────────────────────────
const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

function authHeaders() {
  const token = localStorage.getItem("accesstoken") ?? "";
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

async function fetchCart(): Promise<Cart> {
  const res = await fetch(`${BASE}/cart/`, { headers: authHeaders() });
  if (!res.ok) throw new Error("Failed to fetch cart");
  return res.json();
}

async function createOrder(shippingAddress: string) {
  const res = await fetch(`${BASE}/orders/create/`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ shipping_address: shippingAddress }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || "Failed to create order");
  }
  return res.json();
}

async function initiatePayment(orderId: number) {
  const res = await fetch(`${BASE}/payments/create/`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ order_id: orderId }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || "Failed to initiate payment");
  }
  return res.json();
}

async function verifyPayment(data: RazorpayResponse) {
  const res = await fetch(`${BASE}/payments/verify/`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || "Payment verification failed");
  }
  return res.json();
}

// ─── Form shape ───────────────────────────────────────────────────────────────
interface FormState {
  fullName: string;
  phone: string;
  addressLine: string;
  city: string;
  state: string;
  pincode: string;
}

// ─── Main Component ───────────────────────────────────────────────────────────
export default function CheckoutPage() {
  const router = useRouter();

  const [cart, setCart] = useState<Cart | null>(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState<FormState>({
    fullName: "",
    phone: "",
    addressLine: "",
    city: "",
    state: "",
    pincode: "",
  });
  const [formErrors, setFormErrors] = useState<Partial<FormState>>({});

  // Load Razorpay SDK
  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.async = true;
    document.body.appendChild(script);
    return () => {
      document.body.removeChild(script);
    };
  }, []);

  // Fetch cart
  useEffect(() => {
    fetchCart()
      .then(setCart)
      .catch(() => setError("Could not load your cart. Please try again."))
      .finally(() => setLoading(false));
  }, []);

  function validate(): boolean {
    const errors: Partial<FormState> = {};
    if (!form.fullName.trim()) errors.fullName = "Full name is required";
    if (!form.phone.trim() || !/^\d{10}$/.test(form.phone))
      errors.phone = "Enter a valid 10-digit phone number";
    if (!form.addressLine.trim()) errors.addressLine = "Address is required";
    if (!form.city.trim()) errors.city = "City is required";
    if (!form.state.trim()) errors.state = "State is required";
    if (!form.pincode.trim() || !/^\d{6}$/.test(form.pincode))
      errors.pincode = "Enter a valid 6-digit PIN code";
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  }

  function fieldClass(field: keyof FormState) {
    const base =
      "w-full rounded-lg border px-4 py-2.5 text-sm text-card-foreground bg-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-coral focus:border-coral transition-colors";
    return formErrors[field] ? `${base} border-red-400` : `${base} border-border`;
  }

  async function handlePlaceOrder() {
    if (!validate()) return;
    setProcessing(true);
    setError(null);

    try {
      const shippingAddress = `${form.fullName}, ${form.addressLine}, ${form.city}, ${form.state} - ${form.pincode}. Phone: ${form.phone}`;
      const order = await createOrder(shippingAddress);
      const paymentData = await initiatePayment(order.id);

      const rzp = new window.Razorpay({
        key: paymentData.key,
        amount: paymentData.amount,
        currency: paymentData.currency || "INR",
        name: "BlueCart",
        description: `Order #${order.id}`,
        order_id: paymentData.razorpay_order_id,
        handler: async (response: RazorpayResponse) => {
          try {
            await verifyPayment(response);
            router.push(`/orders/${order.id}?success=true`);
          } catch {
            setError(
              `Payment received but verification failed. Contact support with Order ID: ${order.id}`
            );
            setProcessing(false);
          }
        },
        prefill: { name: form.fullName, contact: form.phone },
        theme: { color: "#F95C4B" },
        modal: {
          ondismiss: () => {
            setProcessing(false);
            setError(
              "Payment cancelled. Your order is saved — retry payment from your Orders page."
            );
          },
        },
      });

      rzp.open();
    } catch (err: unknown) {
      setError(
        err instanceof Error ? err.message : "Something went wrong. Please try again."
      );
      setProcessing(false);
    }
  }

  // ─── Loading state ────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="flex min-h-screen flex-col">
        <Header />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="h-10 w-10 border-4 border-coral border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-muted-foreground">Loading your cart...</p>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  // ─── Empty cart state ─────────────────────────────────────────────────────
  if (!cart || cart.items.length === 0) {
    return (
      <div className="flex min-h-screen flex-col">
        <Header />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center py-16">
            <div className="flex h-24 w-24 items-center justify-center rounded-full bg-muted text-muted-foreground mb-6 mx-auto">
              <IconCart />
            </div>
            <h2 className="text-xl font-semibold text-foreground mb-2">Your cart is empty</h2>
            <p className="text-muted-foreground mb-6">Add some items before checking out.</p>
            <Link
              href="/products"
              className="inline-flex items-center justify-center rounded-lg bg-coral px-6 py-3 text-base font-semibold text-white transition-colors hover:bg-coral-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-coral focus-visible:ring-offset-2"
            >
              Start Shopping
            </Link>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  const subtotal = parseFloat(cart.total_price);
  const shipping = subtotal > 999 ? 0 : 99;
  const total = subtotal + shipping;

  // ─── Main render ──────────────────────────────────────────────────────────
  return (
    <div className="flex min-h-screen flex-col">
      <Header />

      <main className="flex-1 py-8 sm:py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">

          {/* Breadcrumb */}
          <nav className="mb-6 flex items-center gap-2 text-sm text-muted-foreground" aria-label="Breadcrumb">
            <Link href="/" className="hover:text-coral transition-colors">Home</Link>
            <span aria-hidden="true">›</span>
            <Link href="/cart" className="hover:text-coral transition-colors">Cart</Link>
            <span aria-hidden="true">›</span>
            <span className="text-foreground" aria-current="page">Checkout</span>
          </nav>

          <h1 className="text-2xl font-bold text-foreground sm:text-3xl mb-8">Checkout</h1>

          {/* Error banner */}
          {error && (
            <div role="alert" className="mb-6 rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-700 flex gap-3">
              <IconWarning />
              <p>{error}</p>
            </div>
          )}

          <div className="grid gap-8 lg:grid-cols-3">

            {/* ── LEFT: Shipping + Payment ── */}
            <div className="lg:col-span-2 space-y-6">

              {/* Shipping form */}
              <section className="rounded-xl bg-card p-6 shadow-sm">
                <h2 className="text-lg font-semibold text-card-foreground mb-6">Delivery Address</h2>

                <div className="grid gap-4 sm:grid-cols-2">

                  {/* Full Name */}
                  <div className="sm:col-span-2">
                    <label htmlFor="fullName" className="block text-sm font-medium text-card-foreground mb-1.5">
                      Full Name *
                    </label>
                    <input
                      id="fullName"
                      type="text"
                      value={form.fullName}
                      onChange={(e) => setForm({ ...form, fullName: e.target.value })}
                      placeholder="e.g. Rahul Kumar"
                      className={fieldClass("fullName")}
                    />
                    {formErrors.fullName && (
                      <p className="mt-1 text-xs text-red-600">{formErrors.fullName}</p>
                    )}
                  </div>

                  {/* Phone */}
                  <div>
                    <label htmlFor="phone" className="block text-sm font-medium text-card-foreground mb-1.5">
                      Phone Number *
                    </label>
                    <input
                      id="phone"
                      type="tel"
                      value={form.phone}
                      onChange={(e) => setForm({ ...form, phone: e.target.value })}
                      placeholder="10-digit mobile number"
                      maxLength={10}
                      className={fieldClass("phone")}
                    />
                    {formErrors.phone && (
                      <p className="mt-1 text-xs text-red-600">{formErrors.phone}</p>
                    )}
                  </div>

                  {/* Pincode */}
                  <div>
                    <label htmlFor="pincode" className="block text-sm font-medium text-card-foreground mb-1.5">
                      PIN Code *
                    </label>
                    <input
                      id="pincode"
                      type="text"
                      value={form.pincode}
                      onChange={(e) => setForm({ ...form, pincode: e.target.value })}
                      placeholder="6-digit PIN"
                      maxLength={6}
                      className={fieldClass("pincode")}
                    />
                    {formErrors.pincode && (
                      <p className="mt-1 text-xs text-red-600">{formErrors.pincode}</p>
                    )}
                  </div>

                  {/* Address Line */}
                  <div className="sm:col-span-2">
                    <label htmlFor="addressLine" className="block text-sm font-medium text-card-foreground mb-1.5">
                      Address Line *
                    </label>
                    <input
                      id="addressLine"
                      type="text"
                      value={form.addressLine}
                      onChange={(e) => setForm({ ...form, addressLine: e.target.value })}
                      placeholder="House/Flat no., Street, Locality"
                      className={fieldClass("addressLine")}
                    />
                    {formErrors.addressLine && (
                      <p className="mt-1 text-xs text-red-600">{formErrors.addressLine}</p>
                    )}
                  </div>

                  {/* City */}
                  <div>
                    <label htmlFor="city" className="block text-sm font-medium text-card-foreground mb-1.5">
                      City *
                    </label>
                    <input
                      id="city"
                      type="text"
                      value={form.city}
                      onChange={(e) => setForm({ ...form, city: e.target.value })}
                      placeholder="e.g. Chennai"
                      className={fieldClass("city")}
                    />
                    {formErrors.city && (
                      <p className="mt-1 text-xs text-red-600">{formErrors.city}</p>
                    )}
                  </div>

                  {/* State */}
                  <div>
                    <label htmlFor="state" className="block text-sm font-medium text-card-foreground mb-1.5">
                      State *
                    </label>
                    <input
                      id="state"
                      type="text"
                      value={form.state}
                      onChange={(e) => setForm({ ...form, state: e.target.value })}
                      placeholder="e.g. Tamil Nadu"
                      className={fieldClass("state")}
                    />
                    {formErrors.state && (
                      <p className="mt-1 text-xs text-red-600">{formErrors.state}</p>
                    )}
                  </div>

                </div>
              </section>

              {/* Payment method */}
              <section className="rounded-xl bg-card p-6 shadow-sm">
                <h2 className="text-lg font-semibold text-card-foreground mb-4">Payment</h2>
                <div className="flex items-center gap-3 rounded-lg border-2 border-coral bg-coral/5 p-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-coral/10 text-coral">
                    <IconCard />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-card-foreground">Razorpay — Secure Payment</p>
                    <p className="text-xs text-muted-foreground">UPI, Cards, Net Banking, Wallets accepted</p>
                  </div>
                  <IconCheck />
                </div>
              </section>

            </div>

            {/* ── RIGHT: Order Summary ── */}
            <div className="lg:col-span-1">
              <div className="sticky top-24 rounded-xl bg-card p-6 shadow-sm">
                <h2 className="text-lg font-semibold text-card-foreground mb-6 pb-4 border-b border-border">
                  Order Summary
                </h2>

                {/* Items list */}
                <ul className="space-y-3 mb-6" aria-label="Cart items">
                  {cart.items.map((item) => (
                    <li key={item.id} className="flex items-center gap-3">
                      <div className="h-12 w-12 shrink-0 rounded-md bg-muted overflow-hidden">
                        {item.product.image ? (
                          <img
                            src={item.product.image}
                            alt={item.product.name}
                            className="h-full w-full object-cover"
                            loading="lazy"
                            width={48}
                            height={48}
                          />
                        ) : (
                          <div className="h-full w-full flex items-center justify-center text-muted-foreground text-xs">
                            IMG
                          </div>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-card-foreground line-clamp-1">
                          {item.product.name}
                        </p>
                        <p className="text-xs text-muted-foreground">Qty: {item.quantity}</p>
                      </div>
                      <p className="text-sm font-semibold text-card-foreground shrink-0">
                        ₹{parseFloat(item.subtotal).toLocaleString("en-IN")}
                      </p>
                    </li>
                  ))}
                </ul>

                {/* Totals */}
                <dl className="space-y-3 border-t border-border pt-4">
                  <div className="flex justify-between text-sm">
                    <dt className="text-muted-foreground">
                      Subtotal ({cart.total_items} {cart.total_items === 1 ? "item" : "items"})
                    </dt>
                    <dd className="font-medium text-card-foreground">
                      ₹{subtotal.toLocaleString("en-IN")}
                    </dd>
                  </div>
                  <div className="flex justify-between text-sm">
                    <dt className="text-muted-foreground">Shipping</dt>
                    <dd className="font-medium text-card-foreground">
                      {shipping === 0 ? (
                        <span className="text-green-600">FREE</span>
                      ) : (
                        `₹${shipping}`
                      )}
                    </dd>
                  </div>
                  {shipping > 0 && (
                    <p className="text-xs text-coral">
                      Add ₹{(999 - subtotal).toLocaleString("en-IN")} more for free shipping
                    </p>
                  )}
                  <div className="flex justify-between border-t border-border pt-3">
                    <dt className="text-base font-semibold text-card-foreground">Total</dt>
                    <dd className="text-xl font-bold text-card-foreground">
                      ₹{total.toLocaleString("en-IN")}
                    </dd>
                  </div>
                </dl>

                {/* CTA button */}
                <button
                  type="button"
                  onClick={handlePlaceOrder}
                  disabled={processing}
                  className="mt-6 flex w-full items-center justify-center gap-2 rounded-lg bg-coral py-3 text-base font-semibold text-white transition-colors hover:bg-coral-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-coral focus-visible:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed"
                >
                  {processing ? (
                    <>
                      <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <IconLock />
                      Pay ₹{total.toLocaleString("en-IN")} Securely
                    </>
                  )}
                </button>

                {/* Security badges */}
                <div className="mt-4 pt-4 border-t border-border">
                  <div className="flex items-center justify-center gap-4 text-muted-foreground">
                    <div className="flex items-center gap-1 text-xs">
                      <IconLockSmall />
                      Secure Checkout
                    </div>
                    <div className="h-3 w-px bg-border" />
                    <p className="text-xs">SSL Encrypted</p>
                  </div>
                </div>

              </div>
            </div>

          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}