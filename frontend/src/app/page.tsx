import { fetchProducts } from "@/lib/api";
import { ProductCard } from "@/components/ProductCard";
import Link from "next/link";

export default async function HomePage() {
  const products = await fetchProducts(6);

  return (
    <>
      <section className="hero">
        <div className="container hero-grid">
          <div className="hero-card">
            <span className="highlight">Новый витринный фронтенд</span>
            <h1>Лёгкая витрина на Next.js с Algolia-поиском</h1>
            <p className="lead">
              Каталог синхронизируется из Django, а поиск работает на сверхскоростном движке Algolia. Развивайте магазин
              без боли.
            </p>
            <div className="cta-buttons">
              <Link className="btn btn-primary" href="/products">
                Перейти в каталог
              </Link>
              <a className="btn btn-outline" href="http://localhost:8000/admin/" target="_blank" rel="noreferrer noopener">
                Управление товарами
              </a>
            </div>
          </div>
          <div className="highlight-grid">
            <div className="highlight">Автообновление товаров → Algolia</div>
            <div className="highlight">Мгновенный поиск сниппетов и категорий</div>
            <div className="highlight">Готовность к SSR/ISR и масштабированию</div>
          </div>
        </div>
      </section>

      <section className="section" id="features">
        <div className="container">
          <div className="section-header">
            <h2>Что уже реализовано</h2>
            <p>API на Django, Algolia-индексация, Next.js-frontend, готовый Docker-стек.</p>
          </div>
          <div className="feature-grid">
            <div className="feature-card">
              <h3>Каталог и корзина</h3>
              <p>Управление товарами, категориями и заказами через админку и API.</p>
            </div>
            <div className="feature-card">
              <h3>Поиск Algolia</h3>
              <p>Мгновенная выдача, фильтры по категориям, ранжирование и подсветка.</p>
            </div>
            <div className="feature-card">
              <h3>Next.js витрина</h3>
              <p>Современная фронтенд-архитектура c SSR и готовностью к статической генерации.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="section-header">
            <h2>Популярные товары</h2>
            <p>Список подгружается напрямую из Django API. Настройте выдачу под ваши бизнес-метрики.</p>
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
