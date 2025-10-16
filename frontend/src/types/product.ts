export type Product = {
  id: number;
  name: string;
  slug: string;
  sku: string;
  short_description: string;
  description: string;
  price: string;
  currency: string;
  stock: number;
  category: {
    id: number;
    name: string;
    slug: string;
    description: string;
    is_active: boolean;
  } | null;
  images: Array<{
    id: number;
    image: string;
    alt_text: string;
    is_main: boolean;
  }>;
};
