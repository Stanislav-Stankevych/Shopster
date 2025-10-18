import "server-only";

import { Product, CategorySummary } from "@/types/product";

const API_BASE =
  process.env.INTERNAL_API_BASE_URL ??
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://localhost:8000";

type FetchProductsPageOptions = {
  page?: number;
  pageSize?: number;
  query?: Record<string, string | undefined>;
};

export type PaginatedProducts = {
  items: Product[];
  nextPage: number | null;
  previousPage: number | null;
  totalCount: number;
};

function parsePageNumber(value: unknown): number | null {
  if (!value || typeof value !== "string") {
    return null;
  }
  try {
    const pageParam = new URL(value, API_BASE).searchParams.get("page");
    return pageParam ? Number(pageParam) : null;
  } catch {
    return null;
  }
}

export async function fetchProductsPage(options: FetchProductsPageOptions = {}): Promise<PaginatedProducts> {
  const page = options.page ?? 1;
  const pageSize = options.pageSize ?? 12;

  const url = new URL("/api/products/", API_BASE);
  url.searchParams.set("page", String(page));
  url.searchParams.set("page_size", String(pageSize));
  if (options.query) {
    for (const [key, value] of Object.entries(options.query)) {
      if (value !== undefined && value !== "") {
        url.searchParams.set(key, value);
      }
    }
  }

  const response = await fetch(url.toString(), {
    headers: { Accept: "application/json" },
    next: { revalidate: 60 }
  });

  if (!response.ok) {
    console.error("Failed to fetch products page", response.status, response.statusText);
    return { items: [], nextPage: null, previousPage: null, totalCount: 0 };
  }

  const data = await response.json();
  const items: Product[] = Array.isArray(data.results) ? data.results : data;

  return {
    items,
    nextPage: parsePageNumber(data.next),
    previousPage: parsePageNumber(data.previous),
    totalCount: typeof data.count === "number" ? data.count : items.length
  };
}

export async function fetchProducts(limit = 6): Promise<Product[]> {
  const page = await fetchProductsPage({ pageSize: limit });
  return page.items;
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

export async function fetchCategories(): Promise<CategorySummary[]> {
  const url = new URL("/api/categories/", API_BASE);
  url.searchParams.set("page_size", "100");

  const response = await fetch(url.toString(), {
    headers: { Accept: "application/json" },
    next: { revalidate: 300 }
  });

  if (!response.ok) {
    console.error("Failed to fetch categories", response.status, response.statusText);
    return [];
  }

  const data = await response.json();
  const categories: CategorySummary[] = Array.isArray(data.results) ? data.results : data;
  return categories.filter((category) => Boolean(category?.slug));
}



