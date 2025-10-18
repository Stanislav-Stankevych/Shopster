export type Product = {
  id: number;
  name: string;
  slug: string;
  sku: string;
  short_description: string;
  description: string;
  meta_title: string;
  meta_description: string;
  meta_keywords: string;
  price: string;
  currency: string;
  stock: number;
  category: {
    id: number;
    name: string;
    slug: string;
    description: string;
    meta_title: string;
    meta_description: string;
    is_active: boolean;
    created_at?: string;
    updated_at?: string;
  } | null;
  images: Array<{
    id: number;
    image: string;
    alt_text: string;
    is_main: boolean;
  }>;
  created_at?: string;
  updated_at?: string;
};

export type CategorySummary = {
  id: number;
  name: string;
  slug: string;
  meta_title?: string;
  meta_description?: string;
};
