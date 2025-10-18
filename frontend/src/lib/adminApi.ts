import "server-only";

import { API_BASE_URL } from "@/lib/config";

export type CurrencyBreakdown = {
  currency: string;
  total_sales: string;
  total_orders: number;
};

export type TopProduct = {
  product_id: number | null;
  product_name: string;
  total_quantity: number;
  total_sales: string;
};

export type StatsOverview = {
  total_orders: number;
  gross_revenue: string;
  currency_breakdown: CurrencyBreakdown[];
  top_products: TopProduct[];
};

type StatsParams = {
  dateFrom?: string;
  dateTo?: string;
};

export async function fetchStatsOverview(
  accessToken: string,
  params: StatsParams = {}
): Promise<StatsOverview> {
  const url = new URL("/api/stats/overview/", API_BASE_URL);
  if (params.dateFrom) {
    url.searchParams.set("date_from", params.dateFrom);
  }
  if (params.dateTo) {
    url.searchParams.set("date_to", params.dateTo);
  }

  const response = await fetch(url.toString(), {
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    cache: "no-store",
  });

  if (response.status === 401 || response.status === 403) {
    throw new Error("Unauthorized");
  }

  if (!response.ok) {
    const payload = await response.text();
    throw new Error(payload || "Failed to load statistics.");
  }

  return response.json() as Promise<StatsOverview>;
}
