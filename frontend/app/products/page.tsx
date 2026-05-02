import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { ProductCard } from "@/components/product-card"
import Link from "next/link"

// Sample product data
const products = [
  {
    id: 1,
    name: "Wireless Bluetooth Headphones with Active Noise Cancellation",
    price: 2499,
    originalPrice: 3999,
    rating: 4.5,
    reviewCount: 128,
    imageUrl: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop",
    category: "Electronics",
  },
  {
    id: 2,
    name: "Premium Cotton Casual T-Shirt",
    price: 799,
    rating: 4.2,
    reviewCount: 89,
    imageUrl: "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop",
    category: "Fashion",
  },
  {
    id: 3,
    name: "Smart Watch with Health Tracking",
    price: 4999,
    originalPrice: 6999,
    rating: 4.7,
    reviewCount: 256,
    imageUrl: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop",
    category: "Electronics",
  },
  {
    id: 4,
    name: "Leather Crossbody Bag",
    price: 1899,
    rating: 4.4,
    reviewCount: 67,
    imageUrl: "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=400&h=400&fit=crop",
    category: "Fashion",
  },
  {
    id: 5,
    name: "Ceramic Plant Pot Set",
    price: 1299,
    originalPrice: 1599,
    rating: 4.6,
    reviewCount: 43,
    imageUrl: "https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=400&h=400&fit=crop",
    category: "Home & Garden",
  },
  {
    id: 6,
    name: "Professional Running Shoes",
    price: 3499,
    rating: 4.8,
    reviewCount: 189,
    imageUrl: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop",
    category: "Sports",
  },
  {
    id: 7,
    name: "Organic Skincare Gift Set",
    price: 1999,
    originalPrice: 2499,
    rating: 4.3,
    reviewCount: 112,
    imageUrl: "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400&h=400&fit=crop",
    category: "Beauty",
  },
  {
    id: 8,
    name: "Minimalist Desk Lamp",
    price: 1599,
    rating: 4.5,
    reviewCount: 78,
    imageUrl: "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400&h=400&fit=crop",
    category: "Home & Garden",
  },
  {
    id: 9,
    name: "Portable Bluetooth Speaker",
    price: 1999,
    originalPrice: 2499,
    rating: 4.4,
    reviewCount: 156,
    imageUrl: "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400&h=400&fit=crop",
    category: "Electronics",
  },
  {
    id: 10,
    name: "Yoga Mat Premium",
    price: 999,
    rating: 4.6,
    reviewCount: 203,
    imageUrl: "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=400&h=400&fit=crop",
    category: "Sports",
  },
  {
    id: 11,
    name: "Classic Denim Jacket",
    price: 2799,
    rating: 4.5,
    reviewCount: 91,
    imageUrl: "https://images.unsplash.com/photo-1495105787522-5334e3ffa0ef?w=400&h=400&fit=crop",
    category: "Fashion",
  },
  {
    id: 12,
    name: "Stainless Steel Water Bottle",
    price: 599,
    rating: 4.7,
    reviewCount: 312,
    imageUrl: "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=400&h=400&fit=crop",
    category: "Sports",
  },
]

const categories = ["All", "Electronics", "Fashion", "Home & Garden", "Sports", "Beauty", "Books"]

export default function ProductsPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      
      <main className="flex-1 py-8 sm:py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          {/* Breadcrumb */}
          <nav className="mb-6 flex items-center gap-2 text-sm text-muted-foreground" aria-label="Breadcrumb">
            <Link href="/" className="hover:text-coral transition-colors">Home</Link>
            <span aria-hidden="true">→</span>
            <span className="text-foreground" aria-current="page">Products</span>
          </nav>

          {/* Header */}
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-8">
            <h1 className="text-2xl font-bold text-foreground sm:text-3xl">
              All Products
            </h1>
            <p className="text-sm text-muted-foreground">
              Showing {products.length} products
            </p>
          </div>

          {/* Filters */}
          <div className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            {/* Category Tabs */}
            <div className="flex flex-wrap gap-2" role="tablist" aria-label="Product categories">
              {categories.map((category, index) => (
                <button
                  key={category}
                  type="button"
                  role="tab"
                  aria-selected={index === 0}
                  className={`rounded-full px-4 py-2 text-sm font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-coral focus-visible:ring-offset-2 ${
                    index === 0
                      ? "bg-coral text-white"
                      : "bg-card text-card-foreground hover:bg-muted"
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>

            {/* Sort */}
            <div className="flex items-center gap-3">
              <label htmlFor="sort" className="text-sm text-muted-foreground whitespace-nowrap">
                Sort by:
              </label>
              <select
                id="sort"
                className="rounded-lg border-2 border-border bg-card px-3 py-2 text-sm text-card-foreground focus:border-coral focus:outline-none focus:ring-2 focus:ring-coral/20"
              >
                <option value="relevance">Relevance</option>
                <option value="price-low">Price: Low to High</option>
                <option value="price-high">Price: High to Low</option>
                <option value="rating">Customer Rating</option>
                <option value="newest">Newest First</option>
              </select>
            </div>
          </div>

          {/* Product Grid */}
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 sm:gap-6">
            {products.map((product) => (
              <ProductCard key={product.id} {...product} />
            ))}
          </div>

          {/* Pagination */}
          <nav className="mt-12 flex items-center justify-center gap-2" aria-label="Pagination">
            <button
              type="button"
              disabled
              className="flex h-10 w-10 items-center justify-center rounded-lg border border-border bg-card text-muted-foreground transition-colors hover:border-coral hover:text-coral disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus-visible:ring-2 focus-visible:ring-coral"
              aria-label="Previous page"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <button
              type="button"
              className="flex h-10 w-10 items-center justify-center rounded-lg bg-coral text-white font-medium focus:outline-none focus-visible:ring-2 focus-visible:ring-coral focus-visible:ring-offset-2"
              aria-current="page"
            >
              1
            </button>
            <button
              type="button"
              className="flex h-10 w-10 items-center justify-center rounded-lg border border-border bg-card text-card-foreground font-medium transition-colors hover:border-coral hover:text-coral focus:outline-none focus-visible:ring-2 focus-visible:ring-coral"
            >
              2
            </button>
            <button
              type="button"
              className="flex h-10 w-10 items-center justify-center rounded-lg border border-border bg-card text-card-foreground font-medium transition-colors hover:border-coral hover:text-coral focus:outline-none focus-visible:ring-2 focus-visible:ring-coral"
            >
              3
            </button>
            <button
              type="button"
              className="flex h-10 w-10 items-center justify-center rounded-lg border border-border bg-card text-card-foreground transition-colors hover:border-coral hover:text-coral focus:outline-none focus-visible:ring-2 focus-visible:ring-coral"
              aria-label="Next page"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </nav>
        </div>
      </main>

      <Footer />
    </div>
  )
}
