import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import Link from "next/link"

// Sample product data
const product = {
  id: 1,
  name: "Wireless Bluetooth Headphones with Active Noise Cancellation",
  price: 2499,
  originalPrice: 3999,
  rating: 4.5,
  reviewCount: 128,
  category: "Electronics",
  description: "Experience premium sound quality with our wireless Bluetooth headphones featuring active noise cancellation technology. Perfect for music lovers, these headphones offer crystal-clear audio, comfortable over-ear design, and up to 30 hours of battery life. The built-in microphone ensures clear calls, while the foldable design makes them easy to carry anywhere.",
  features: [
    "Active Noise Cancellation (ANC)",
    "30 hours battery life",
    "Bluetooth 5.0 connectivity",
    "Built-in microphone for calls",
    "Comfortable memory foam ear cushions",
    "Foldable and portable design",
    "Touch controls on ear cups",
    "Quick charge - 10 min for 3 hours playback",
  ],
  images: [
    "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&h=600&fit=crop",
    "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=600&h=600&fit=crop",
    "https://images.unsplash.com/photo-1487215078519-e21cc028cb29?w=600&h=600&fit=crop",
    "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=600&h=600&fit=crop",
  ],
  seller: "TechGadgets Store",
  inStock: true,
}

const reviews = [
  {
    id: 1,
    author: "Rahul K.",
    rating: 5,
    date: "April 28, 2026",
    title: "Amazing sound quality!",
    content: "These headphones exceeded my expectations. The noise cancellation is superb, and the battery lasts forever. Highly recommended for anyone who loves music.",
  },
  {
    id: 2,
    author: "Priya M.",
    rating: 4,
    date: "April 25, 2026",
    title: "Great product with minor issues",
    content: "Sound quality is excellent and very comfortable to wear. The only issue is the touch controls are a bit sensitive. Overall a great purchase.",
  },
  {
    id: 3,
    author: "Amit S.",
    rating: 5,
    date: "April 20, 2026",
    title: "Best headphones I've owned",
    content: "Perfect for work from home calls and listening to music. The ANC blocks out all distractions. Worth every rupee!",
  },
]

