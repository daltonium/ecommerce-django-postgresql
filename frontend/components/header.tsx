import Link from "next/link"

export function Header() {
  return (
    <header className="sticky top-0 z-50 bg-army-black text-white shadow-lg">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between gap-4">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl font-bold tracking-tight">
              Blue<span className="text-coral">Cart</span>
            </span>
          </Link>

          {/* Navigation - Desktop */}
          <nav className="hidden md:flex items-center gap-8" aria-label="Main navigation">
            <Link 
              href="/" 
              className="relative py-2 text-sm font-medium text-white/90 transition-colors hover:text-white after:absolute after:bottom-0 after:left-0 after:h-0.5 after:w-0 after:bg-coral after:transition-all hover:after:w-full focus:outline-none focus-visible:ring-2 focus-visible:ring-coral focus-visible:ring-offset-2 focus-visible:ring-offset-army-black"
            >
              Home
            </Link>
            <Link 
              href="/products" 
              className="relative py-2 text-sm font-medium text-white/90 transition-colors hover:text-white after:absolute after:bottom-0 after:left-0 after:h-0.5 after:w-0 after:bg-coral after:transition-all hover:after:w-full focus:outline-none focus-visible:ring-2 focus-visible:ring-coral focus-visible:ring-offset-2 focus-visible:ring-offset-army-black"
            >
              Products
            </Link>
            <Link 
              href="/categories" 
              className="relative py-2 text-sm font-medium text-white/90 transition-colors hover:text-white after:absolute after:bottom-0 after:left-0 after:h-0.5 after:w-0 after:bg-coral after:transition-all hover:after:w-full focus:outline-none focus-visible:ring-2 focus-visible:ring-coral focus-visible:ring-offset-2 focus-visible:ring-offset-army-black"
            >
              Categories
            </Link>
            <Link 
              href="/seller/dashboard" 
              className="relative py-2 text-sm font-medium text-white/90 transition-colors hover:text-white after:absolute after:bottom-0 after:left-0 after:h-0.5 after:w-0 after:bg-coral after:transition-all hover:after:w-full focus:outline-none focus-visible:ring-2 focus-visible:ring-coral focus-visible:ring-offset-2 focus-visible:ring-offset-army-black"
            >
              Sell
            </Link>
          </nav>

          {/* Search - Desktop */}
          <form className="hidden sm:flex relative flex-1 max-w-md mx-4" role="search">
            <label htmlFor="search" className="sr-only">Search products</label>
            <input
              id="search"
              type="search"
              placeholder="Search products..."
              className="w-full rounded-lg border-0 bg-white/10 px-4 py-2.5 pr-10 text-sm text-white placeholder:text-white/50 transition-colors focus:bg-white/15 focus:outline-none focus:ring-2 focus:ring-coral"
            />
            <button 
              type="submit" 
              className="absolute right-3 top-1/2 -translate-y-1/2 text-white/50 hover:text-white"
              aria-label="Search"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>
          </form>

          {/* Actions */}
          <div className="flex items-center gap-2">
            {/* Cart */}
            <Link 
              href="/cart" 
              className="relative flex h-10 w-10 items-center justify-center rounded-full transition-colors hover:bg-white/10 focus:outline-none focus-visible:ring-2 focus-visible:ring-coral"
              aria-label="Shopping cart, 3 items"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              <span className="absolute -right-0.5 -top-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-coral text-[10px] font-semibold text-white">
                3
              </span>
            </Link>

            {/* User */}
            <Link 
              href="/login" 
              className="flex h-10 w-10 items-center justify-center rounded-full transition-colors hover:bg-white/10 focus:outline-none focus-visible:ring-2 focus-visible:ring-coral"
              aria-label="Account"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </Link>

            {/* Mobile Menu Toggle */}
            <button 
              type="button"
              className="flex md:hidden h-10 w-10 items-center justify-center rounded-full transition-colors hover:bg-white/10 focus:outline-none focus-visible:ring-2 focus-visible:ring-coral"
              aria-label="Open menu"
              aria-expanded="false"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}
