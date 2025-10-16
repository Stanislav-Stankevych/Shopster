
import { fetchProducts } from "@/lib/api";
import { ProductCard } from "@/components/ProductCard";

export default async function ProductsPage() {
  const products = await fetchProducts(12);

  return (
    <section className="section">
      <div className="container">
        <div className="section-header">
          <h1>Каталог</h1>
          <p>Синхронизируется из Django. Используйте поиск в шапке сайта для мгновенной фильтрации.</p>
        </div>
        <div className="product-grid">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      </div>
    </section>
  );
}

