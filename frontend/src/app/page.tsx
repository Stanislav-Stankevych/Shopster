import { fetchProducts } from "@/lib/api";
import { ProductCard } from "@/components/ProductCard";
import Link from "next/link";
import { FRONTEND_ORIGIN } from "@/lib/config";

export default async function HomePage() {
  const products = await fetchProducts(6);

  return (
    <>
      <section className="hero">
        <div className="container hero-grid">
          <div className="hero-card">
            <span className="highlight">New headless storefront</span>
            <h1>Launch a modern commerce stack with Next.js and Algolia search</h1>
            <p className="lead">
              The catalog is powered by Django REST API, the search is backed by Algolia. Extend the platform with
              payments, analytics, and custom experiences when you are ready.
            </p>
            <div className="cta-buttons">
              <a className="btn btn-primary" href={`${FRONTEND_ORIGIN}/products`}>Explore catalog</a>
              <a className="btn btn-outline" href="http://localhost:8000/admin/" target="_blank" rel="noreferrer noopener">
                Manage products
              </a>
            </div>
          </div>
          <div className="highlight-grid">
            <div className="highlight">Automatic sync from Django to Algolia</div>
            <div className="highlight">Instant results with category facets and relevance tuning</div>
            <div className="highlight">Ready for SSR/ISR and static export</div>
          </div>
        </div>
      </section>

      <section className="section" id="features">
        <div className="container">
          <div className="section-header">
            <h2>What is included</h2>
            <p>Django API, Algolia indexing pipeline, Next.js frontend and Dockerised infrastructure.</p>
          </div>
          <div className="feature-grid">
            <div className="feature-card">
              <h3>Catalog & orders</h3>
              <p>Manage products, categories, carts and orders from the Django admin or via API endpoints.</p>
            </div>
            <div className="feature-card">
              <h3>Algolia search</h3>
              <p>Instant search with facets, typo tolerance and configurable ranking.</p>
            </div>
            <div className="feature-card">
              <h3>Next.js storefront</h3>
              <p>Modern UX with server components, ready for static generation or server rendering.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="section-header">
            <h2>Featured products</h2>
            <p>Data comes straight from the Django API. Adjust the selection to match your merchandising strategy.</p>
          </div>
          <div className="product-grid">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </div>
      </section>
    </>
  );
}






