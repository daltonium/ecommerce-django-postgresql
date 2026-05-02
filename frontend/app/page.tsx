import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { HeroSection } from "@/components/hero-section"
import { ProductCard } from "@/components/product-card"
import { CategoryCard, ElectronicsIcon, FashionIcon, HomeIcon, SportsIcon, BooksIcon, BeautyIcon } from "@/components/category-card"
import Link from "next/link"

// Sample product data
const featuredProducts = [
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
]

const categories = [
  { name: "Electronics", icon: <ElectronicsIcon />, href: "/categories/electronics" },
  { name: "Fashion", icon: <FashionIcon />, href: "/categories/fashion" },
  { name: "Home & Garden", icon: <HomeIcon />, href: "/categories/home" },
  { name: "Sports", icon: <SportsIcon />, href: "/categories/sports" },
  { name: "Books", icon: <BooksIcon />, href: "/categories/books" },
  { name: "Beauty", icon: <BeautyIcon />, href: "/categories/beauty" },
]

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      
      <main className="flex-1">
        {/* Hero Section */}
        <HeroSection />

        {/* Categories Section */}
        <section className="py-12 sm:py-16" aria-labelledby="categories-heading">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between mb-8">
              <h2 id="categories-heading" className="text-2xl font-bold text-foreground relative after:absolute after:-bottom-2 after:left-0 after:h-0.5 after:w-12 after:bg-coral">
                Shop by Category
              </h2>
              <Link 
                href="/categories" 
                className="text-sm font-medium text-coral hover:text-coral-hover transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-coral focus-visible:ring-offset-2"
              >
                View All →
              </Link>
            </div>
            
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
              {categories.map((category) => (
                <CategoryCard
                  key={category.name}
                  name={category.name}
                  icon={category.icon}
                  href={category.href}
                />
              ))}
            </div>
          </div>
        </section>

        {/* Featured Products Section */}
        <section className="py-12 sm:py-16 bg-muted/30" aria-labelledby="featured-heading">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between mb-8">
              <h2 id="featured-heading" className="text-2xl font-bold text-foreground relative after:absolute after:-bottom-2 after:left-0 after:h-0.5 after:w-12 after:bg-coral">
                Featured Products
              </h2>
              <Link 
                href="/products" 
                className="text-sm font-medium text-coral hover:text-coral-hover transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-coral focus-visible:ring-offset-2"
              >
                View All →
              </Link>
            </div>
            
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 sm:gap-6">
              {featuredProducts.map((product) => (
                <ProductCard key={product.id} {...product} />
              ))}
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-12 sm:py-16" aria-labelledby="features-heading">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <h2 id="features-heading" className="sr-only">Why Choose BlueCart</h2>
            <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
              {/* Feature 1 */}
              <div className="flex flex-col items-center text-center p-6 rounded-xl bg-card">
                <div className="flex h-14 w-14 items-center justify-center rounded-full bg-coral/10 text-coral mb-4">
                  <svg className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path d="M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-card-foreground mb-2">Free Shipping</h3>
                <p className="text-sm text-muted-foreground">Free shipping on orders over ₹999</p>
              </div>

              {/* Feature 2 */}
              <div className="flex flex-col items-center text-center p-6 rounded-xl bg-card">
                <div className="flex h-14 w-14 items-center justify-center rounded-full bg-coral/10 text-coral mb-4">
                  <svg className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-card-foreground mb-2">Secure Payments</h3>
                <p className="text-sm text-muted-foreground">100% secure payment via Razorpay</p>
              </div>

              {/* Feature 3 */}
              <div className="flex flex-col items-center text-center p-6 rounded-xl bg-card">
                <div className="flex h-14 w-14 items-center justify-center rounded-full bg-coral/10 text-coral mb-4">
                  <svg className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-card-foreground mb-2">Easy Returns</h3>
                <p className="text-sm text-muted-foreground">7-day hassle-free return policy</p>
              </div>

              {/* Feature 4 */}
              <div className="flex flex-col items-center text-center p-6 rounded-xl bg-card">
                <div className="flex h-14 w-14 items-center justify-center rounded-full bg-coral/10 text-coral mb-4">
                  <svg className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-card-foreground mb-2">24/7 Support</h3>
                <p className="text-sm text-muted-foreground">Round-the-clock customer support</p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-12 sm:py-16 bg-army-black" aria-labelledby="cta-heading">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
            <h2 id="cta-heading" className="text-2xl sm:text-3xl font-bold text-white mb-4 text-balance">
              Ready to Start <span className="text-coral">Selling</span>?
            </h2>
            <p className="text-white/70 max-w-2xl mx-auto mb-8 text-pretty">
              Join thousands of sellers on BlueCart. List your products, reach millions of customers, and grow your business.
            </p>
            <Link
              href="/seller/register"
              className="inline-flex items-center justify-center rounded-lg bg-coral px-8 py-3.5 text-base font-semibold text-white transition-colors hover:bg-coral-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-army-black"
            >
              Become a Seller
            </Link>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  )
}
