"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState, useTransition } from "react";

import { API_BASE_URL } from "@/lib/config";

export default function ForgotPasswordPage() {
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const router = useRouter();

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const email = String(formData.get("email") || "");
    if (!email) {
      setError("Введите email.");
      return;
    }

    startTransition(async () => {
      setError(null);
      try {
        const response = await fetch(`${API_BASE_URL}/api/auth/password/reset/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email }),
        });
        if (!response.ok) {
          throw new Error("Не удалось отправить письмо. Попробуйте позже.");
        }
        setSubmitted(true);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Не удалось отправить письмо.");
      }
    });
  };

  if (submitted) {
    return (
      <section className="section">
        <div className="container auth-card">
          <h1>Проверьте почту</h1>
          <p className="auth-subtitle">
            Если адрес зарегистрирован, мы отправили инструкцию по восстановлению пароля. Проверьте входящие или папку
            «Спам».
          </p>
          <button className="btn btn-primary auth-submit" onClick={() => router.push("/signin")}>
            Вернуться ко входу
          </button>
        </div>
      </section>
    );
  }

  return (
    <section className="section">
      <div className="container auth-card">
        <h1>Забыли пароль?</h1>
        <p className="auth-subtitle">
          Укажите email, который вы использовали при регистрации. Мы отправим ссылку для восстановления пароля.
        </p>
        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="auth-field">
            <span>Email</span>
            <input name="email" type="email" placeholder="user@example.com" required />
          </label>
          {error && <p className="auth-error">{error}</p>}
          <button className="btn btn-primary auth-submit" type="submit" disabled={isPending}>
            {isPending ? "Отправляем..." : "Отправить ссылку"}
          </button>
        </form>
        <p className="auth-hint">
          <Link href="/signin">Вернуться ко входу</Link>
        </p>
      </div>
    </section>
  );
}
