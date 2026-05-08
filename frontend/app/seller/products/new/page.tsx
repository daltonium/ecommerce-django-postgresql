"use client"
import { useState } from "react"
import { useRouter } from "next/navigation"

export default function NewProductPage() {
  const router = useRouter()
  const [form, setForm] = useState({
    name: "", description: "", price: "", stock: "", category: "", is_active: true
  })
  const [image, setImage] = useState<File | null>(null)
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError("")

    const token = localStorage.getItem("access_token")

    // WHY FormData and not JSON?
    // Product has an image field (file upload).
    // Files cannot be sent as JSON — they must use multipart/form-data.
    const body = new FormData()
    Object.entries(form).forEach(([k, v]) => body.append(k, String(v)))
    if (image) body.append("image", image)

    try {
      const res = await fetch("http://localhost:8000/api/sellers/products/", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        // DO NOT set Content-Type manually — browser sets it with boundary for FormData
        body,
      })
      if (!res.ok) {
        const data = await res.json()
        setError(JSON.stringify(data))
        return
      }
      router.push("/seller/products")
    } catch {
      setError("Something went wrong. Try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-foreground mb-6">Add New Product</h1>

      {error && (
        <div className="mb-4 rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5 bg-card rounded-xl border border-border p-6 shadow-sm">
        {/* Name */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-1" htmlFor="name">
            Product Name
          </label>
          <input
            id="name" required
            className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-coral"
            value={form.name}
            onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
          />
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-1" htmlFor="description">
            Description
          </label>
          <textarea
            id="description" rows={4} required
            className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-coral"
            value={form.description}
            onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
          />
        </div>

        {/* Price + Stock */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-1" htmlFor="price">
              Price (₹)
            </label>
            <input
              id="price" type="number" min="0" step="0.01" required
              className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-coral"
              value={form.price}
              onChange={e => setForm(f => ({ ...f, price: e.target.value }))}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-foreground mb-1" htmlFor="stock">
              Stock
            </label>
            <input
              id="stock" type="number" min="0" required
              className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-coral"
              value={form.stock}
              onChange={e => setForm(f => ({ ...f, stock: e.target.value }))}
            />
          </div>
        </div>

        {/* Category ID */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-1" htmlFor="category">
            Category ID
          </label>
          <input
            id="category" type="number" required
            placeholder="e.g. 1 (Electronics)"
            className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-coral"
            value={form.category}
            onChange={e => setForm(f => ({ ...f, category: e.target.value }))}
          />
          <p className="text-xs text-muted-foreground mt-1">
            Tip: replace this with a &lt;select&gt; fetching from <code>/api/products/categories/</code>
          </p>
        </div>

        {/* Image upload */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-1" htmlFor="image">
            Product Image (optional)
          </label>
          <input
            id="image" type="file" accept="image/*"
            className="w-full text-sm text-muted-foreground file:mr-3 file:rounded-lg file:border-0 file:bg-muted file:px-3 file:py-1.5 file:text-sm file:font-medium"
            onChange={e => setImage(e.target.files?.[0] ?? null)}
          />
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-2">
          <button
            type="submit" disabled={loading}
            className="flex-1 rounded-lg bg-coral py-2.5 text-sm font-semibold text-white hover:bg-coral-hover transition-colors disabled:opacity-60"
          >
            {loading ? "Adding..." : "Add Product"}
          </button>
          <button
            type="button"
            onClick={() => router.push("/seller/products")}
            className="flex-1 rounded-lg border border-border py-2.5 text-sm font-medium hover:bg-muted transition-colors"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}