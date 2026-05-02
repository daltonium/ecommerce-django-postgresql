import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import Link from "next/link"

// Sample cart data
const cartItems = [
  {
    id: 1,
    name: "Wireless Bluetooth Headphones with Active Noise Cancellation",
    price: 2499,
    quantity: 1,
    imageUrl: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=200&h=200&fit=crop",
  },
  {
    id: 3,
    name: "Smart Watch with Health Tracking",
    price: 4999,
    quantity: 1,
    imageUrl: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=200&h=200&fit=crop",
  },
  {
    id: 6,
    name: "Professional Running Shoes",
    price: 3499,
    quantity: 2,
    imageUrl: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=200&h=200&fit=crop",
  },
]

export default function CartPage() {
  const subtotal = cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0)
  const shipping = subtotal > 999 ? 0 : 99
  const total = subtotal + shipping

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      
      <main className="flex-1 py-8 sm:py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          {/* Breadcrumb */}
          <nav className="mb-6 flex items-center gap-2 text-sm text-muted-foreground" aria-label="Breadcrumb">
            <Link href="/" className="hover:text-coral transition-colors">Home</Link>
            <span aria-hidden="true">→</span>
            <span className="text-foreground" aria-current="page">Shopping Cart</span>
          </nav>

          <h1 className="text-2xl font-bold text-foreground sm:text-3xl mb-8">
            Shopping Cart
          </h1>

          {cartItems.length > 0 ? (
            <div className="grid gap-8 lg:grid-cols-3">
              {/* Cart Items */}
              <div className="lg:col-span-2">
                <div className="space-y-4">
                  {cartItems.map((item) => (
                    <article 
                      key={item.id} 
                      className="flex gap-4 rounded-xl bg-card p-4 shadow-sm sm:gap-6 sm:p-6"
                    >
                      {/* Product Image */}
                      <Link href={`/products/${item.id}`} className="shrink-0">
                        <div className="h-24 w-24 overflow-hidden rounded-lg bg-muted sm:h-32 sm:w-32">
                          <img
                            src={item.imageUrl}
                            alt={item.name}
                            className="h-full w-full object-cover"
                          />
                        </div>
                      </Link>

                      {/* Product Details */}
                      <div className="flex flex-1 flex-col justify-between">
                        <div>
                          <Link 
                            href={`/products/${item.id}`}
                            className="text-sm font-medium text-card-foreground hover:text-coral transition-colors line-clamp-2 sm:text-base focus:outline-none focus-visible:underline"
                          >
                            {item.name}
                          </Link>
                          <p className="mt-2 text-lg font-bold text-card-foreground">
                            ₹{item.price.toLocaleString()}
                          </p>
                        </div>

                        {/* Actions */}
                        <div className="mt-4 flex items-center justify-between">
                          {/* Quantity */}
                          <div className="flex items-center rounded-lg border border-border">
                            <button
                              type="button"
                              className="flex h-9 w-9 items-center justify-center text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-coral"
                              aria-label="Decrease quantity"
                            >
                              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                <path strokeLinecap="round" strokeLinejoin="round" d="M20 12H4" />
                              </svg>
                            </button>
                            <span className="w-12 text-center text-sm font-medium text-card-foreground">
                              {item.quantity}
                            </span>
                            <button
                              type="button"
                              className="flex h-9 w-9 items-center justify-center text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-coral"
                              aria-label="Increase quantity"
                            >
                              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                              </svg>
                            </button>
                          </div>

                          {/* Remove */}
                          <button
                            type="button"
                            className="text-sm font-medium text-muted-foreground transition-colors hover:text-coral focus:outline-none focus-visible:underline"
                          >
                            Remove
                          </button>
                        </div>
                      </div>
                    </article>
                  ))}
                </div>

                {/* Clear Cart */}
                <div className="mt-6">
                  <button
                    type="button"
                    className="text-sm font-medium text-muted-foreground transition-colors hover:text-coral focus:outline-none focus-visible:underline"
                  >
                    Clear all items
                  </button>
                </div>
              </div>

              {/* Order Summary */}
              <div className="lg:col-span-1">
                <div className="sticky top-24 rounded-xl bg-card p-6 shadow-sm">
                  <h2 className="text-lg font-semibold text-card-foreground mb-6 pb-4 border-b border-border">
                    Order Summary
                  </h2>

                  <dl className="space-y-4">
                    <div className="flex justify-between text-sm">
                      <dt className="text-muted-foreground">Subtotal ({cartItems.length} items)</dt>
                      <dd className="font-medium text-card-foreground">₹{subtotal.toLocaleString()}</dd>
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
                        Add ₹{(999 - subtotal).toLocaleString()} more for free shipping
                      </p>
                    )}
                    <div className="flex justify-between border-t border-border pt-4">
                      <dt className="text-base font-semibold text-card-foreground">Total</dt>
                      <dd className="text-xl font-bold text-card-foreground">₹{total.toLocaleString()}</dd>
                    </div>
                  </dl>

                  <Link
                    href="/checkout"
                    className="mt-6 flex w-full items-center justify-center rounded-lg bg-coral py-3 text-base font-semibold text-white transition-colors hover:bg-coral-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-coral focus-visible:ring-offset-2"
                  >
                    Proceed to Checkout
                  </Link>

                  <Link
                    href="/products"
                    className="mt-4 flex w-full items-center justify-center rounded-lg border-2 border-border bg-transparent py-3 text-base font-medium text-card-foreground transition-colors hover:bg-muted focus:outline-none focus-visible:ring-2 focus-visible:ring-coral focus-visible:ring-offset-2"
                  >
                    Continue Shopping
                  </Link>

                  {/* Security Badges */}
                  <div className="mt-6 pt-6 border-t border-border">
                    <div className="flex items-center justify-center gap-4 text-muted-foreground">
                      <div className="flex items-center gap-1 text-xs">
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                        </svg>
                        Secure Checkout
                      </div>
                      <div className="flex items-center gap-1 text-xs">
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                        </svg>
                        SSL Encrypted
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            /* Empty Cart State */
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <div className="flex h-24 w-24 items-center justify-center rounded-full bg-muted text-muted-foreground mb-6">
                <svg className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-foreground mb-2">Your cart is empty</h2>
              <p className="text-muted-foreground mb-6 max-w-md">
                Looks like you haven&apos;t added any items to your cart yet. Start shopping to fill it up!
              </p>
              <Link
                href="/products"
                className="inline-flex items-center justify-center rounded-lg bg-coral px-6 py-3 text-base font-semibold text-white transition-colors hover:bg-coral-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-coral focus-visible:ring-offset-2"
              >
                Start Shopping
              </Link>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  )
}
