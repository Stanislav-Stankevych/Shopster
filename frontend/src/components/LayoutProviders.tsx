"use client";

import { PropsWithChildren } from "react";
import Link from "next/link";
import { FRONTEND_ORIGIN } from "@/lib/config";

import { AccountMenu } from "@/components/AccountMenu";
import { AlgoliaSearch } from "@/components/AlgoliaSearch";
import { CartBadge } from "@/components/CartBadge";
import { AdminNavLink } from "@/components/AdminNavLink";
import { AuthSessionProvider } from "@/components/SessionProvider";

export function LayoutProviders({ children }: PropsWithChildren) {
  return (
    <AuthSessionProvider>
      <header className="top-nav">
        <div className="container nav-wrapper">
          <Link href="/" className="logo">
            Shopster
          </Link>
          <div className="nav-right">
            <AlgoliaSearch />
            <nav className="nav-links">
              <Link href="/#features">Features</Link>
              <a href={`${FRONTEND_ORIGIN}/products`}>Catalog</a>
              <AdminNavLink />
            </nav>
            <CartBadge />
            <AccountMenu />
          </div>
        </div>
      </header>
      <main>{children}</main>
      <footer className="footer">
        <div className="container footer-wrapper">
          <p>&copy; {new Date().getFullYear()} Shopster</p>
          <div className="footer-links">
            <a href="mailto:shop@example.com">shop@example.com</a>
            <a href="tel:+79991234567">+7 (999) 123-45-67</a>
          </div>
        </div>
      </footer>
    </AuthSessionProvider>
  );
}





