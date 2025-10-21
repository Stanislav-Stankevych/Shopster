"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useSession } from "next-auth/react";

import type { ProductReview } from "@/types/product";
import {
  createProductReview,
  deleteProductReview,
  fetchProductReviews,
  updateProductReview,
} from "@/lib/reviewApi";

type ProductReviewsProps = {
  productId: number;
  productSlug: string;
  averageRating: number | null;
  reviewsCount: number;
  canReview: boolean;
  userReview: ProductReview | null;
};

type ReviewFormState = {
  rating: number;
  title: string;
  body: string;
};

const initialFormState: ReviewFormState = {
  rating: 5,
  title: "",
  body: "",
};

function formatDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleDateString("ru-RU", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function moderationLabel(status: ProductReview["moderation_status"]): string {
  switch (status) {
    case "approved":
      return "Одобрен";
    case "pending":
      return "На модерации";
    case "rejected":
      return "Отклонён";
    default:
      return status;
  }
}

export function ProductReviews({
  productId,
  productSlug,
  averageRating,
  reviewsCount,
  canReview,
  userReview,
}: ProductReviewsProps) {
  const { status: sessionStatus } = useSession();
  const [isAuthenticated, setIsAuthenticated] = useState(sessionStatus === "authenticated");
  const [reviews, setReviews] = useState<ProductReview[]>([]);
  const [nextPage, setNextPage] = useState<number | null>(1);
  const [totalCount, setTotalCount] = useState<number>(reviewsCount);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [formVisible, setFormVisible] = useState(canReview);
  const [editingReview, setEditingReview] = useState<ProductReview | null>(null);
  const [form, setForm] = useState<ReviewFormState>(() => {
    if (userReview) {
      return {
        rating: userReview.rating,
        title: userReview.title ?? "",
        body: userReview.body ?? "",
      };
    }
    return { ...initialFormState };
  });

  useEffect(() => {
    setIsAuthenticated(sessionStatus === "authenticated");
  }, [sessionStatus]);

  const hasMore = nextPage !== null;

  const loadReviews = useCallback(
    async (page: number) => {
      setLoading(true);
      setError(null);
      try {
        const { reviews: fetched, nextPage: next, totalCount: count } = await fetchProductReviews(productSlug, page);
        setReviews((prev) => {
          if (page === 1) {
            return fetched;
          }
          const existingIds = new Set(prev.map((review) => review.id));
          const merged = [...prev];
          fetched.forEach((review) => {
            if (!existingIds.has(review.id)) {
              merged.push(review);
            }
          });
          return merged;
        });
        setNextPage(next);
        setTotalCount(count);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Не удалось загрузить отзывы.");
      } finally {
        setLoading(false);
      }
    },
    [productSlug]
  );

  useEffect(() => {
    loadReviews(1).catch(() => undefined);
  }, [loadReviews]);

  const canSubmitReview = useMemo(() => canReview && isAuthenticated, [canReview, isAuthenticated]);

  const resetForm = () => {
    setFormVisible(false);
    setEditingReview(null);
    setForm({ ...initialFormState });
  };

  const handleCreateOrUpdate = async () => {
    setSubmitting(true);
    setError(null);
    try {
      if (editingReview) {
        const updated = await updateProductReview(editingReview.id, {
          rating: form.rating,
          title: form.title,
          body: form.body,
        });
        setReviews((prev) => prev.map((review) => (review.id === updated.id ? updated : review)));
        resetForm();
      } else {
        const created = await createProductReview({
          product_id: productId,
          rating: form.rating,
          title: form.title,
          body: form.body,
        });
        setReviews((prev) => [created, ...prev.filter((review) => review.id !== created.id)]);
        setNextPage(nextPage ?? null);
        setFormVisible(false);
        setForm({ ...initialFormState });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось сохранить отзыв.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = (review: ProductReview) => {
    setEditingReview(review);
    setForm({
      rating: review.rating,
      title: review.title ?? "",
      body: review.body ?? "",
    });
    setFormVisible(true);
  };

  const handleDelete = async (reviewId: number) => {
    if (!confirm("Удалить отзыв?")) {
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await deleteProductReview(reviewId);
      setReviews((prev) => prev.filter((review) => review.id !== reviewId));
      setFormVisible(false);
      setEditingReview(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось удалить отзыв.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleLoadMore = () => {
    if (nextPage && !loading) {
      loadReviews(nextPage).catch(() => undefined);
    }
  };

  const derivedAverage = averageRating ?? null;
  const approvedCount = reviewsCount;

  return (
    <section className="product-reviews">
      <header className="product-reviews__header">
        <h2>Отзывы</h2>
        <p className="product-reviews__summary">
          {approvedCount > 0
            ? `Средняя оценка ${derivedAverage?.toFixed(1) ?? "—"} ★ · Одобренных отзывов: ${approvedCount}`
            : "Пока нет одобренных отзывов"}
        </p>
      </header>

      {error && <p className="product-reviews__error">{error}</p>}

      {canSubmitReview && !formVisible && (
        <button className="btn btn-primary" onClick={() => setFormVisible(true)}>
          Написать отзыв
        </button>
      )}

      {!isAuthenticated && (
        <p className="product-reviews__hint">
          <Link href="/api/auth/signin" className="link">
            Войдите
          </Link>{" "}
          или зарегистрируйтесь, чтобы оставить отзыв.
        </p>
      )}

      {formVisible && (
        <div className="product-reviews__form">
          <h3>{editingReview ? "Изменить отзыв" : "Новый отзыв"}</h3>
          <div className="form-grid">
            <label>
              <span>Оценка</span>
              <select
                value={form.rating}
                onChange={(event) => setForm((prev) => ({ ...prev, rating: Number(event.target.value) }))}
                disabled={submitting}
              >
                {[5, 4, 3, 2, 1].map((value) => (
                  <option key={value} value={value}>
                    {value} ★
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span>Заголовок</span>
              <input
                type="text"
                value={form.title}
                onChange={(event) => setForm((prev) => ({ ...prev, title: event.target.value }))}
                placeholder="Коротко о впечатлении"
                disabled={submitting}
                maxLength={120}
              />
            </label>
            <label className="form-grid__full">
              <span>Отзыв</span>
              <textarea
                value={form.body}
                onChange={(event) => setForm((prev) => ({ ...prev, body: event.target.value }))}
                rows={4}
                placeholder="Поделитесь опытом покупки и использования"
                disabled={submitting}
              />
            </label>
          </div>
          <div className="product-reviews__form-actions">
            <button className="btn btn-primary" onClick={handleCreateOrUpdate} disabled={submitting || !form.body.trim()}>
              {submitting ? "Сохраняем..." : "Отправить"}
            </button>
            <button className="btn btn-secondary" type="button" onClick={resetForm} disabled={submitting}>
              Отмена
            </button>
          </div>
          <p className="product-reviews__note">
            Отправленный отзыв попадёт на модерацию. О публикации мы сообщим письмом.
          </p>
        </div>
      )}

      <ul className="product-review-list">
        {reviews.map((review) => (
          <li key={review.id} className="product-review-card">
            <div className="product-review-card__header">
              <strong>{review.user.name}</strong>
              <span className="product-review-card__rating">{`${review.rating} ★`}</span>
            </div>
            <div className="product-review-card__meta">
              <span>{formatDate(review.created_at)}</span>
              {review.verified_purchase && <span className="tag">Проверенная покупка</span>}
              <span className={`tag tag--${review.moderation_status}`}>{moderationLabel(review.moderation_status)}</span>
            </div>
            {review.title && <h4 className="product-review-card__title">{review.title}</h4>}
            <p className="product-review-card__body">{review.body}</p>
            {review.is_owner && (
              <div className="product-review-card__actions">
                <button className="btn btn-secondary" onClick={() => handleEdit(review)} disabled={submitting}>
                  Редактировать
                </button>
                <button className="btn btn-outline" onClick={() => handleDelete(review.id)} disabled={submitting}>
                  Удалить
                </button>
              </div>
            )}
          </li>
        ))}
      </ul>

      {hasMore && (
        <button className="btn btn-secondary" onClick={handleLoadMore} disabled={loading}>
          {loading ? "Загружаем..." : "Показать ещё"}
        </button>
      )}

      {!loading && reviews.length === 0 && (
        <p className="product-reviews__empty">Будьте первым, кто поделится впечатлением о товаре.</p>
      )}
    </section>
  );
}
