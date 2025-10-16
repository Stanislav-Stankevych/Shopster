import { fetchProducts } from "@/lib/api";
import { ProductCard } from "@/components/ProductCard";
import { AlgoliaSearch } from "@/components/AlgoliaSearch";

export default async function ProductsPage() {
  const products = await fetchProducts(12);

  return (
    <section className="section">
      <div className="container">
        <div className="section-header">
          <h1>Каталог</h1>
          <p>Синхронизируется из Django. Используйте поиск Algolia для мгновенной фильтрации.</p>
        </div>
        <div className="product-grid">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
        <AlgoliaSearch />
      </div>
    </section>
  );
}
