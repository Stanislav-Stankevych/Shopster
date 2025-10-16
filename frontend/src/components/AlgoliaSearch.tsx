"use client";

import Link from "next/link";
import { useMemo } from "react";
import {
  Configure,
  Hits,
  InstantSearch,
  RefinementList,
  SearchBox,
  useInstantSearch,
  useSearchBox
} from "react-instantsearch-hooks-web";
import type { Hit } from "instantsearch.js";

import { ALGOLIA_INDEX, getAlgoliaSearchClient } from "@/lib/algolia";

type SearchHit = Hit<{
  name: string;
  price: number;
  currency: string;
  short_description: string;
  category: string;
  image_url: string;
  slug: string;
}>;

const MIN_QUERY_LENGTH = 2;

function createSearchClient() {
  const baseClient = getAlgoliaSearchClient();
  if (!baseClient) {
    return null;
  }

  return {
    ...baseClient,
    search(requests: any[]) {
      const shouldThrottle = requests.every(({ params }) => {
        const query = params?.query ?? "";
        return !query || query.trim().length < MIN_QUERY_LENGTH;
      });

      if (shouldThrottle) {
        return Promise.resolve({
          results: requests.map(() => ({
            hits: [],
            nbHits: 0,
            page: 0,
            nbPages: 0,
            hitsPerPage: 12,
            exhaustiveNbHits: false,
            query: "",
            params: "",
            processingTimeMS: 0
          }))
        });
      }

      return baseClient.search(requests);
    }
  };
}

function HitCard({ hit }: { hit: SearchHit }) {
  const price = hit.price?.toLocaleString("ru-RU", { style: "currency", currency: hit.currency ?? "RUB" });
  const imageUrl =
    hit.image_url && !hit.image_url.startsWith("http")
      ? `${process.env.NEXT_PUBLIC_API_BASE_URL}${hit.image_url}`
      : hit.image_url;

  return (
    <Link href={`/products/${hit.slug}`} className="search-hit">
      {imageUrl ? <img className="search-hit__thumb" src={imageUrl} alt={hit.name} /> : <div className="search-hit__thumb placeholder">Нет фото</div>}
      <div className="search-hit__content">
        <span className="search-hit__price">{price}</span>
        <h3 className="search-hit__title">{hit.name}</h3>
        <p className="search-hit__description">{hit.short_description}</p>
        {hit.category && <span className="search-hit__category">{hit.category}</span>}
      </div>
    </Link>
  );
}

function SearchResults() {
  const { query } = useSearchBox();
  const { results, status } = useInstantSearch();
  const trimmedQuery = (query || "").trim();

  if (!trimmedQuery || trimmedQuery.length < MIN_QUERY_LENGTH) {
    return <p className="search-hint">Начните вводить запрос (минимум {MIN_QUERY_LENGTH} символа), чтобы увидеть результаты.</p>;
  }

  if (status === "loading") {
    return <p className="search-hint">Загружаем результаты…</p>;
  }

  if (!results || results.nbHits === 0) {
    return <p className="search-hint">По запросу ничего не найдено. Попробуйте изменить формулировку.</p>;
  }

  return <Hits hitComponent={HitCard} />;
}

export function AlgoliaSearch() {
  const searchClient = useMemo(() => createSearchClient(), []);

  if (!searchClient) {
    return <p>Поиск временно недоступен. Проверьте настройки Algolia.</p>;
  }

  return (
    <div className="search-panel">
      <InstantSearch searchClient={searchClient} indexName={ALGOLIA_INDEX}>
        <div className="search-panel__header">
          <SearchBox placeholder="Поиск по каталогу" autoFocus />
        </div>
        <div className="search-panel__body">
          <aside className="search-panel__filters">
            <h4 className="search-panel__subtitle">Категории</h4>
            <RefinementList attribute="category" />
          </aside>
          <section className="search-panel__results">
            <Configure hitsPerPage={12} />
            <SearchResults />
          </section>
        </div>
      </InstantSearch>
    </div>
  );
}
