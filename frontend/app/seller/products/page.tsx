"use client"
import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"

interface Product {
  id: number
  name: string
  price: string
  stock: number
  is_active: boolean
  category_name: string
  created_at: string
  image: string | null
}

export default function SellerProductsPage() {
  const router = useRouter()
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    fetchProducts()
  }, [])

  async function fetchProducts() {
    const token = localStorage.getItem("access_token")
    // WHY check token here? Seller pages are protected.
    // If no token → redirect to login before the API call even fires.
    if (!token) { router.push("/login"); return }

    try {
      const res = await fetch("http://localhost:8000/api/sellers/products/", {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.status === 401) { router.push("/login"); return }
      if (!res.ok) throw new Error("Failed to fetch products")
      const data = await res.json()
      setProducts(data)
    } catch (err) {
      setError("Could not load products. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  async function toggleActive(id: number, currentState: boolean) {
    const token = localStorage.getItem("access_token")
    // PATCH only the is_active field — not the full product
    await fetch(`http://localhost:8000/api/sellers/products/${id}/`, {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ is_active: !currentState }),
    })
    // Optimistic update — update UI immediately, no full refetch needed
    setProducts(prev =>
      prev.map(p => p.id === id ? { ...p, is_active: !currentState } : p)
    )
  }

  async function deleteProduct(id: number) {
    if (!confirm("Delete this product? This cannot be undone.")) return
    const token = localStorage.getItem("access_token")
    await fetch(`http://localhost:8000/api/sellers/products/${id}/`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    })
    setProducts(prev => prev.filter(p => p.id !== id))
  }

  // Stock badge color logic
  function stockBadge(stock: number) {
    if (stock === 0) return "bg-red-100 text-red-700"
    if (stock <= 5) return "bg-yellow-100 text-yellow-700"
    return "bg-green-100 text-green-700"
  }

  if (loading) return <div className="p-8 text-center text-muted-foreground">Loading products...</div>
  if (error) return <div className="p-8 text-center text-red-500">{error}</div>

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-foreground">My Products</h1>
          <p className="text-sm text-muted-foreground mt-1">
            {products.length} product{products.length !== 1 ? "s" : ""} total
          </p>
        </div>
        <Link
          href="/seller/products/new"
          className="flex items-center gap-2 rounded-lg bg-coral px-4 py-2 text-sm font-semibold text-white hover:bg-coral-hover transition-colors"
        >
          + Add Product
        </Link>
      </div>

      {/* Empty state */}
      {products.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-border py-16 text-center">
          <p className="text-muted-foreground mb-4">You haven't added any products yet.</p>
          <Link
            href="/seller/products/new"
            className="rounded-lg bg-coral px-4 py-2 text-sm font-semibold text-white hover:bg-coral-hover"
          >
            Add your first product
          </Link>
        </div>
      ) : (
        /* Products Table */
        <div className="overflow-hidden rounded-xl border border-border bg-card shadow-sm">
          <table className="w-full text-sm">
            <thead className="border-b border-border bg-muted/40">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Product</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Category</th>
                <th className="px-4 py-3 text-right font-medium text-muted-foreground">Price</th>
                <th className="px-4 py-3 text-center font-medium text-muted-foreground">Stock</th>
                <th className="px-4 py-3 text-center font-medium text-muted-foreground">Active</th>
                <th className="px-4 py-3 text-right font-medium text-muted-foreground">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {products.map((product) => (
                <tr key={product.id} className="hover:bg-muted/30 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      {product.image ? (
                        <img
                          src={`http://localhost:8000${product.image}`}
                          alt={product.name}
                          className="h-10 w-10 rounded-lg object-cover bg-muted"
                        />
                      ) : (
                        <div className="h-10 w-10 rounded-lg bg-muted flex items-center justify-center text-muted-foreground text-xs">
                          No img
                        </div>
                      )}
                      <span className="font-medium text-card-foreground line-clamp-1 max-w-xs">
                        {product.name}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">{product.category_name}</td>
                  <td className="px-4 py-3 text-right font-medium tabular-nums">
                    ₹{Number(product.price).toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${stockBadge(product.stock)}`}>
                      {product.stock === 0 ? "Out of stock" : `${product.stock} left`}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    {/* Toggle is_active via PATCH */}
                    <button
                      onClick={() => toggleActive(product.id, product.is_active)}
                      className={`relative inline-flex h-5 w-9 cursor-pointer rounded-full transition-colors ${
                        product.is_active ? "bg-coral" : "bg-muted"
                      }`}
                      aria-label={product.is_active ? "Deactivate product" : "Activate product"}
                    >
                      <span className={`inline-block h-4 w-4 rounded-full bg-white shadow transition-transform mt-0.5 ${
                        product.is_active ? "translate-x-4" : "translate-x-0.5"
                      }`} />
                    </button>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Link
                        href={`/seller/products/${product.id}/edit`}
                        className="rounded-md px-3 py-1.5 text-xs font-medium border border-border hover:bg-muted transition-colors"
                      >
                        Edit
                      </Link>
                      <button
                        onClick={() => deleteProduct(product.id)}
                        className="rounded-md px-3 py-1.5 text-xs font-medium text-red-600 border border-red-200 hover:bg-red-50 transition-colors"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}