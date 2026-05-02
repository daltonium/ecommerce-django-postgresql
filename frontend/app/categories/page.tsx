"use client"

import { useState, useEffect } from "react"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import Link from "next/link"

interface Category {
  id: number
  name: string
  slug: string
  description: string
  product_count: number
}

export default function CategoriesPage() {
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    async function fetchCategories() {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/categories/`)
        const data = await res.json()
        setCategories(data)
      } catch (err) {
        setError("Failed to load categories.")
      } finally {
        setLoading(false)
      }
    }

    fetchCategories()
  }, [])

  return (
    <div className="flex min-h-screen flex-col">
      <Header />

      <main className="flex-1 py-8 sm:py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">

          <h1 className="text-2xl font-bold text-foreground sm:text-3xl mb-8">
            All Categories
          </h1>

          {/* Loading */}
          {loading && (
            <div className="flex justify-center py-16">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-coral border-t-transparent" />
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-600 border border-red-200">
              {error}
            </div>
          )}

          {/* Categories Grid */}
          {!loading && !error && categories.length > 0 && (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {categories.map((category) => (
                <Link
                  key={category.id}
                  href={`/products?category=${category.slug}`}
                  className="rounded-xl bg-card p-6 shadow-sm hover:shadow-md transition-shadow border border-border"
                >
                  <h2 className="text-lg font-semibold text-card-foreground">
                    {category.name}
                  </h2>
                  {category.description && (
                    <p className="mt-1 text-sm text-muted-foreground line-clamp-2">
                      {category.description}
                    </p>
                  )}
                  <p className="mt-3 text-sm font-medium text-coral">
                    {category.product_count} products →
                  </p>
                </Link>
              ))}
            </div>
          )}

          {/* Empty */}
          {!loading && !error && categories.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <p className="text-muted-foreground">No categories found.</p>
            </div>
          )}

        </div>
      </main>

      <Footer />
    </div>
  )
}