"use client";

import Link from "next/link";
import { useSession } from "next-auth/react";

export function AdminNavLink() {
  const { data: session } = useSession();

  if (!session?.user?.is_staff) {
    return null;
  }

  return (
    <>
      <Link href="/admin/stats">Admin dashboard</Link>
      <a href="http://localhost:3000admin/" target="_blank" rel="noreferrer noopener">
        Django admin
      </a>
    </>
  );
}
