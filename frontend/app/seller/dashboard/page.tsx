import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import Link from "next/link"

// Sample data
const stats = [
  { label: "Total Sales", value: "₹1,24,500", change: "+12.5%", positive: true },
  { label: "Orders", value: "156", change: "+8.2%", positive: true },
  { label: "Products", value: "24", change: "+2", positive: true },
  { label: "Avg. Rating", value: "4.6", change: "-0.1", positive: false },
]

const recentOrders = [
  { id: "ORD-001", customer: "Rahul Kumar", product: "Wireless Headphones", amount: 2499, status: "Paid", date: "May 2, 2026" },
  { id: "ORD-002", customer: "Priya Sharma", product: "Smart Watch", amount: 4999, status: "Shipped", date: "May 1, 2026" },
  { id: "ORD-003", customer: "Amit Singh", product: "Running Shoes", amount: 3499, status: "Delivered", date: "Apr 30, 2026" },
  { id: "ORD-004", customer: "Sneha Patel", product: "Bluetooth Speaker", amount: 1999, status: "Pending", date: "Apr 30, 2026" },
]

const sidebarLinks = [
  { name: "Dashboard", href: "/seller/dashboard", icon: "dashboard", active: true },
  { name: "Products", href: "/seller/products", icon: "products", active: false },
  { name: "Orders", href: "/seller/orders", icon: "orders", active: false },
  { name: "Messages", href: "/seller/messages", icon: "messages", active: false },
  { name: "Settings", href: "/seller/settings", icon: "settings", active: false },
]

function getStatusStyles(status: string) {
  switch (status) {
    case "Paid":
      return "bg-green-100 text-green-700"
    case "Shipped":
      return "bg-blue-100 text-blue-700"
    case "Delivered":
      return "bg-green-100 text-green-700"
    case "Pending":
      return "bg-yellow-100 text-yellow-700"
    case "Cancelled":
      return "bg-red-100 text-red-700"
    default:
      return "bg-gray-100 text-gray-700"
  }
}

