"use client";

import "@/app/globals.css";
import { Inter } from "next/font/google";
import Link from "next/link";
import { PropsWithChildren } from "react";

const inter = Inter({ subsets: ["latin", "cyrillic"] });

export default function RootLayout({ children }: PropsWithChildren) {
  return (
    <html lang="ru" className={inter.className}>
      <body>
        <header className="top-nav">
          <div className="container nav-wrapper">
            <Link href="/" className="logo">
              Shopster
            </Link>
            <nav className="nav-links">
              <Link href="/#features">Возможности</Link>
              <Link href="/products">Каталог</Link>
              <a href="http://localhost:8000/admin/" target="_blank" rel="noreferrer noopener">
                Админка
              </a>
            </nav>
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
      </body>
    </html>
  );
}