export default function ProductDetailPage() {
  const discount = Math.round(((product.originalPrice - product.price) / product.originalPrice) * 100)

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      
      <main className="flex-1 py-8 sm:py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          {/* Breadcrumb */}
          <nav className="mb-6 flex items-center gap-2 text-sm text-muted-foreground" aria-label="Breadcrumb">
            <Link href="/" className="hover:text-coral transition-colors">Home</Link>
            <span aria-hidden="true">→</span>
            <Link href="/products" className="hover:text-coral transition-colors">Products</Link>
            <span aria-hidden="true">→</span>
            <span className="text-foreground line-clamp-1" aria-current="page">{product.name}</span>
          </nav>

          {/* Product Section */}
          <div className="grid gap-8 lg:grid-cols-2 lg:gap-12">
            {/* Gallery */}
            <div className="space-y-4">
              {/* Main Image */}
              <div className="aspect-square overflow-hidden rounded-2xl bg-muted">
                <img
                  src={product.images[0]}
                  alt={product.name}
                  className="h-full w-full object-cover"
                />
              </div>
              {/* Thumbnails */}
              <div className="flex gap-3">
                {product.images.map((image, index) => (
                  <button
                    key={index}
                    type="button"
                    className={`aspect-square w-20 overflow-hidden rounded-lg border-2 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-coral ${
                      index === 0 ? "border-coral" : "border-transparent hover:border-coral/50"
                    }`}
                  >
                    <img src={image} alt={`${product.name} view ${index + 1}`} className="h-full w-full object-cover" />
                  </button>
                ))}
              </div>
            </div>

            {/* Product Info */}
            <div className="space-y-6">
              {/* Category */}
              <p className="text-sm font-medium uppercase tracking-wider text-coral">
                {product.category}
              </p>

              {/* Title */}
              <h1 className="text-2xl font-bold text-foreground sm:text-3xl text-balance">
                {product.name}
              </h1>

              {/* Rating */}
              <div className="flex items-center gap-3">
                <div className="flex text-coral" aria-label={`Rating: ${product.rating} out of 5 stars`}>
                  {[...Array(5)].map((_, i) => (
                    <svg
                      key={i}
                      className={`h-5 w-5 ${i < Math.floor(product.rating) ? 'fill-current' : 'fill-muted stroke-coral'}`}
                      viewBox="0 0 20 20"
                    >
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                </div>
                <span className="text-sm text-muted-foreground">
                  {product.rating} ({product.reviewCount} reviews)
                </span>
              </div>

              {/* Price */}
              <div className="flex items-baseline gap-4">
                <span className="text-3xl font-bold text-foreground">
                  ₹{product.price.toLocaleString()}
                </span>
                {product.originalPrice && (
                  <>
                    <span className="text-xl text-muted-foreground line-through">
                      ₹{product.originalPrice.toLocaleString()}
                    </span>
                    <span className="rounded-full bg-coral/10 px-3 py-1 text-sm font-semibold text-coral">
                      {discount}% OFF
                    </span>
                  </>
                )}
              </div>

              {/* Description */}
              <p className="text-muted-foreground leading-relaxed text-pretty">
                {product.description}
              </p>

              {/* Seller */}
              <div className="flex items-center gap-2 text-sm">
                <span className="text-muted-foreground">Sold by:</span>
                <Link href="#" className="font-medium text-coral hover:underline">
                  {product.seller}
                </Link>
              </div>

              {/* Stock Status */}
              <div className="flex items-center gap-2">
                <span className={`inline-flex h-2.5 w-2.5 rounded-full ${product.inStock ? 'bg-green-500' : 'bg-red-500'}`}></span>
                <span className={`text-sm font-medium ${product.inStock ? 'text-green-600' : 'text-red-600'}`}>
                  {product.inStock ? 'In Stock' : 'Out of Stock'}
                </span>
              </div>

              {/* Actions */}
              <div className="flex flex-col gap-3 sm:flex-row pt-2">
                <button
                  type="button"
                  className="flex-1 rounded-lg bg-coral py-3.5 text-base font-semibold text-white transition-colors hover:bg-coral-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-coral focus-visible:ring-offset-2"
                >
                  Add to Cart
                </button>
                <button
                  type="button"
                  className="flex-1 rounded-lg border-2 border-army-black bg-army-black py-3.5 text-base font-semibold text-white transition-colors hover:bg-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-army-black focus-visible:ring-offset-2"
                >
                  Buy Now
                </button>
              </div>

              {/* Features */}
              <div className="border-t border-border pt-6">
                <h2 className="text-lg font-semibold text-foreground mb-4">Key Features</h2>
                <ul className="grid gap-2 sm:grid-cols-2">
                  {product.features.map((feature, index) => (
                    <li key={index} className="flex items-start gap-2 text-sm text-muted-foreground">
                      <svg className="h-5 w-5 shrink-0 text-coral" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Reviews Section */}
          <section className="mt-16 border-t border-border pt-12" aria-labelledby="reviews-heading">
            <h2 id="reviews-heading" className="text-2xl font-bold text-foreground mb-8">
              Customer Reviews
            </h2>

            <div className="grid gap-8 lg:grid-cols-3">
              {/* Rating Summary */}
              <div className="rounded-xl bg-card p-6 h-fit">
                <div className="text-center">
                  <p className="text-5xl font-bold text-foreground">{product.rating}</p>
                  <div className="flex justify-center mt-2 text-coral">
                    {[...Array(5)].map((_, i) => (
                      <svg
                        key={i}
                        className={`h-5 w-5 ${i < Math.floor(product.rating) ? 'fill-current' : 'fill-muted stroke-coral'}`}
                        viewBox="0 0 20 20"
                      >
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                    ))}
                  </div>
                  <p className="mt-2 text-sm text-muted-foreground">
                    Based on {product.reviewCount} reviews
                  </p>
                </div>

                <div className="mt-6">
                  <button
                    type="button"
                    className="w-full rounded-lg bg-army-black py-3 text-sm font-semibold text-white transition-colors hover:bg-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-army-black focus-visible:ring-offset-2"
                  >
                    Write a Review
                  </button>
                </div>
              </div>

              {/* Reviews List */}
              <div className="lg:col-span-2 space-y-6">
                {reviews.map((review) => (
                  <article key={review.id} className="rounded-xl bg-card p-6">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <div className="flex text-coral">
                          {[...Array(5)].map((_, i) => (
                            <svg
                              key={i}
                              className={`h-4 w-4 ${i < review.rating ? 'fill-current' : 'fill-muted stroke-coral'}`}
                              viewBox="0 0 20 20"
                            >
                              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                            </svg>
                          ))}
                        </div>
                        <h3 className="mt-2 font-semibold text-card-foreground">{review.title}</h3>
                      </div>
                      <time className="text-sm text-muted-foreground whitespace-nowrap">{review.date}</time>
                    </div>
                    <p className="mt-3 text-sm text-muted-foreground leading-relaxed">{review.content}</p>
                    <p className="mt-4 text-sm font-medium text-card-foreground">— {review.author}</p>
                  </article>
                ))}

                <button
                  type="button"
                  className="w-full rounded-lg border-2 border-border bg-transparent py-3 text-base font-medium text-card-foreground transition-colors hover:bg-muted focus:outline-none focus-visible:ring-2 focus-visible:ring-coral focus-visible:ring-offset-2"
                >
                  Load More Reviews
                </button>
              </div>
            </div>
          </section>
        </div>
      </main>

      <Footer />
    </div>
  )
}
