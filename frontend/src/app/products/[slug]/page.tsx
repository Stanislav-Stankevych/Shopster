import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";

import { AddToCartButton } from "@/components/AddToCartButton";
import { fetchProduct } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

type Props = {
  params: Promise<{ slug: string }>;
};

export default async function ProductDetailPage({ params }: Props) {
  const { slug } = await params;
  const product = await fetchProduct(slug);

  if (!product) {
    notFound();
  }

  const mainImage = product.images.find((img) => img.is_main) ?? product.images[0];

  return (
    <section className="section">
      <div className="container hero-grid">
        <div className="hero-card">
          <Link href="/products" className="btn btn-outline" style={{ marginBottom: "1.5rem", width: "fit-content" }}>
            ← Back to catalog
          </Link>
          <h1>{product.name}</h1>
          <p className="lead">{product.description || product.short_description}</p>
          <div className="cta-buttons">
            <span className="btn price-badge">{formatCurrency(product.currency ?? "RUB", Number(product.price))}</span>
            <AddToCartButton productId={product.id} />
            <span className="btn btn-outline">In stock: {product.stock}</span>
          </div>
          <p>SKU: {product.sku}</p>
          {product.category && <p>Category: {product.category.name}</p>}
        </div>
        <div className="hero-card" style={{ padding: 0, overflow: "hidden" }}>
          {mainImage ? (
            <Image
              src={new URL(mainImage.image, process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000").toString()}
              alt={mainImage.alt_text || product.name}
              width={960}
              height={640}
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
          ) : (
            <div className="product-image" />
          )}
        </div>
      </div>
    </section>
  );
}

