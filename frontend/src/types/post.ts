export type PostSummary = {
  id: number;
  slug: string;
  title: string;
  summary: string;
  meta_title: string;
  meta_description: string;
  published_at?: string;
  tags: string[];
};

export type PostDetail = PostSummary & {
  body: string;
  meta_keywords: string;
  og_image?: string;
  created_at?: string;
  updated_at?: string;
};

