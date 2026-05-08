"use client"
import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"

export default function EditProductPage() {
  const router = useRouter()
  const { id } = useParams()
  const [form, setForm] = useState({
    name: "", description: "", price: "", stock: "", category: "", is_active: true
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    async function loadProduct() {
      const token = localStorage.getItem("access_token")
      const res = await fetch(`http://localhost:8000/api/sellers/products/${id}/`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) { router.push("/seller/products"); return }
      const data = await res.json()
      setForm({
        name: data.name,
        description: data.description,
        price: data.price,
        stock: String(data.stock),
        category: String(data.category),  // category ID
        is_active: data.is_active,
      })
      setLoading(false)
    }
    loadProduct()
  }, [id])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    const token = localStorage.getItem("access_token")

    // PUT = full update (all fields required)
    const res = await fetch(`http://localhost:8000/api/sellers/products/${id}/`, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ...form,
        price: form.price,
        stock: Number(form.stock),
        category: Number(form.category),
      }),
    })

    if (res.ok) {
      router.push("/seller/products")
    } else {
      const data = await res.json()
      setError(JSON.stringify(data))
    }
    setSaving(false)
  }

  if (loading) return <div className="p-8 text-center text-muted-foreground">Loading...</div>

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-foreground mb-6">Edit Product</h1>
      {error && (
        <div className="mb-4 rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}
      <form onSubmit={handleSubmit} className="space-y-5 bg-card rounded-xl border border-border p-6 shadow-sm">
        {/* Same fields as new/page.tsx — populate with `form` state */}
        {/* ... name, description, price, stock, category inputs ... */}

        {/* Active toggle */}
        <div className="flex items-center gap-3">
          <input
            id="is_active" type="checkbox"
            checked={form.is_active}
            onChange={e => setForm(f => ({ ...f, is_active: e.target.checked }))}
            className="h-4 w-4 accent-coral"
          />
          <label htmlFor="is_active" className="text-sm font-medium text-foreground">
            Product is active (visible to buyers)
          </label>
        </div>

        <div className="flex gap-3 pt-2">
          <button type="submit" disabled={saving}
            className="flex-1 rounded-lg bg-coral py-2.5 text-sm font-semibold text-white hover:bg-coral-hover disabled:opacity-60">
            {saving ? "Saving..." : "Save Changes"}
          </button>
          <button type="button" onClick={() => router.push("/seller/products")}
            className="flex-1 rounded-lg border border-border py-2.5 text-sm font-medium hover:bg-muted">
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}