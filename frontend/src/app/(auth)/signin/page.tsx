"use client";

import { signIn } from "next-auth/react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState, useTransition } from "react";

export default function SignInPage() {
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const router = useRouter();

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const identifier = String(formData.get("identifier") || "");
    const password = String(formData.get("password") || "");
    if (!identifier || !password) {
      setError("Введите логин и пароль.");
      return;
    }

    startTransition(async () => {
      const result = await signIn("credentials", {
        identifier,
        password,
        redirect: false,
      });

      if (result?.error) {
        setError("Не удалось войти. Проверьте данные.");
        return;
      }
      setError(null);
      router.push("/account");
    });
  };

  return (
    <section className="section">
      <div className="container auth-card">
        <h1>Вход в аккаунт</h1>
        <p className="auth-subtitle">Используйте email или логин и пароль, указанные при регистрации.</p>
        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="auth-field">
            <span>Логин или email</span>
            <input name="identifier" type="text" placeholder="user@example.com" required minLength={2} />
          </label>
          <label className="auth-field">
            <span>Пароль</span>
            <input name="password" type="password" placeholder="••••••••" required minLength={6} />
          </label>
          {error && <p className="auth-error">{error}</p>}
          <button className="btn btn-primary auth-submit" type="submit" disabled={isPending}>
            {isPending ? "Входим..." : "Войти"}
          </button>
        </form>
        <p className="auth-hint">
          Нет аккаунта? <Link href="/signup">Зарегистрируйтесь</Link>
        </p>
        <p className="auth-hint">
          <Link href="/forgot-password">Забыли пароль?</Link>
        </p>
      </div>
    </section>
  );
}
