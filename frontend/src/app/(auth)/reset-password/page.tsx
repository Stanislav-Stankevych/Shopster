"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, useState, useTransition } from "react";

import { API_BASE_URL } from "@/lib/config";

export default function ResetPasswordPage() {
  const searchParams = useSearchParams();
  const uid = searchParams.get("uid") ?? "";
  const token = searchParams.get("token") ?? "";
  const router = useRouter();

  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const [completed, setCompleted] = useState(false);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const password = String(formData.get("password") || "");
    const passwordConfirm = String(formData.get("password_confirm") || "");

    if (!uid || !token) {
      setError("Недействительная ссылка для сброса.");
      return;
    }

    if (!password || password.length < 6) {
      setError("Пароль должен содержать не менее 6 символов.");
      return;
    }

    if (password !== passwordConfirm) {
      setError("Пароли не совпадают.");
      return;
    }

    startTransition(async () => {
      setError(null);
      try {
        const response = await fetch(`${API_BASE_URL}/api/auth/password/reset/confirm/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ uid, token, password, password_confirm: passwordConfirm }),
        });
        if (!response.ok) {
          const data = await response.json().catch(() => ({}));
          const message =
            typeof data === "object" && data !== null
              ? Object.values(data as Record<string, string[]>).flat().join(" ")
              : "Не удалось изменить пароль.";
          throw new Error(message || "Не удалось изменить пароль.");
        }
        setCompleted(true);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Не удалось изменить пароль.");
      }
    });
  };

  if (!uid || !token) {
    return (
      <section className="section">
        <div className="container auth-card">
          <h1>Ссылка недействительна</h1>
          <p className="auth-subtitle">Проверьте, что вы перешли по актуальной ссылке из письма.</p>
          <Link className="btn btn-primary auth-submit" href="/forgot-password">
            Запросить новую ссылку
          </Link>
        </div>
      </section>
    );
  }

  if (completed) {
    return (
      <section className="section">
        <div className="container auth-card">
          <h1>Пароль обновлён</h1>
          <p className="auth-subtitle">Теперь вы можете войти, используя новый пароль.</p>
          <button className="btn btn-primary auth-submit" onClick={() => router.push("/signin")}>
            Перейти ко входу
          </button>
        </div>
      </section>
    );
  }

  return (
    <section className="section">
      <div className="container auth-card">
        <h1>Сброс пароля</h1>
        <p className="auth-subtitle">Введите новый пароль для вашего аккаунта.</p>
        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="auth-field">
            <span>Новый пароль</span>
            <input name="password" type="password" placeholder="••••••••" required minLength={6} />
          </label>
          <label className="auth-field">
            <span>Повторите пароль</span>
            <input name="password_confirm" type="password" placeholder="••••••••" required minLength={6} />
          </label>
          {error && <p className="auth-error">{error}</p>}
          <button className="btn btn-primary auth-submit" type="submit" disabled={isPending}>
            {isPending ? "Сохраняем..." : "Изменить пароль"}
          </button>
        </form>
        <p className="auth-hint">
          Вспомнили пароль? <Link href="/signin">Войти</Link>
        </p>
      </div>
    </section>
  );
}
