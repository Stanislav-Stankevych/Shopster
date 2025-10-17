import { ProductsInfiniteList } from "@/components/ProductsInfiniteList";
import { fetchProductsPage } from "@/lib/api";

const PAGE_SIZE = 12;

export default async function ProductsPage() {
  const initialPage = await fetchProductsPage({ pageSize: PAGE_SIZE });

  return (
    <section className="section">
      <div className="container">
        <div className="section-header">
          <h1>Catalog</h1>
          <p>Products are synced from Django. Use search and filters to navigate quickly.</p>
        </div>
        <ProductsInfiniteList
          initialItems={initialPage.items}
          initialNextPage={initialPage.nextPage}
          pageSize={PAGE_SIZE}
          totalCount={initialPage.totalCount}
        />
      </div>
    </section>
  );
}
