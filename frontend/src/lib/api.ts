import "server-only";
import { Product } from "@/types/product";

const API_BASE =
  process.env.INTERNAL_API_BASE_URL ??
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://localhost:8000";

export async function fetchProducts(limit = 6): Promise<Product[]> {
  const url = new URL("/api/products/", API_BASE);
  if (limit) {
    url.searchParams.set("page_size", String(limit));
  }

  const response = await fetch(url.toString(), {
    headers: {
      Accept: "application/json"
    },
    next: { revalidate: 60 }
  });

  if (!response.ok) {
    console.error("Failed to fetch products", response.statusText);
    return [];
  }

  const data = await response.json();
  return data.results ?? data;
}

export async function fetchProduct(slug: string): Promise<Product | null> {
  const url = new URL(`/api/products/${slug}/`, API_BASE);
  const response = await fetch(url.toString(), {
    headers: { Accept: "application/json" },
    next: { revalidate: 60 }
  });
  if (!response.ok) {
    return null;
  }
  return response.json();
}
