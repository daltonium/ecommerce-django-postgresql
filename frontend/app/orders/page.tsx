import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import Link from "next/link"

// Sample orders data
const orders = [
  {
    id: "ORD-12345",
    date: "May 2, 2026",
    status: "Delivered",
    total: 7497,
    items: [
      { name: "Wireless Bluetooth Headphones", price: 2499, quantity: 1, image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=100&h=100&fit=crop" },
      { name: "Smart Watch with Health Tracking", price: 4999, quantity: 1, image: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=100&h=100&fit=crop" },
    ],
  },
  {
    id: "ORD-12344",
    date: "April 28, 2026",
    status: "Shipped",
    total: 3499,
    items: [
      { name: "Professional Running Shoes", price: 3499, quantity: 1, image: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=100&h=100&fit=crop" },
    ],
  },
  {
    id: "ORD-12343",
    date: "April 20, 2026",
    status: "Delivered",
    total: 2598,
    items: [
      { name: "Ceramic Plant Pot Set", price: 1299, quantity: 2, image: "https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=100&h=100&fit=crop" },
    ],
  },
  {
    id: "ORD-12342",
    date: "April 15, 2026",
    status: "Cancelled",
    total: 1999,
    items: [
      { name: "Organic Skincare Gift Set", price: 1999, quantity: 1, image: "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=100&h=100&fit=crop" },
    ],
  },
]

function getStatusStyles(status: string) {
  switch (status) {
    case "Delivered":
      return { bg: "bg-green-100", text: "text-green-700", dot: "bg-green-500" }
    case "Shipped":
      return { bg: "bg-blue-100", text: "text-blue-700", dot: "bg-blue-500" }
    case "Processing":
      return { bg: "bg-yellow-100", text: "text-yellow-700", dot: "bg-yellow-500" }
    case "Cancelled":
      return { bg: "bg-red-100", text: "text-red-700", dot: "bg-red-500" }
    default:
      return { bg: "bg-gray-100", text: "text-gray-700", dot: "bg-gray-500" }
  }
}

export default function OrdersPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      
      <main className="flex-1 py-8 sm:py-12">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          {/* Breadcrumb */}
          <nav className="mb-6 flex items-center gap-2 text-sm text-muted-foreground" aria-label="Breadcrumb">
            <Link href="/" className="hover:text-coral transition-colors">Home</Link>
            <span aria-hidden="true">→</span>
            <span className="text-foreground" aria-current="page">My Orders</span>
          </nav>

          <h1 className="text-2xl font-bold text-foreground sm:text-3xl mb-8">
            My Orders
          </h1>

          {orders.length > 0 ? (
            <div className="space-y-6">
              {orders.map((order) => {
                const statusStyles = getStatusStyles(order.status)
                return (
                  <article key={order.id} className="rounded-xl bg-card shadow-sm overflow-hidden">
                    {/* Order Header */}
                    <div className="flex flex-wrap items-center justify-between gap-4 border-b border-border bg-muted/30 px-5 py-4">
                      <div className="flex flex-wrap items-center gap-x-6 gap-y-2">
                        <div>
                          <p className="text-xs text-muted-foreground uppercase tracking-wide">Order</p>
                          <p className="font-semibold text-card-foreground">{order.id}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground uppercase tracking-wide">Date</p>
                          <p className="font-medium text-card-foreground">{order.date}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground uppercase tracking-wide">Total</p>
                          <p className="font-semibold text-card-foreground">₹{order.total.toLocaleString()}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`inline-flex h-2 w-2 rounded-full ${statusStyles.dot}`}></span>
                        <span className={`text-sm font-medium ${statusStyles.text}`}>{order.status}</span>
                      </div>
                    </div>

                    {/* Order Items */}
                    <div className="divide-y divide-border">
                      {order.items.map((item, index) => (
                        <div key={index} className="flex gap-4 p-5">
                          <div className="h-20 w-20 shrink-0 overflow-hidden rounded-lg bg-muted">
                            <img src={item.image} alt={item.name} className="h-full w-full object-cover" />
                          </div>
                          <div className="flex flex-1 flex-col justify-between">
                            <div>
                              <h3 className="font-medium text-card-foreground line-clamp-2">{item.name}</h3>
                              <p className="mt-1 text-sm text-muted-foreground">Qty: {item.quantity}</p>
                            </div>
                            <p className="font-semibold text-card-foreground">₹{item.price.toLocaleString()}</p>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Order Actions */}
                    <div className="flex flex-wrap items-center justify-between gap-4 border-t border-border px-5 py-4">
                      <div className="flex flex-wrap gap-3">
                        <Link
                          href={`/orders/${order.id}`}
                          className="text-sm font-medium text-coral hover:text-coral-hover transition-colors focus:outline-none focus-visible:underline"
                        >
                          View Details
                        </Link>
                        {order.status === "Delivered" && (
                          <button
                            type="button"
                            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors focus:outline-none focus-visible:underline"
                          >
                            Write a Review
                          </button>
                        )}
                        {order.status === "Shipped" && (
                          <button
                            type="button"
                            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors focus:outline-none focus-visible:underline"
                          >
                            Track Order
                          </button>
                        )}
                      </div>
                      {order.status === "Delivered" && (
                        <button
                          type="button"
                          className="rounded-lg border-2 border-border bg-transparent px-4 py-2 text-sm font-medium text-card-foreground transition-colors hover:bg-muted focus:outline-none focus-visible:ring-2 focus-visible:ring-coral"
                        >
                          Buy Again
                        </button>
                      )}
                    </div>
                  </article>
                )
              })}
            </div>
          ) : (
            /* Empty State */
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <div className="flex h-24 w-24 items-center justify-center rounded-full bg-muted text-muted-foreground mb-6">
                <svg className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-foreground mb-2">No orders yet</h2>
              <p className="text-muted-foreground mb-6 max-w-md">
                You haven&apos;t placed any orders yet. Start shopping to see your orders here!
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
