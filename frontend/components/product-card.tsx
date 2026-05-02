import Link from "next/link"

interface ProductCardProps {
  id: number
  name: string
  price: number
  originalPrice?: number
  rating: number
  reviewCount: number
  imageUrl: string
  category: string
}

export function ProductCard({
  id,
  name,
  price,
  originalPrice,
  rating,
  reviewCount,
  imageUrl,
  category,
}: ProductCardProps) {
  return (
    <article className="group overflow-hidden rounded-xl bg-card shadow-sm transition-all duration-300 hover:shadow-lg hover:-translate-y-1">
      <Link href={`/products/${id}`} className="block focus:outline-none focus-visible:ring-2 focus-visible:ring-coral focus-visible:ring-offset-2">
        {/* Image */}
        <div className="relative aspect-square overflow-hidden bg-muted">
          <img
            src={imageUrl}
            alt={name}
            className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
          />
          {originalPrice && (
            <span className="absolute left-3 top-3 rounded-full bg-coral px-2.5 py-1 text-xs font-semibold text-white">
              Sale
            </span>
          )}
        </div>

        {/* Content */}
        <div className="p-4">
          <p className="text-xs font-medium uppercase tracking-wide text-coral">
            {category}
          </p>
          <h3 className="mt-1 text-sm font-medium text-card-foreground line-clamp-2 text-pretty">
            {name}
          </h3>
          
          {/* Rating */}
          <div className="mt-2 flex items-center gap-1" aria-label={`Rating: ${rating} out of 5 stars, ${reviewCount} reviews`}>
            <div className="flex text-coral" aria-hidden="true">
              {[...Array(5)].map((_, i) => (
                <svg
                  key={i}
                  className={`h-3.5 w-3.5 ${i < Math.floor(rating) ? 'fill-current' : 'fill-muted stroke-coral'}`}
                  viewBox="0 0 20 20"
                >
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              ))}
            </div>
            <span className="text-xs text-muted-foreground">({reviewCount})</span>
          </div>

          {/* Price */}
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-lg font-bold text-card-foreground">
              ₹{price.toLocaleString()}
            </span>
            {originalPrice && (
              <span className="text-sm text-muted-foreground line-through">
                ₹{originalPrice.toLocaleString()}
              </span>
            )}
          </div>
        </div>
      </Link>

      {/* Add to Cart Button */}
      <div className="px-4 pb-4">
        <button
          type="button"
          className="w-full rounded-lg bg-army-black py-2.5 text-sm font-medium text-white transition-colors hover:bg-coral focus:outline-none focus-visible:ring-2 focus-visible:ring-coral focus-visible:ring-offset-2"
        >
          Add to Cart
        </button>
      </div>
    </article>
  )
}
