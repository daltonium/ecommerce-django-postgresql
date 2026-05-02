"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import Link from "next/link"

export default function LoginPage() {
  const router = useRouter()
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setLoading(true)
    setError("")

    const form = e.currentTarget
    const email = (form.elements.namedItem("email") as HTMLInputElement).value
    const password = (form.elements.namedItem("password") as HTMLInputElement).value

    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    })

    const data = await res.json()

    if (res.ok) {
      localStorage.setItem("access_token", data.access)
      localStorage.setItem("refresh_token", data.refresh)
      router.push("/products")
    } else {
      setError("Invalid email or password. Please try again.")
    }

    setLoading(false)
  }

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex flex-1 items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          <div className="rounded-2xl bg-card p-8 shadow-lg sm:p-10">

            <div className="text-center mb-8">
              <Link href="/" className="inline-block mb-4">
                <span className="text-2xl font-bold tracking-tight text-foreground">
                  Blue<span className="text-coral">Cart</span>
                </span>
              </Link>
              <h1 className="text-2xl font-bold text-card-foreground">Welcome back</h1>
              <p className="mt-2 text-sm text-muted-foreground">
                Sign in to your account to continue shopping
              </p>
            </div>

            {error && (
              <div className="mb-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-600 border border-red-200">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-card-foreground mb-2">
                  Email address
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  autoComplete="email"
                  required
                  className="w-full rounded-lg border-2 border-border bg-background px-4 py-3 text-foreground placeholder:text-muted-foreground transition-colors focus:border-coral focus:outline-none focus:ring-2 focus:ring-coral/20"
                  placeholder="you@example.com"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label htmlFor="password" className="block text-sm font-medium text-card-foreground">
                    Password
                  </label>
                  <Link href="/forgot-password" className="text-sm font-medium text-coral hover:text-coral-hover transition-colors">
                    Forgot password?
                  </Link>
                </div>
                <input
                  type="password"
                  id="password"
                  name="password"
                  autoComplete="current-password"
                  required
                  className="w-full rounded-lg border-2 border-border bg-background px-4 py-3 text-foreground placeholder:text-muted-foreground transition-colors focus:border-coral focus:outline-none focus:ring-2 focus:ring-coral/20"
                  placeholder="Enter your password"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-lg bg-coral py-3 text-base font-semibold text-white transition-colors hover:bg-coral-hover focus:outline-none disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {loading ? "Signing in..." : "Sign in"}
              </button>
            </form>

            <p className="mt-8 text-center text-sm text-muted-foreground">
              Don&apos;t have an account?{" "}
              <Link href="/register" className="font-semibold text-coral hover:text-coral-hover transition-colors">
                Create an account
              </Link>
            </p>

          </div>
        </div>
      </main>
      <Footer />
    </div>
  )
}