export default function SellerDashboardPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      
      <main className="flex-1 py-8">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid gap-8 lg:grid-cols-4">
            {/* Sidebar */}
            <aside className="lg:col-span-1">
              <nav className="sticky top-24 rounded-xl bg-card p-4 shadow-sm" aria-label="Seller navigation">
                <div className="mb-6 px-3">
                  <h2 className="text-lg font-semibold text-card-foreground">Seller Hub</h2>
                  <p className="text-sm text-muted-foreground">Manage your store</p>
                </div>
                <ul className="space-y-1">
                  {sidebarLinks.map((link) => (
                    <li key={link.name}>
                      <Link
                        href={link.href}
                        className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-coral ${
                          link.active
                            ? "bg-coral text-white"
                            : "text-card-foreground hover:bg-muted"
                        }`}
                      >
                        {link.icon === "dashboard" && (
                          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                          </svg>
                        )}
                        {link.icon === "products" && (
                          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                          </svg>
                        )}
                        {link.icon === "orders" && (
                          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                          </svg>
                        )}
                        {link.icon === "messages" && (
                          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                          </svg>
                        )}
                        {link.icon === "settings" && (
                          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                            <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          </svg>
                        )}
                        {link.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              </nav>
            </aside>

            {/* Main Content */}
            <div className="lg:col-span-3 space-y-8">
              {/* Header */}
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
                  <p className="text-muted-foreground">Welcome back! Here&apos;s your store overview.</p>
                </div>
                <Link
                  href="/seller/products/new"
                  className="inline-flex items-center justify-center gap-2 rounded-lg bg-coral px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-coral-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-coral focus-visible:ring-offset-2"
                >
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                  </svg>
                  Add Product
                </Link>
              </div>

              {/* Stats Grid */}
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {stats.map((stat) => (
                  <div key={stat.label} className="rounded-xl bg-card p-5 shadow-sm">
                    <p className="text-sm text-muted-foreground">{stat.label}</p>
                    <p className="mt-2 text-2xl font-bold text-card-foreground">{stat.value}</p>
                    <p className={`mt-1 text-sm font-medium ${stat.positive ? "text-green-600" : "text-red-500"}`}>
                      {stat.change}
                    </p>
                  </div>
                ))}
              </div>

              {/* Recent Orders */}
              <section aria-labelledby="orders-heading">
                <div className="flex items-center justify-between mb-4">
                  <h2 id="orders-heading" className="text-lg font-semibold text-foreground">
                    Recent Orders
                  </h2>
                  <Link 
                    href="/seller/orders" 
                    className="text-sm font-medium text-coral hover:text-coral-hover transition-colors"
                  >
                    View All →
                  </Link>
                </div>

                <div className="overflow-hidden rounded-xl bg-card shadow-sm">
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-border bg-muted/50">
                          <th scope="col" className="px-4 py-3 text-left text-sm font-semibold text-card-foreground">
                            Order ID
                          </th>
                          <th scope="col" className="px-4 py-3 text-left text-sm font-semibold text-card-foreground">
                            Customer
                          </th>
                          <th scope="col" className="px-4 py-3 text-left text-sm font-semibold text-card-foreground hidden sm:table-cell">
                            Product
                          </th>
                          <th scope="col" className="px-4 py-3 text-left text-sm font-semibold text-card-foreground">
                            Amount
                          </th>
                          <th scope="col" className="px-4 py-3 text-left text-sm font-semibold text-card-foreground">
                            Status
                          </th>
                          <th scope="col" className="px-4 py-3 text-left text-sm font-semibold text-card-foreground hidden md:table-cell">
                            Date
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border">
                        {recentOrders.map((order) => (
                          <tr key={order.id} className="hover:bg-muted/30 transition-colors">
                            <td className="px-4 py-3 text-sm font-medium text-coral">
                              {order.id}
                            </td>
                            <td className="px-4 py-3 text-sm text-card-foreground">
                              {order.customer}
                            </td>
                            <td className="px-4 py-3 text-sm text-muted-foreground hidden sm:table-cell">
                              {order.product}
                            </td>
                            <td className="px-4 py-3 text-sm font-medium text-card-foreground">
                              ₹{order.amount.toLocaleString()}
                            </td>
                            <td className="px-4 py-3">
                              <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${getStatusStyles(order.status)}`}>
                                {order.status}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-sm text-muted-foreground hidden md:table-cell">
                              {order.date}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </section>

              {/* Quick Actions */}
              <section aria-labelledby="actions-heading">
                <h2 id="actions-heading" className="text-lg font-semibold text-foreground mb-4">
                  Quick Actions
                </h2>
                <div className="grid gap-4 sm:grid-cols-3">
                  <Link
                    href="/seller/products/new"
                    className="flex items-center gap-4 rounded-xl bg-card p-5 shadow-sm transition-all hover:shadow-md hover:-translate-y-0.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-coral"
                  >
                    <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-coral/10 text-coral">
                      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                      </svg>
                    </div>
                    <div>
                      <p className="font-medium text-card-foreground">Add New Product</p>
                      <p className="text-sm text-muted-foreground">List a new item</p>
                    </div>
                  </Link>

                  <Link
                    href="/seller/orders"
                    className="flex items-center gap-4 rounded-xl bg-card p-5 shadow-sm transition-all hover:shadow-md hover:-translate-y-0.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-coral"
                  >
                    <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-coral/10 text-coral">
                      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                    </div>
                    <div>
                      <p className="font-medium text-card-foreground">Manage Orders</p>
                      <p className="text-sm text-muted-foreground">View all orders</p>
                    </div>
                  </Link>

                  <Link
                    href="/seller/messages"
                    className="flex items-center gap-4 rounded-xl bg-card p-5 shadow-sm transition-all hover:shadow-md hover:-translate-y-0.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-coral"
                  >
                    <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-coral/10 text-coral">
                      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                      </svg>
                    </div>
                    <div>
                      <p className="font-medium text-card-foreground">Messages</p>
                      <p className="text-sm text-muted-foreground">Customer inquiries</p>
                    </div>
                  </Link>
                </div>
              </section>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  )
}
